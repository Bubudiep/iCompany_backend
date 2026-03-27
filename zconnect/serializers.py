from rest_framework import serializers
from .models import *

class ZUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZUserNotification
        fields = "__all__"
        