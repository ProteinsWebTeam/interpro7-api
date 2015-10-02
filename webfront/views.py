from django.shortcuts import render
from webfront.models import Clan


def home_page(request):
    clan = Clan.objects.using('pfam_ro').last()
    return render(request, 'home.html', {"clan":clan})
