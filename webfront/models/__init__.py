from webfront.models.pfam import *
# TODO: check why tests fail when the interpro model is included
# The problem is that that there are not migrations for this models, but there are errors when running makemigrations.
# ../virtualenv/bin/python manage.py makemigrations -n adding_interpro_models
# from webfront.models.interpro import *
