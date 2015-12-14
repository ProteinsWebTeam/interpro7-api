from django.conf.urls import include, url, patterns
# from django.conf import settings
# <<<<<<< HEAD
from webfront import views
from rest_framework import routers
#
router = routers.DefaultRouter()
router.register(r'clans', views.ClanViewSet, base_name="api_clans")
router.register(r'pfama', views.PFamAViewSet)
router.register(r'clan_membership', views.MembershipViewSet)
router.register(r'clan_relationships', views.PFamA2PFamAViewSet)
#
# base_urlpatterns = [
#     url(r'^$', views.home_page, name='home'),
#     # url(r'^clans/$', 'webfront.views.clans_page', name='clans_list'),
#     # url(r'^clans/([a-zA-Z0-9_\-]+)/$', 'webfront.views.clan_page', name='view_clan'),
#
#     url(r'^api/', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#
#     # First attempt to the REST schema
#     url(r'^entry/$', 'webfront.views.entries_page', name='entries_page'),
#     url(r'^entry/interpro/$', 'webfront.views.interpro_page', name='interpro_page'),
#     url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_filter_page', name='interpro_filter_page'),
#     url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_page', name='interpro_member_page'),
#     url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_page', name='interpro_member_filter_page'),
#     url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_acc_page', name='interpro_member_filter_acc_page'),
# #    url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/$', 'webfront.views.interpro_member_filter_acc_option_page', name='interpro_member_filter_acc_option_page'),
#
# =======
from webfront.views import interpro, common
from webfront.views.member_databases import pfam

paths = [
    ['entry'],# section
    ['all', 'interpro'],# interpro
    ['all', 'unintegrated', r'IPR\d{6}'],# i_filter
    ['pfam'],# db_member
]
n_additional_levels = 3
for _ in range(n_additional_levels):
    # paths.append([r'[^/]+'])
    pass


def construct_url(base, i=True, appendSlash=True, format=True, **kwargs):
    return r'{casing}^{formatted_base}{slash}$'.format(
        casing=('(?i)' if i else ''),
        formatted_base=base.format(**kwargs) if format else base,
        slash=('/' if appendSlash else ''),
    )


def or_group(array):
    return '|'.join(array)


def build_common_urls():
    base = ''
    yield url(construct_url(base, format=False), common.Handler.as_view())

    intermediary = []

    for level in paths:
        intermediary.append(or_group(level))
        path = '/'.join(map(
            lambda g: '({})'.format(g),
            intermediary,
        ))
        yield url(construct_url(path, format=False), common.Handler.as_view())

    yield url(construct_url(path+r'(.+)', format=False), common.Handler.as_view())

urlpatterns = [
    # *build_common_urls(),
    url(r'^web/?$', 'webfront.views.member_databases.pfam.home_page', name='home'),
    url(r'^web/entry/?$', 'webfront.views.member_databases.pfam.entries_page', name='entries_page'),
    url(r'^web/entry/interpro/?$', 'webfront.views.member_databases.pfam.interpro_page', name='interpro_page'),
    url(r'^web/entry/interpro/([a-zA-Z0-9_\-]+)/?$', 'webfront.views.member_databases.pfam.interpro_filter_page', name='interpro_filter_page'),
    url(r'^web/entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$', 'webfront.views.member_databases.pfam.interpro_member_page', name='interpro_member_page'),
    url(r'^web/entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$', 'webfront.views.member_databases.pfam.interpro_member_filter_page', name='interpro_member_filter_page'),
    url(r'^web/entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$', 'webfront.views.member_databases.pfam.interpro_member_filter_acc_page', name='interpro_member_filter_acc_page'),
    url(r'^api/', include(router.urls)),
    url(r'^(?P<url>.*)$', common.GeneralHandler.as_view()),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls))
#     )
