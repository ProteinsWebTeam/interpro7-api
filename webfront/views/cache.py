from django.core.cache import cache
from django.shortcuts import render
from rest_framework import status
from webfront.response import Response

class InterProCache:
    def set(self, key, response):
        if response.status_code == status.HTTP_200_OK:
            value = {
                'data': {
                    'metadata': response.data['metadata']
                },
                'status': response.status_code,
                'template_name': response.template_name,
                'exception': response.exception,
                'content_type': response.content_type
            }
            cache.set(key, value)

    def get(self, key):
        value = cache.get(key)
        if (value != None):
            value = Response(
                value.get('data'),
                value.get('status', 200),
                value.get('template_name'),
                {},
                value.get('exception', False),
                value.get('content_type')
            )
        return value
