from django.conf.urls import include, url
from webfront import views

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
    url(r'^clans/$', 'webfront.views.clans_page', name='clans_list'),
    url(r'^clans/([a-zA-Z0-9_]+)/$', 'webfront.views.clan_page', name='view_clan'),
]
