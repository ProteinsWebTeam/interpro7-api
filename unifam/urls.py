from django.conf.urls import include, url
# from django.conf import settings
from webfront import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'clans', views.ClanViewSet, base_name="api_clans")
router.register(r'pfama', views.PFamAViewSet)
router.register(r'clan_membership', views.MembershipViewSet)
router.register(r'clan_relationships', views.PFamA2PFamAViewSet)

base_urlpatterns = [
    url(r'^$', views.home_page, name='home'),
    # url(r'^clans/$', 'webfront.views.clans_page', name='clans_list'),
    # url(r'^clans/([a-zA-Z0-9_\-]+)/$', 'webfront.views.clan_page', name='view_clan'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # First attempt to the REST schema
    url(r'^entry/$', 'webfront.views.entries_page', name='entries_page'),
    url(r'^entry/interpro/$', 'webfront.views.interpro_page', name='interpro_page'),
    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_filter_page', name='interpro_filter_page'),
    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_page', name='interpro_member_page'),
    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_page', name='interpro_member_filter_page'),
    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_acc_page', name='interpro_member_filter_acc_page'),
#    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_acc_option_page', name='interpro_member_filter_acc_option_page'),

]

# This is done to be able to use both the root path and the "skeleton" prefix
urlpatterns = [
    url('^', include(base_urlpatterns)), # iff you wish to maintain the un-prefixed URL's too
    url('^skeleton/', include(base_urlpatterns)),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls))
#     )
