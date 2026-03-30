from rest_framework import serializers
from .models import *

class ZUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZUserNotification
        fields = "__all__"
        
class EHSIssueSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return super().create(validated_data)
    class Meta:
        model = EHSIssue
        fields = "__all__"