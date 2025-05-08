from .models import *
from rest_framework import serializers

class JobsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobsUser
        fields = '__all__'
