from rest_framework import serializers
from webfront.models import Clan, Pfama, Pfama2PfamaHhsearch, ClanMembership


class PfamaSerializer(serializers.HyperlinkedModelSerializer):
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        return "http://pfam.xfam.org/family/"+obj.pfama_acc

    class Meta:
        model = Pfama
        fields = ('pfama_acc', 'pfama_id', 'num_full','link')


class Pfama2PfamaHhsearchSerializer(serializers.HyperlinkedModelSerializer):
    pfama_acc_1 = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    pfama_acc_2 = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    evalue = serializers.FloatField()

    class Meta:
        model = Pfama2PfamaHhsearch
        fields = ('pfama_acc_1','pfama_acc_2','evalue')


class ClanSerializer(serializers.HyperlinkedModelSerializer):
    members = PfamaSerializer(many=True, read_only=True)
    relationships = serializers.SerializerMethodField()
    total_occurrences = serializers.SerializerMethodField()

    def get_total_occurrences(self,obj):
        total =0;
        for member in obj.members.all():
            total += member.num_full
        return total

    def get_relationships(self, obj):
        queryset = Pfama2PfamaHhsearch.objects.using('pfam_ro').all().filter(pfama_acc_1__clan=obj).filter(pfama_acc_2__clan=obj)
        serializer = Pfama2PfamaHhsearchSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Clan
        fields = ('clan_acc', 'clan_id', 'total_occurrences', 'members', 'relationships')

class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClanMembership
        fields = ('clan_acc', 'pfama_acc')
