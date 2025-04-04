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
        
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
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
 
class AppChatRoomSerializer(serializers.ModelSerializer):
    not_read = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    members = CompanyStaffSerializer(many=True)
    def get_not_read(self,room):
        try:
            qs_last_seen=AppChatStatus.objects.filter(room=room,
                    user__user__user=self.context['request'].user).first()
            if qs_last_seen:
                qs_not_read=ChatMessage.objects.filter(room=room,
                    created_at__gt=qs_last_seen.last_read_at).count()
            else:
                qs_not_read=ChatMessage.objects.filter(room=room).count()
            return qs_not_read
        except Exception as e:
            return 0
    def get_last_message(self,room):
        try:
            qs_mess=ChatMessage.objects.filter(room=room).first()
            return ChatMessageSerializer(qs_mess).data
        except Exception as e:
            return None
    class Meta:
        model = AppChatRoom
        fields = '__all__'