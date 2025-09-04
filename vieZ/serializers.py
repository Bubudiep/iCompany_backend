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

class StoreProductsCtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductsCtl
        fields = ['id','name','code','descriptions']
        
class StoreProductsSerializer(serializers.ModelSerializer):
    img_base64 = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = StoreProducts
        fields = "__all__"
    def to_representation(self, instance):
        """Xử lý khi trả data ra (resize, trả về thumbnail)"""
        ret = super().to_representation(instance)
        img_data = ret.get("img_base64")
        if not img_data:
            return ret
        try:
            if img_data.startswith("data:image/png;base64,"):
                raw = base64.b64decode(img_data.split(",")[-1])
                image = Image.open(BytesIO(raw))
                image.thumbnail((88, 88))
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                thumb_base64 = base64.b64encode(buffer.getvalue()).decode()
                ret["img_base64"] = f"data:image/png;base64,{thumb_base64}"
        except Exception:
            ret["img_base64"] = None
        return ret
    def create(self, validated_data):
        category=validated_data.pop('category',None)
        created=StoreProducts.objects.create(**validated_data)
        if category:
            created.category.set(category)
        return created
    def update(self, instance, validated_data):
        """Chỉ update img_base64 hoặc field khác nếu có"""
        category=validated_data.pop('category',None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if category:
            instance.category.set(category)
        instance.save()
        return instance

        
class UserStoreSerializer(serializers.ModelSerializer):
    product_categorys=serializers.SerializerMethodField(read_only=True)
    def get_product_categorys(self,obj):
        try:
            qs_cates=StoreProductsCtl.objects.filter(store=obj)
            return StoreProductsCtlSerializer(qs_cates,many=True).data
        except Exception as e:
            return {"detail":f"{e}"}
    class Meta:
        model = UserStore
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
            qs_config=UserConfigs.objects.get(user=obj)
            return UserPlanSerializer(qs_config.plan).data
        except Exception as e:
            return {"detail":f"{e}"}
    def get_config(self,obj):
        try:
            qs_config, created=UserConfigs.objects.get_or_create(user=obj)
            if created:
                free_plan=UserPlan.objects.get(name='Free')
                created.plan=free_plan
                created.save()
                return UserConfigSerializer(created).data
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
            return f"{e}"
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
        
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['user']
        
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