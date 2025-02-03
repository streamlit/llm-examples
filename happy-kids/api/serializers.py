from rest_framework import serializers
from .models import *

class historicalSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = historicalSessions
        fields = ('id','sessionDate','username')

class LuluTrainningSerializer(serializers.ModelSerializer):
    class Meta:
        model = luluTrainning
        fields = ('id','version_title','attachments','comments','creation_date')

class UsersMilestonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersMilestones
        fields = ('id','user','milestone','completed','created_at')
