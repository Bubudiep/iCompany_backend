from rest_framework import serializers
from .models import *

class KhuCongNghiepSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhuCongNghiep
        fields = '__all__'
        
class CompanyListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLists
        fields = '__all__'
        
class BaivietTuyendungSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    images_details = serializers.SerializerMethodField()
    def get_images_details(self, obj):
        request = self.context.get('request')
        result = []
        for img in obj.images.all():
            if img.image:
                img_url = img.image.url
                if request:
                    img_url = request.build_absolute_uri(img_url)
                result.append({
                    "uid": str(img.id),                  # UID bắt buộc (nên là string)
                    "name": img.image.name.split('/')[-1], # Tên file hiển thị
                    "status": "done",                    # Trạng thái "done" để hiện khung xanh
                    "url": img_url,                      # Link ảnh để preview
                    # "thumbUrl": img_url                # (Tuỳ chọn) link thumbnail
                })
        return result
    class Meta:
        model = BaivietTuyendung
        fields = '__all__'
        read_only_fields=['user','code']
    def create(self, validated_data):
        images=validated_data.pop('images',None)
        created=super().create(validated_data)
        if images:
            for image_data in images:
                new_image = BaivietTuyenDungImages.objects.create(image=image_data)
                created.images.add(new_image)
        tags=validated_data.pop('tags',None)
        if tags:
            created.tags.set(tags)
        return created
    def update(self, instance, validated_data):
        images=validated_data.pop('images',None)
        if images:
            for image_data in images:
                new_image = BaivietTuyenDungImages.objects.create(image=image_data)
                instance.images.add(new_image)
        tags=validated_data.pop('tags',None)
        if tags:
            instance.tags.set(tags)
        return super().update(instance, validated_data)
        
class BaivietTuyendungTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaivietTuyendungTags
        fields = '__all__'
        
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


class AnhBaivietSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnhBaiviet
        fields = '__all__'
        read_only_fields = ['file_name', 'file_type', 'file_size']

class BaivietSerializer(serializers.ModelSerializer):
    images = AnhBaivietSerializer(many=True, required=False)
    likes_count = serializers.IntegerField(read_only=True)
    shares_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    # comments_count = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Baiviet
        fields = [
            'id', 'user', 'username', 'noidung', 'location_name', 
            'lat_location', 'long_location','likes', 'shares', 'loadeds', 'vieweds',
            'images','likes_count', 'shares_count', 'views_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'likes', 'shares', 'loadeds', 'vieweds']
    def validate(self, data):
        images_data = self.initial_data.getlist('images') # Lấy danh sách files từ request data (Multipart)
        if images_data and len(images_data) > 3:
            raise serializers.ValidationError(
                {"images": "Mỗi bài viết chỉ được đăng tối đa 3 ảnh."}
            )
        return data

    def create(self, validated_data):
        images_files = self.context['request'].FILES.getlist('images') 
        baiviet = Baiviet.objects.create(**validated_data)
        for image_file in images_files:
            AnhBaiviet.objects.create(baiviet=baiviet, image=image_file)
        return baiviet