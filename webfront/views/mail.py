from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from django.http import JsonResponse
from interpro.settings import INTERPRO_CONFIG


def mail_interhelp(request):
    path = request.POST.get('path', INTERPRO_CONFIG.get("sendmail_path"))
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    if path and subject and message and from_email:
        message = MIMEText(message)
        message['From'] = from_email
        message['To'] = 'interhelp@ebi.ac.uk'
        message['Subject'] = subject
        p = Popen([path, "-t", "-oi"], stdin=PIPE)
        p.communicate(message.as_bytes())
        data = {
            'from': from_email,
            'subject': subject,
        }
        return JsonResponse(data)
    else:
        data = {
            'error': 'Make sure all fields are entered and valid',
        }
        return JsonResponse(data)
