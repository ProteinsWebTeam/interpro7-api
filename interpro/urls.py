from django.urls import re_path
from webfront.views import common, mail

urlpatterns = [
    re_path(r"^api/mail/$", mail.send_email),
    re_path(r"^api/(?P<url>.*)$", common.GeneralHandler.as_view()),
]
