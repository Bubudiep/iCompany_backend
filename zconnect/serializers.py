from rest_framework import serializers
from .models import *

class ZUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZUserNotification
        fields = "__all__"
class EHSImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EHSImage
        fields = ['id', 'image', 'created_at']
class MailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailRequest
        fields = "__all__"
class EHSIssueHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EHSIssueHistory
        fields = "__all__"
class EHSIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EHSIssue
        fields = "__all__"
class QNARequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QNARequest
        fields = "__all__"
class QNARequestViewSerializer(serializers.ModelSerializer):
    answer_by = serializers.CharField(source='answer_by.profile.name', read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    def get_author(self, obj):
        if obj.isAnonymous:
            return "Anonymous"
        if obj.author:
            return obj.author.profile.cardid
        return None
    class Meta:
        model = QNARequest
        fields = "__all__"
class EHSIssueViewSerializer(serializers.ModelSerializer):
    images = EHSImageSerializer(many=True, read_only=True)
    area = serializers.SlugRelatedField(
        many=True, 
        read_only=True, 
        slug_field='name'
    )
    categories = serializers.SlugRelatedField(
        many=True, 
        read_only=True, 
        slug_field='name'
    )
    author = serializers.CharField(source='author.profile.name', read_only=True)
    class Meta:
        model = EHSIssue
        fields = "__all__"