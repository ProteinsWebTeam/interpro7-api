from rest_framework.response import Response as R
from django.conf import settings

# from webfront.models import Database
#
#
# interpro_version = Database.objects.get(pk="INTERPRO").version
interpro_version = "65.0"


class Response(R):
    def __init__(self, data=None, status=None, template_name=None, headers={},
                 exception=False, content_type=None):

        if settings.DEBUG:
            from django.db import connection
            from webfront.searcher.elastic_controller import es_results

            timings = [
                # 'cpu;desc="CPU";dur=1',
                'mysql;desc="MySQL";dur={:0.2f}'.format(
                    sum((float(query['time']) for query in connection.queries)) * 1000
                ),
                # 'filesystem;desc="Filesystem";dur=0',
                'es;desc="Elasticsearch";dur={:0.2f}'.format(
                    sum(query['took'] for query in es_results)
                ),
                # 'django;desc=Django;dur={:0.2f}'.format(
                #     (datetime.now().timestamp() - django_time['time']) * 1000
                # )
            ]

            headers["Server-Timing"] = ','.join(timings)
        headers["InterPro-Version"] = interpro_version

        super(Response, self).__init__(
            data, status, template_name, headers, exception, content_type,
        )
