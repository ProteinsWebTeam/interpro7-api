from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from django.http import JsonResponse
from interpro.settings import INTERPRO_CONFIG
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.conf import settings


@csrf_exempt
def send_email(request):
    ip_address = get_client_ip(request)
    now = datetime.now()
    if not hasattr(settings, "credentials"):
        return store_credentials_and_mail(request, ip_address, now)
    else:
        last_accessed = settings.credentials
        if last_accessed["ip"] == ip_address:
            then = datetime.strptime(last_accessed["time"], "%Y-%m-%d %H:%M:%S.%f")
            time_diff = now - then
            elapsed_min = time_diff / timedelta(minutes=1)
            if elapsed_min >= 1:
                return store_credentials_and_mail(request, ip_address, now)
            else:
                data = {"error": "Request Aborted"}
                return JsonResponse(data, status=429)
        else:
            return store_credentials_and_mail(request, ip_address, now)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def store_credentials_and_mail(request, ip, time):
    settings.credentials = {"ip": ip, "time": time.strftime("%Y-%m-%d %H:%M:%S.%f")}
    return mail(request)


def mail(request):
    path = request.POST.get("path", INTERPRO_CONFIG.get("sendmail_path"))
    subject = request.POST.get("subject", "")
    message = request.POST.get("message", "")
    from_email = request.POST.get("from_email", "")
    queue = request.POST.get("queue", "interpro").lower()
    to_email = {"interpro": "interhelp@ebi.ac.uk", "pfam": "pfam-help@ebi.ac.uk"}.get(
        queue, ""
    )
    if path and subject and message and from_email and to_email:
        message = MIMEText(message)
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        p = Popen([path, "-t", "-oi"], stdin=PIPE)
        p.communicate(message.as_bytes())
        data = {"from": from_email, "subject": subject}
        return JsonResponse(data)
    else:
        data = {"error": "Make sure all fields are entered and valid"}
        return JsonResponse(data, status=400)
