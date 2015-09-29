from django.conf.urls import include, url
from webfront import views

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
]
