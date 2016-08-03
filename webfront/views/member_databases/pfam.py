from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from rest_framework import viewsets
from interpro.settings import DB_MEMBERS
from webfront.models.pfam import Clan, Pfama, Pfama2PfamaHhsearch, ClanMembership, PfamaRegFullSignificant, PfamseqMarkup
from webfront.serializers.pfam import ClanSerializer, PfamaSerializer, Pfama2PfamaHhsearchSerializer, MembershipSerializer
from webfront.active_sites import ActiveSites

db_members = DB_MEMBERS


def home_page(request):
    return render(request, 'home.html')


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
        list_of_families = i_filter# query to get the specific family

    if member is not None:
        list_of_families += " - "+member
    return list_of_families


def interpro_filter_page(request, i_filter):
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
        "list_of_families": get_filtered_information(i_filter, member),
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
            "family": family,
            "data_types": db_members[member.lower()]['options_per_family'],
            "list_of_families": get_filtered_information(i_filter, member),
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
                active_sites = ActiveSites(m_filter)
                active_sites.load_from_db()
                active_sites.load_alignment()

                return render(request, 'pfam_active_sites.html', {
                    "filter": i_filter,
                    "member": member,
                    "family": family,
                    "active_sites": active_sites,
                    "data_types": db_members[member.lower()]['options_per_family'],
                    "list_of_families": get_filtered_information(i_filter, member),
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
