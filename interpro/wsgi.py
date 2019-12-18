"""
WSGI config for interpro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    import pymysql

    pymysql.version_info = (1, 4, 6, "final", 0)  # change mysqlclient version
    pymysql.install_as_MySQLdb()
    print("running pymysql")
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interpro.settings")

application = get_wsgi_application()
