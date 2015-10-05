from django.shortcuts import render
from webfront.models import Clan
from rest_framework import viewsets
from webfront.serializers import ClanSerializer


def home_page(request):
    return render(request, 'home.html')


def clans_page(request):
    clans = Clan.objects.using('pfam_ro').all()
    return render(request, 'clans.html', {"clans":clans})


def clan_page(request, clan_id):
    clan = Clan.objects.using('pfam_ro').get(clan_id=clan_id)
    return render(request, 'clan.html', {"clan": clan})


class ClanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Clan.objects.using('pfam_ro').all()
    serializer_class = ClanSerializer
