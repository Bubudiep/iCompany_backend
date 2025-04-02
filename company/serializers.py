from rest_framework import serializers
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['companyType','avatar','name','fullname','address',
        'addressDetails','hotline','isValidate','isOA','wallpaper',
        'shortDescription','description','created_at']

class CompanyDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDepartment
        fields = '__all__'

class CompanyPossitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPossition
        fields = '__all__'
        
class CompanyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = '__all__'
        
class CompanyStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyStaff
        fields = ['id','cardID','isActive','isSuperAdmin','isAdmin','isBan',
                  'isOnline','isValidate','socket_id','created_at','updated_at']
        
class CompanyStaffHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyStaffHistory
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'full_name', 'phone', 'gender',
            'avatar', 'avatar_base64', 'date_of_birth', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
