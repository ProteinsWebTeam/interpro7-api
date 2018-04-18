from django.core.cache import cache
from django.shortcuts import render
from rest_framework import status
from webfront.response import Response
from django.conf import settings

class InterProCache:
    def set(self, key, response):
        try:
            key = key.replace("//", "/")
            if settings.INTERPRO_CONFIG.get('enable_caching', False)\
                and settings.INTERPRO_CONFIG.get('enable_cache_write', False):
                if response.status_code == status.HTTP_200_OK :
                    #print("Caching {}".format(key))
                    value = {
                        'data': {x: response.data[x] for x in response.data},
                        'status': response.status_code,
                        'template_name': response.template_name,
                        'exception': response.exception,
                        'content_type': response.content_type,
                        'headers': {
                            'content-type': response.get('content-type', ""),
                            'interpro-version': response.get('interpro-version', ""),
                            'Original-Server-Timing': response.get('server-timing', ""),
                            'Cached': 'true'
                        }
                    }
                    cache.set(key, value)
                    cache.persist(key)
        except:
            pass

    def get(self, key):
        key = key.replace("//", "/")
        if settings.INTERPRO_CONFIG.get('enable_caching', False):
            value = cache.get(key)
            if (value != None):
                #print("Found {}".format(key))
                value = Response(
                    value.get('data'),
                    value.get('status', 200),
                    value.get('template_name'),
                    value.get('headers', {}),
                    value.get('exception', False),
                    value.get('content_type')
                )
            return value
