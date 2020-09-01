from django import template
from django.utils.html import escape
from django.utils.encoding import iri_to_uri
from rest_framework.utils.urls import replace_query_param

from django.conf import settings

register = template.Library()

@register.simple_tag
def get_url_with_prefix(request, key, val):
    iri = request.get_full_path()
    uri = iri_to_uri(iri)
    return settings.INTERPRO_CONFIG["url_path_prefix"] + escape(replace_query_param(uri, key, val))
