from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from webfront.models import Clan, Pfama, Pfama2PfamaHhsearch, ClanMembership
from rest_framework import viewsets
from webfront.serializers import ClanSerializer, PfamaSerializer, Pfama2PfamaHhsearchSerializer, MembershipSerializer
from django.http import HttpResponseNotFound

db_members = {
    'cath-gene3d': {
        'filter': 'cath-gene3d',
        'label': 'CATH-Gene3D',
        'options': [],
        'options_per_family': []
    },
    'hamap': {
        'filter': 'hamap',
        'label': 'HAMAP',
        'options': [],
        'options_per_family': []
    },
    'panther': {
        'filter': 'panther',
        'label': 'PANTHER',
        'options': [],
         'options_per_family': []
    },
    'pirsf': {
        'filter': 'pirsf',
        'label': 'PIRSF',
        'options': [],
         'options_per_family': []
    },
    'prints': {
        'filter': 'prints',
        'label': 'PRINTS',
        'options': [],
        'options_per_family': []
    },
    'prosite_patterns': {
        'filter': 'prosite_patterns',
        'label': 'PROSITE patterns',
        'options': [],
        'options_per_family': []
    },
    'prosite_profiles': {
        'filter': 'prosite_profiles',
        'label': 'PROSITE profiles',
        'options': [],
        'options_per_family': []
    },
    'pfam': {
        'filter': 'pfam',
        'label': 'Pfam',
        'options': [{
            "label": "Clans",
            "filter": "clans"
        }],
        'options_per_family': [{
            "label": "Active Sites",
            "filter": "active_sites"
        }]
    },
    'prodom': {
        'filter': 'prodom',
        'label': 'ProDom',
        'options': [],
        'options_per_family': []
    },
    'smart': {
        'filter': 'smart',
        'label': 'SMART',
        'options': [],
        'options_per_family': []
    },
    'superfamily': {
        'filter': 'superfamily',
        'label': 'SUPERFAMILY',
        'options': [],
        'options_per_family': []
    },
    'tigrfams': {
        'filter': 'tigrfams',
        'label': 'TIGRFAMs',
        'options': [],
        'options_per_family': []
    }
}


def home_page(request):
    return render(request, 'home.html')


# def clans_page(request):
#     clans = Clan.objects.using('pfam_ro').all()
#     return render(request, 'clans.html', {"clans":clans})
#
#

def entries_page(request):
    return render(request, 'entries.html')


def interpro_page(request):
    return redirect('interpro_filter_page', "integrated")
#    return HttpResponseNotFound("The URL is wrong. at this level the only valid resource is /interpro/")


def get_filtered_information(i_filter="integrated", member=None):
    if i_filter == "all":
        list_of_families = "All" # query to get all
    elif i_filter == "unintegrated":
        list_of_families = "Unintegrated" # query to get unintegrated
    elif i_filter == "integrated":
        list_of_families = "Integrated" # query to get integrated
    else:
        list_of_families =  i_filter# query to get the specific family

    if member != None:
        list_of_families += " - "+member
    return list_of_families


def interpro_filter_page(request, i_filter):
    print(db_members)
    return render(request, 'interpro_entries.html', {
        "filter": i_filter,
        "list_of_families": get_filtered_information(i_filter),
        "db_members": db_members
    })


def interpro_member_page(request, i_filter, member):
    families=[]
    if member.lower() == "pfam":
        families = Pfama.objects.using('pfam_ro').all()[:200]
    return render(request, 'interpro_member_entries.html', {
        "filter": i_filter,
        "member": member,
        "families": families,
        "data_types": db_members[member.lower()]['options'],
        "list_of_families": get_filtered_information(i_filter,member),
        "db_members": db_members
    })


def interpro_member_filter_page(request, i_filter, member, m_filter):
    if member.lower() == "pfam":
        if m_filter.lower() == "clans":
            clans = Clan.objects.using('pfam_ro').all()
            return render(request, 'clans.html', {
                "filter": i_filter,
                "member": member,
                "m_filter": m_filter,
                "clans": clans
            })
        else:
            try:
                family = Pfama.objects.using('pfam_ro').get(pfama_acc=m_filter)
            except ObjectDoesNotExist:
                return HttpResponseNotFound("Family accession "+m_filter+" not found")


        return render(request, 'pfam_family.html', {
            "filter": i_filter,
            "member": member,
            "m_filter": m_filter,
            "family":family,
            "data_types": db_members[member.lower()]['options_per_family'],
            "list_of_families": get_filtered_information(i_filter,member),
            "db_members": db_members
        })


def interpro_member_filter_acc_page(request, i_filter, member, m_filter, option):
    if member.lower() == "pfam":
        if m_filter.lower() == "clans":
            clan = Clan.objects.using('pfam_ro').get(clan_acc=option)
            return render(request, 'clan.html', {
                "filter": i_filter,
                "member": member,
                "m_filter": m_filter,
                "data_types": db_members[member.lower()]['options'],
                "clan": clan
            })
        else:
            family = Pfama.objects.using('pfam_ro').get(pfama_acc=m_filter)
            if option == "active_sites":
                return render(request, 'pfam_active_sites.html', {
                    "filter": i_filter,
                    "member": member,
                    "family":family,
                    "data_types": db_members[member.lower()]['options_per_family'],
                    "list_of_families": get_filtered_information(i_filter,member),
                    "db_members": db_members
                })





class ClanViewSet(viewsets.ModelViewSet):
    queryset = Clan.objects.using('pfam_ro').all()
    serializer_class = ClanSerializer


class PFamAViewSet(viewsets.ModelViewSet):
    queryset = Pfama.objects.using('pfam_ro').all()
    serializer_class = PfamaSerializer


class PFamA2PFamAViewSet(viewsets.ModelViewSet):
    queryset = Pfama2PfamaHhsearch.objects.using('pfam_ro').all()
    serializer_class = Pfama2PfamaHhsearchSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = ClanMembership.objects.using('pfam_ro').all()
    serializer_class = MembershipSerializer
