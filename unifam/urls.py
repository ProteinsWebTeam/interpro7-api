from django.conf.urls import include, url, patterns
# from django.conf import settings
from webfront.views import interpro, common, member_databases
# from rest_framework import routers
# from rest_framework_nested import routers

# router = routers.DefaultRouter()
# router = routers.SimpleRouter()
#
# router.register(r'entry', pfam.home_page, base_name='entry')
#
# entries_router = routers.NestedSimpleRouter(router, r'', lookup='interpro')
#
# interpro_router = routers.NestedSimpleRouter(entries_router, r'', lookup='iFilter')


# router.register(r'clans', pfam.ClanViewSet, base_name="api_clans")
# router.register(r'pfama', pfam.PFamAViewSet)
# router.register(r'clan_membership', pfam.MembershipViewSet)
# router.register(r'clan_relationships', pfam.PFamA2PFamAViewSet)
#
# base_urlpatterns = [
#     url(r'^$', pfam.home_page, name='home'),
#     url(r'^clans/$', pfam.clans_page, name='clans_list'),
#     url(r'^clans/([a-zA-Z0-9_\-]+)/$', pfam.clan_page, name='view_clan'),
#
#     url(r'^api/', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
#
# # This is done to be able to use both the root path and the "skeleton" prefix
# urlpatterns = [
#     url('^', include(base_urlpatterns)), # if you wish to maintain the un-prefixed URL's too
#     url('^skeleton/', include(base_urlpatterns)),
# ]

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
    url(r'^(?P<url>.*)$', common.GeneralHandler.as_view()),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls))
#     )
