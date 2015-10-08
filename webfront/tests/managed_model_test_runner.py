from django.test.runner import DiscoverRunner
import sys
from unifam.settings import *

class UnManagedModelTestRunner(DiscoverRunner):
    '''
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run.
    Many thanks to the Caktus Group: http://bit.ly/1N8TcHW
    '''

    def setup_test_environment(self, *args, **kwargs):
        from django.apps import apps
        myapp = apps.get_app_config('webfront')
        self.unmanaged_models = [m for m in myapp.models.values() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
        print("using the custom")
        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False

if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
    DATABASES['pfam_ro']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['pfam_ro']['NAME'] = os.path.join(BASE_DIR, '../database/db2.sqlite3')
    DATABASES['pfam_ro']['TEST'] = {'MIRROR': 'default'}
    del DATABASES['pfam_ro']['OPTIONS']

# DATABASE_ROUTERS = []

# Set Django's test runner to the custom class defined above
# TEST_RUNNER = 'webfront.tests.managed_model_test_runner.ManagedModelTestRunner'
