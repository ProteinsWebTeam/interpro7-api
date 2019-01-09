from django.conf.urls import url
from webfront.views import common

urlpatterns = [url(r"^api/(?P<url>.*)$", common.GeneralHandler.as_view())]
