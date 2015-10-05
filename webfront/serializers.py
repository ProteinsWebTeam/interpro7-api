from rest_framework import serializers
from webfront.models import Clan


class ClanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clan
        fields = ('clan_acc', 'clan_id')
