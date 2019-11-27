from django.conf.urls import url
from webfront.views import common, mail

urlpatterns = [
    url(r"^api/(?P<url>.*)$", common.GeneralHandler.as_view()),
    url(r"^mail/$", mail.mail_interhelp)
]
