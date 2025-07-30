from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        
class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = "__all__"
        
class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfigs
        fields = "__all__"
        
class UserSerializer(serializers.ModelSerializer):
    profile=serializers.SerializerMethodField(read_only=True)
    files=serializers.SerializerMethodField(read_only=True)
    config=serializers.SerializerMethodField(read_only=True)
    plan=serializers.SerializerMethodField(read_only=True)
    def get_plan(self,obj):
        try:
            qs_plan=UserPlan.objects.all()
            return UserPlanSerializer(qs_plan,many=True).data
        except Exception as e:
            return {"detail":f"{e}"}
    def get_config(self,obj):
        try:
            qs_config,_=UserConfigs.objects.get_or_create(user=obj)
            return UserConfigSerializer(qs_config).data
        except Exception as e:
            return {"detail":f"{e}"}
    def get_files(self,obj):
        try:
            qs_files=UserFile.objects.filter(user=obj)
            return UserFileSerializer(qs_files,many=True).data
        except Exception as e:
            return []
    def get_profile(self,obj):
        try:
            qs_profile,_=UserProfile.objects.get_or_create(user=obj)
            return UserProfileSerializer(qs_profile).data
        except Exception as e:
            return {}
    class Meta:
        model = Users
        fields = [
            'id','profile','files','config','plan',
            'created_at','last_login'
        ]
        
class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ['id', 'file', 'file_name', 'file_size', 'uploaded_at']
        read_only_fields = ['file_name', 'file_size', 'uploaded_at']