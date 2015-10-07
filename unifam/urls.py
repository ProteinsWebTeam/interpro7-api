from django.conf.urls import include, url
from webfront import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'clans', views.ClanViewSet)
router.register(r'pfama', views.PFamAViewSet)
router.register(r'clan_membership', views.MembershipViewSet)
router.register(r'clan_relationships', views.PFamA2PFamAViewSet)

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
    url(r'^clans/$', 'webfront.views.clans_page', name='clans_list'),
    url(r'^clans/([a-zA-Z0-9_\-]+)/$', 'webfront.views.clan_page', name='view_clan'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
