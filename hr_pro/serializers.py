from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    level_name = serializers.ReadOnlyField(source='get_level_display')
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields=['user']
        
class UserSerializer(serializers.ModelSerializer):
    profile=serializers.SerializerMethodField(read_only=True)
    def get_profile(self,obj):
        try:
            qs_profile=UserProfile.objects.get(user=obj)
            return UserProfileSerializer(qs_profile).data
        except Exception as e:
            return {}
    class Meta:
        model = HRUser
        fields = ['id','username','profile']