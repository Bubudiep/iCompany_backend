from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
class UserSerializer(serializers.ModelSerializer):
    profile=serializers.SerializerMethodField(read_only=True)
    def get_profile(self,obj):
        try:
            qs_profile,_=UserProfile.objects.get_or_create(user=obj)
            return UserProfileSerializer(qs_profile).data
        except Exception as e:
            return {}
    class Meta:
        model = User
        fields = [
            'id','is_active','email','profile',
            'date_joined','last_login'
        ]
        