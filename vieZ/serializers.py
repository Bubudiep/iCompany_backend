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
    categorys=serializers.SerializerMethodField(read_only=True)
    def get_categorys(self,obj):
        try:
            qs_categody=AppCategorys.objects.all()
            return AppCategorysSerializer(qs_categody,many=True).data
        except Exception as e:
            return {"detail":f"{e}"}
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
            request = self.context.get("request")
            return UserFileSerializer(qs_files,many=True,context={'request': request}).data
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
            'id','profile','files','config','plan','categorys',
            'created_at','last_login'
        ]
        
class UserFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    class Meta:
        model = UserFile
        fields = ['id', 'file','file_type','file_url', 'file_name', 'file_size', 'uploaded_at']
        read_only_fields = ['file_name', 'file_size', 'uploaded_at']
        
class UserAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApps
        fields = '__all__'
        read_only_fields = ['app_id', 'created_at', 'updated_at', 'user']
        
class UserAppsConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppsConfigs
        fields = '__all__'
        
class UserAppDetailSerializer(serializers.ModelSerializer):
    configs=serializers.SerializerMethodField(read_only=True)
    def get_configs(self,obj):
        try:
            qs_config=UserAppsConfigs.objects.filter(app=obj)
            return UserAppsConfigsSerializer(qs_config,many=True).data
        except Exception as e:
            return {"detail":f"{e}"}
    class Meta:
        model = UserApps
        fields = ['name','is_active','is_approve','is_live','configs',
                  'category','app_id','avatar','descriptions',
                  'created_at','updated_at']
        read_only_fields = ['app_id', 'created_at', 'updated_at', 'user']
        
class AppCategorysSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppCategorys
        fields = '__all__'

class StoreMemberSerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()
    def get_feedback(self, obj):
        try:
            qs_feedb=StoreFeedbacks.objects.get(member=obj)
            return StoreFeedbacksSerializer(qs_feedb).data
        except Exception:
            return None
    class Meta:
        model = StoreMember
        fields = ['id','email','phone','avatar','username','feedback']
     
class StoreNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNews
        fields = "__all__"
class StoreSlidesSerializer(serializers.ModelSerializer):
    img_base64 = serializers.SerializerMethodField()
    def get_img_base64(self, obj):
        if not obj.img_base64:
            return None
        try:
            img_data = base64.b64decode(obj.img_base64.split(",")[-1])
            image = Image.open(BytesIO(img_data))
            image.thumbnail((450, 250))
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            thumb_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{thumb_base64}"
        except Exception:
            return None
    class Meta:
        model = StoreSlides
        fields = "__all__"
class StoreProductsCtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductsCtl
        fields = "__all__"
class StoreProductsSerializer(serializers.ModelSerializer):
    img_base64 = serializers.SerializerMethodField()
    class Meta:
        model = StoreProducts
        fields = "__all__"
    def get_img_base64(self, obj):
        if not obj.img_base64:
            return None
        try:
            img_data = base64.b64decode(obj.img_base64.split(",")[-1])
            image = Image.open(BytesIO(img_data))
            image.thumbnail((88, 88))
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            thumb_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{thumb_base64}"
        except Exception:
            return None
         
class StoreFeedbacksSerializer(serializers.ModelSerializer):
    member= StoreMemberSerializer(read_only=True)
    class Meta:
        model = StoreFeedbacks
        fields = "__all__"
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
class OrderSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    def get_item(self, obj):
        try:
            qs_item=OrderItem.objects.filter(order=obj)
            return OrderItemSerializer(qs_item,many=True).data
        except Exception:
            return []
    class Meta:
        model = Order
        fields = "__all__"
        
class StoreCollabsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCollabs
        fields = "__all__"
        
class StoreNewsLTESerializer(serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()
    def get_image_base64(self, obj):
        if not obj.image_base64:
            return None
        try:
            img_data = base64.b64decode(obj.image_base64.split(",")[-1])
            image = Image.open(BytesIO(img_data))
            image.thumbnail((88, 88))
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            thumb_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{thumb_base64}"
        except Exception:
            return None
    class Meta:
        model = StoreNews
        fields = ["id","image_base64","title","short","created_at"]

        
class MemberCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberCart
        fields = '__all__'
        read_only_fields = ['member']
        
class UserStoreMemberViewsSerializer(serializers.ModelSerializer):
    products_cate=serializers.SerializerMethodField(read_only=True)
    def get_products_cate(self,obj):
        qs_products_cate=StoreProductsCtl.objects.filter(store=obj)
        return StoreProductsCtlSerializer(qs_products_cate,many=True).data
    class Meta:
        model = UserStore
        fields = [
            "store_collabs",
            "descriptions",
            "store_name",
            "store_hotline",
            "products_cate",
            "updated_at"
        ]