from rest_framework import serializers
from webfront.models import Clan, Pfama


class ClanMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('pfama_acc','clan_acc')

class PfamaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pfama
        fields = ('pfama_acc','pfama_id')

class ClanSerializer(serializers.HyperlinkedModelSerializer):
    members = PfamaSerializer(many=True, read_only=True)

    class Meta:
        model = Clan
        fields = ('clan_acc', 'clan_id','members')
