from .models import *
from rest_framework import serializers

class ZaloUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZaloUser
        fields = '__all__'

class ZaloUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZaloUserProfile
        exclude = ['user','created_at']
        
class ZaloUserProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZaloUserProfile
        exclude = ['user']
        read_only_fields = ['user','id','created_at','updated_at']
        
class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        
class LastCheckGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastCheckGroup
        fields = '__all__'
        
class ApproveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveType
        fields = '__all__'
        
class ApproveItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveItem
        fields = '__all__'
        
class ApproveItemRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveItemRecord
        fields = '__all__'