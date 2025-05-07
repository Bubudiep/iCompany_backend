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
        read_only_fields = ['key','last_have_message_at','member',
                            'host','id','created_at','updated_at']
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
        
class ApproveItemRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveItemRecord
        fields = '__all__'
class ApproveItemEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveItemEmoji
        fields = ['user','emoji','count']
        
class UserGroupRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroupRecord
        fields = '__all__'
        
class ApproveItemMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveItemMessage
        fields = '__all__'
        
class ApproveItemSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField(read_only=True)
    chat = serializers.SerializerMethodField(read_only=True)
    def get_chat(self, obj):
        qs_item=ApproveItemMessage.objects.filter(item=obj)
        return {
            "last_message": None if not qs_item.first() else ApproveItemMessageSerializer(qs_item.first()).data,
            "total":qs_item.count()
        }
    def get_history(self, obj):
        qs_item=ApproveItemRecord.objects.filter(item=obj)
        return qs_item.count()
    class Meta:
        model = ApproveItem
        fields = '__all__'
        
class ApproveItemsSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)
    emoji = serializers.SerializerMethodField(read_only=True)
    lastcheck = serializers.SerializerMethodField(read_only=True)
    def get_emoji(self, obj):
        qs_emj=ApproveItemEmoji.objects.filter(item=obj)
        result = {}
        for emj in qs_emj:
            user_id = emj.user.id
            if user_id not in result:
                result[user_id] = {}
            result[user_id][emj.emoji] = emj.count
        return result
    
    def get_lastcheck(self, obj):
        try:
            request = self.context.get('request')
            user = getattr(request, 'user', None)
            zuser=ZaloUser.objects.get(user=user)
            if not zuser or not user.is_authenticated:
                return None
            qs_item,_=LastCheckItem.objects.get_or_create(item=obj,user=zuser)
            return ApproveItemMessageSerializer(qs_item,many=True).data
        except Exception as e:
            print(f"{e}")
    def get_message(self, obj):
        qs_item=ApproveItemMessage.objects.filter(item=obj)
        return ApproveItemMessageSerializer(qs_item,many=True).data
    def get_history(self, obj):
        qs_item=ApproveItemRecord.objects.filter(item=obj)
        return ApproveItemRecordSerializer(qs_item,many=True).data
    class Meta:
        model = ApproveItem
        fields = '__all__'
        read_only_fields = ['author','group','status','id','created_at','updated_at']
        
class UserGroupsSerializer(serializers.ModelSerializer):
    types = serializers.SerializerMethodField(read_only=True)
    items = serializers.SerializerMethodField(read_only=True)
    records = serializers.SerializerMethodField(read_only=True)
    def get_records(self, obj):
        qs_rc=UserGroupRecord.objects.filter(group=obj)
        return UserGroupRecordSerializer(qs_rc,many=True).data
    def get_items(self, obj):
        qs_item=ApproveItem.objects.filter(group=obj)[:20]
        return ApproveItemSerializer(qs_item,many=True).data
    def get_types(self, obj):
        qs_type=ApproveType.objects.filter(group=obj)
        return ApproveTypeSerializer(qs_type,many=True).data
    class Meta:
        model = UserGroup
        fields = '__all__'
        