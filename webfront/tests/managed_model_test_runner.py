import os
import re
import sys
from django.test.runner import DiscoverRunner
from django.conf import settings


class UnManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run.
    Many thanks to the Caktus Group: http://bit.ly/1N8TcHW
    """

    def __init__(self, *args, **kwargs):
        settings.IN_TEST_MODE = True
        self.unmanaged_models = []
        super(UnManagedModelTestRunner, self).__init__(*args, **kwargs)

    def setup_test_environment(self, *args, **kwargs):
        from django.apps import apps
        myapp = apps.get_app_config('webfront')
        self.unmanaged_models = [m for m in myapp.models.values() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
            m._meta.db_table = re.sub(r'^"([^"]+)"\."([^"]+)"$', r'\1_\2', m._meta.db_table)

        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False

if 'interpro_ro' in settings.DATABASES and ('test' in sys.argv or 'test_coverage' in sys.argv):  # Covers regular testing and django-coverage
    settings.DATABASES['interpro_ro']['ENGINE'] = 'django.db.backends.sqlite3'
    settings.DATABASES['interpro_ro']['NAME'] = os.path.join(settings.BASE_DIR, '../database/db3.sqlite3')
    settings.DATABASES['interpro_ro']['TEST'] = {'MIRROR': 'default'}
