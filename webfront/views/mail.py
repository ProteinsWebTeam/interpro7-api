from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from django.http import HttpResponse


def mail_interhelp(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    if subject and message and from_email:
        message = MIMEText(message)
        message['From'] = from_email
        message['To'] = 'interhelp@ebi.ac.uk'
        message['Subject'] = subject
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(message.as_bytes())
        return HttpResponse('Thanks for your feedback')
    else:
        return HttpResponse('Make sure all fields are entered and valid')
