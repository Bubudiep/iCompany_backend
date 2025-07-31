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

class UserNotesSerializer(serializers.ModelSerializer):
    shared_with = SharedNoteSerializer(source='sharednote_set', many=True, read_only=True)
    class Meta:
        model = UserNotes
        fields = '__all__'