from django.conf.urls import url
from webfront.views import common

urlpatterns = [
    # *build_common_urls(),
    # url(r'^/?$', 'webfront.views.member_databases.pfam.home_page',
    #     name='home'),
    # url(r'^entry/?$', 'webfront.views.member_databases.pfam.entries_page',
    #     name='entries_page'),
    # url(r'^entry/interpro/?$', 'webfront.views.member_databases.pfam.interpro_page',
    #     name='interpro_page'),
    # url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/?$', 'webfront.views.member_databases.pfam.interpro_filter_page',
    #     name='interpro_filter_page'),
    # url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$',
    #     'webfront.views.member_databases.pfam.interpro_member_page',
    #     name='interpro_member_page'),
    # url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$',
    #     'webfront.views.member_databases.pfam.interpro_member_filter_page',
    #     name='interpro_member_filter_page'),
    # url(r'^entry/interpro/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/?$',
    #     'webfront.views.member_databases.pfam.interpro_member_filter_acc_page',
    #     name='interpro_member_filter_acc_page'),
    url(r'^api/(?P<url>.*)$', common.GeneralHandler.as_view()),
]
