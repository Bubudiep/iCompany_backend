from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUser
        fields = ['id','username']
class NoteUserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUser
        fields = ['username', 'password']
    def create(self, validated_data):
        return NoteUser.objects.create(**validated_data)

class SharedNoteSerializer(serializers.ModelSerializer):
    shared_with_username = serializers.CharField(source='shared_with.username', read_only=True)
    class Meta:
        model = SharedNote
        fields = '__all__'

class NoteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteType
        fields = '__all__'
        read_only_fields=['user']
class NoteCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteCustomer
        fields = '__all__'
        read_only_fields=['user']
        
class UserNotesSerializer(serializers.ModelSerializer):
    phanloai = serializers.CharField(source="loai.type", read_only=True,allow_null=False, allow_blank=True)
    hoten = serializers.CharField(source="khachhang.hoten",read_only=True, allow_null=False, allow_blank=True)
    sodienthoai = serializers.CharField(source="khachhang.sodienthoai",read_only=True, allow_null=False, allow_blank=True)
    shared_with = SharedNoteSerializer(source='sharednote_set', many=True, read_only=True)
    class Meta:
        model = UserNotes
        fields = '__all__'
        read_only_fields=['user']