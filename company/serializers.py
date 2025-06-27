from rest_framework import serializers
from .models import *

class OP_HISTLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorWorkHistory
        fields = ['ma_nhanvien','start_date','customer']
        
class OP_HISTSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        if validated_data.get('customer') is None:
            raise TypeError("Vui lòng nhập công ty làm việc")
        if instance.start_date is None and not validated_data.get('start_date'):
            raise TypeError("Vui lòng nhập ngày bắt đầu")
        if instance.end_date is None and not validated_data.get('end_date'):
            qs_working=OperatorWorkHistory.objects.filter(
                operator=instance.operator,
                end_date__isnull=True
            ).exclude(id=instance.id)
            if len(qs_working)>0:
                raise TypeError("Chỉ được làm việc tại 1 công ty")
            elif validated_data.get('customer'):
                instance.operator.congty_danglam=validated_data.get('customer')
                instance.operator.save()
        note=f" {instance.customer.name} -> {validated_data.get('customer').name}" if validated_data.get('customer') is not None else ""
        OperatorUpdateHistory.objects.create(
            changed_by=user,
            operator=instance.operator,
            notes=f"Cập nhập lịch sử đi làm ở công ty{note}"
        )
        return super().update(instance, validated_data)
    class Meta:
        model = OperatorWorkHistory
        fields = '__all__'
        
class CompanyOperatorDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyOperator
        fields = ["id","congty_danglam",
                  "nguoibaocao","nguoituyen"]
class CompanyOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyOperator
        fields = ["id","avatar","ho_ten","congty_danglam",
                  "diachi","ghichu","ma_nhanvien","ngaysinh",
                  "nguoibaocao","nguoituyen","nhachinh","sdt","so_cccd"]
        
class CompanyStaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar_base64 = serializers.SerializerMethodField(read_only=True)
    def get_avatar_base64(self,obj):
        try:
            return resize_base64_image(obj.avatar_base64,(84,84)) if obj.avatar_base64 else None
        except Exception as e:
            return f"{e}"
    class Meta:
        model = CompanyStaffProfile
        fields = [
            'id', 'username', 'email', 'full_name', 'nick_name', 'phone', 'gender',
            'avatar', 'avatar_base64', 'date_of_birth', 'created_at', 'updated_at',
            'nganhang', 'so_taikhoan', 'chu_taikhoan','zalo','facebook'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
class CompanyStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    department_name = serializers.CharField(source='department.name',allow_null=True, read_only=True)
    possition_name = serializers.CharField(source='possition.name',allow_null=True, read_only=True)
    def get_profile(self,staff):
        try:
            qs_profile=CompanyStaffProfile.objects.get(staff=staff)
            return CompanyStaffProfileSerializer(qs_profile).data
        except Exception as e:
            return None
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    class Meta:
        model = CompanyStaff
        fields = '__all__'
        
class LastCheckAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = LastCheckAPI
        fields = '__all__'

class CompanyPossitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPossition
        fields = '__all__'
        read_only_fields = ['company']
        
class CompanyPossitionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPossition
        fields = '__all__'
        read_only_fields = ['company']
        
class CompanyDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDepartment
        fields = '__all__'
        read_only_fields = ['company']
        
class CompanyDepartmentDetailsSerializer(serializers.ModelSerializer):
    Possition = serializers.SerializerMethodField(read_only=True)
    def get_Possition(self,dept):
        try:
            allPossition=CompanyPossition.objects.filter(company=dept.company,department=dept)
            return CompanyPossitionDetailsSerializer(allPossition,many=True).data
        except Exception as e:
            return None
    class Meta:
        model = CompanyDepartment
        fields = '__all__'
        read_only_fields = ['company']
      
class CompanyCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model =CompanyCustomer
        fields = '__all__'
        read_only_fields = ['company']
        
class CompanyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model =CompanyConfig
        fields = '__all__'
        read_only_fields = ['company']
        
class CompanyVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model =CompanyVendor
        fields = '__all__'
        read_only_fields = ['company','id']
          
class CompanySerializer(serializers.ModelSerializer):
    Department = serializers.SerializerMethodField(read_only=True)
    Customer = serializers.SerializerMethodField(read_only=True)
    Vendor = serializers.SerializerMethodField(read_only=True)
    Staff = serializers.SerializerMethodField(read_only=True)
    Config = serializers.SerializerMethodField(read_only=True)
    def get_Config(self,company):
        try:
            allConfig,_=CompanyConfig.objects.get_or_create(company=company)
            return CompanyConfigSerializer(allConfig).data
        except Exception as e:
            return []
    def get_Staff(self,company):
        try:
            allStaff=CompanyStaff.objects.filter(company=company)
            return CompanyStaffSerializer(allStaff,many=True).data
        except Exception as e:
            return []
    def get_Vendor(self,company):
        try:
            allVendor=CompanyVendor.objects.filter(company=company)
            return CompanyVendorSerializer(allVendor,many=True).data
        except Exception as e:
            return []
    def get_Customer(self,company):
        try:
            allCustomer=CompanyCustomer.objects.filter(company=company)
            return CompanyCustomerSerializer(allCustomer,many=True).data
        except Exception as e:
            return []
    Department = serializers.SerializerMethodField(read_only=True)
    def get_Department(self,company):
        try:
            allDepartment=CompanyDepartment.objects.filter(company=company)
            return CompanyDepartmentDetailsSerializer(allDepartment,many=True).data
        except Exception as e:
            return []
    class Meta:
        model = Company
        fields = ['companyType','avatar','name','fullname','address',
            'Department','Customer','Vendor','Staff','Config',
            'addressDetails','hotline','isValidate','isOA','wallpaper',
            'shortDescription','description','created_at']
        
class CompanyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CompanyUser
        fields = ['username', 'password']
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = make_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        
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
 
class CompanyStaffHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyStaffHistory
        fields = '__all__'
        
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        
class AppChatRoomSerializer(serializers.ModelSerializer):
    not_read = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    # messages = serializers.SerializerMethodField()
    members = CompanyStaffSerializer(many=True)
    ghim = serializers.SerializerMethodField()
    def get_ghim(self,room):
        try:
            ghim=ChatMessage.objects.filter(room=room,ghim_by__isnull=False)
            return ChatMessageSerializer(ghim,many=True).data
        except Exception as e:
            return []
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
    # def get_messages(self,room):
    #     qs_mess=ChatMessage.objects.filter(room=room,isAction=False)[:30]
    #     if qs_mess:
    #         return ChatMessageSerializer(qs_mess,many=True).data
    #     else:
    #         return None
    def get_last_message(self,room):
        qs_mess=ChatMessage.objects.filter(room=room,isAction=False).first()
        if qs_mess:
            return ChatMessageSerializer(qs_mess).data
        else:
            return None
    class Meta:
        model = AppChatRoom
        fields = '__all__'
class AppChatRoomDetailSerializer(serializers.ModelSerializer):
    not_read = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    members = CompanyStaffSerializer(many=True)
    ghim = serializers.SerializerMethodField()
    def get_ghim(self,room):
        try:
            ghim=ChatMessage.objects.filter(room=room,ghim_by__isnull=False)
            return ChatMessageSerializer(ghim,many=True).data
        except Exception as e:
            return []
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
    def get_message(self,room):
        try:
            qs_mess=ChatMessage.objects.filter(room=room)
            return {
                'total':len(qs_mess),
                "data":ChatMessageSerializer(qs_mess[:30],many=True).data
            }
        except Exception as e:
            return None
    class Meta:
        model = AppChatRoom
        fields = '__all__'
        
class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyOperator
        fields = ['id','ho_ten','trangthai']
        
class CompanyStaffDetailsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    department_name = serializers.SerializerMethodField(read_only=True)
    possition_name = serializers.SerializerMethodField(read_only=True)
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    def get_possition_name(self, obj):
        return obj.possition.name if obj.possition else None
    def get_profile(self, qs):
        try:
            profile=CompanyStaffProfile.objects.get(staff=qs)
            return CompanyStaffProfileSerializer(profile).data
        except CompanyStaffProfile.DoesNotExist:
            return None
            
    class Meta:
        model = CompanyStaff
        fields = [
            'id','cardID','username',
            'company','user','department','managerCustomer',
            'possition','isSuperAdmin','isActive','isAdmin',
            'isOnline','isValidate','socket_id','profile',
            'created_at','department_name','possition_name'
        ]
class CompanyStaffProfileLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyStaffProfile
        fields = ['full_name','nick_name','avatar']

class CompanyStaffSmallSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    def get_profile(self, qs):
        try:
            profile=CompanyStaffProfile.objects.get(staff=qs)
            return CompanyStaffProfileLTESerializer(profile).data
        except CompanyStaffProfile.DoesNotExist:
            return None
    class Meta:
        model = CompanyStaff
        fields = [
            'id','cardID','department',
            'possition','isSuperAdmin',
            'isActive','isAdmin',
            'isOnline','isValidate',
            'socket_id','profile',
            'created_at'
        ]
class AdvanceTypeSerializer(serializers.ModelSerializer):     
    class Meta:
        model = AdvanceType
        fields = '__all__'
class AdvanceReasonTypeSerializer(serializers.ModelSerializer):     
    class Meta:
        model = AdvanceReasonType
        fields = '__all__'
        
class AdvanceRequestHistorySerializer(serializers.ModelSerializer):
    user = CompanyStaffDetailsSerializer(allow_null=True)  
    class Meta:
        model = AdvanceRequestHistory
        fields = '__all__'
        
class AdvanceRequestLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceRequest
        fields = ['amount','status','payment_status','retrieve_status','created_at']
             
class AdvanceRequestSerializer(serializers.ModelSerializer):
    requesttype = serializers.CharField(source='requesttype.typecode', read_only=True, allow_null=True)
    operator = serializers.CharField(source='operator.ho_ten', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    retrieve_status_display = serializers.CharField(source='get_retrieve_status_display', read_only=True)
    hinhthucThanhtoan_display = serializers.CharField(source='get_hinhthucThanhtoan_display', read_only=True)
    nguoiThuhuong_display = serializers.CharField(source='get_nguoiThuhuong_display', read_only=True)
    class Meta:
        model = AdvanceRequest
        fields = '__all__'
        
class AdvanceRequestDetailsSerializer(serializers.ModelSerializer):
    reason = AdvanceReasonTypeSerializer(allow_null=True)
    requesttype = AdvanceTypeSerializer(allow_null=True)
    operator = OperatorSerializer(allow_null=True)
    history = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    retrieve_status_display = serializers.CharField(source='get_retrieve_status_display', read_only=True)
    hinhthucThanhtoan_display = serializers.CharField(source='get_hinhthucThanhtoan_display', read_only=True)
    nguoiThuhuong_display = serializers.CharField(source='get_nguoiThuhuong_display', read_only=True)
    def get_history(self, qs):
        qs_his=AdvanceRequestHistory.objects.filter(request=qs)
        return AdvanceRequestHistorySerializer(qs_his,many=True).data
    class Meta:
        model = AdvanceRequest
        fields = '__all__'
               
class OperatorUpdateHistorySerializer(serializers.ModelSerializer):
    changed_by=CompanyStaffProfileSerializer(allow_null=True)
    class Meta:
        model = OperatorUpdateHistory
        fields = '__all__'
class CompanyOperatorWorkHistorySerializer(serializers.ModelSerializer):
    work = serializers.SerializerMethodField(read_only=True)
    def get_work(self, qs):
        qs_work=OperatorWorkHistory.objects.filter(operator=qs)
        return OP_HISTSerializer(qs_work,many=True).data
    class Meta:
        model = CompanyOperator
        fields = '__all__'
            
class CompanyOperatorMoreDetailsSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    work = serializers.SerializerMethodField(read_only=True)
    thamnien = serializers.SerializerMethodField(read_only=True)
    baoung = serializers.SerializerMethodField(read_only=True)
    baogiu = serializers.SerializerMethodField(read_only=True)
    history = serializers.SerializerMethodField(read_only=True)
    def get_history(self, qs):
        qs_update=OperatorUpdateHistory.objects.filter(operator=qs)
        return OperatorUpdateHistorySerializer(qs_update,many=True).data
    def get_baoung(self, qs):
        try:
            qs_baoung=AdvanceRequest.objects.filter(
                operator=qs,
                requesttype__typecode="Báo ứng"
            )
            return AdvanceRequestSerializer(qs_baoung,many=True).data
        except Exception as e:
            print(f"{e}")
            return []
    def get_baogiu(self, qs):
        try:
            qs_baogiu=AdvanceRequest.objects.filter(
                operator=qs,
                requesttype__typecode="Báo giữ lương"
            )
            return AdvanceRequestSerializer(qs_baogiu,many=True).data
        except Exception as e:
            print(f"{e}")
            return []
    def get_thamnien(self, qs):
        return None
    def get_work(self, qs):
        qs_work=OperatorWorkHistory.objects.filter(operator=qs)
        return OP_HISTSerializer(qs_work,many=True).data
    class Meta:
        model = CompanyOperator
        fields = '__all__'
        
class CompanyOperatorDetailsSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    work = serializers.SerializerMethodField(read_only=True)
    congty_danglam = serializers.SerializerMethodField(read_only=True)
    nhachinh = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    thamnien = serializers.SerializerMethodField(read_only=True)
    def get_thamnien(self, obj):
        def calculate_seniority(record):
            if not record.start_date:
                return 0
            start_date = record.start_date
            end_date = record.end_date or now().date()
            delta_days = (end_date - start_date).days + 1
            if record.noihopdong:
                delta_days += calculate_seniority(record.noihopdong)
            return delta_days
        qs_history=OperatorWorkHistory.objects.filter(operator=obj).first()
        if qs_history:
            total_days = calculate_seniority(qs_history)
            return total_days
        else:
            return None
    
    def get_congty_danglam(self, qs):
        if qs.congty_danglam:
            return {
                "name":qs.congty_danglam.name,
                "fullname":qs.congty_danglam.fullname,
            }
    def get_vendor(self, qs):
        if qs.vendor:
            return {
                "name":qs.vendor.name,
                "fullname":qs.vendor.fullname,
            }
    def get_nhachinh(self, qs):
        if qs.nhachinh:
            return {
                "name":qs.nhachinh.name,
                "fullname":qs.nhachinh.fullname,
            }
    def get_work(self, qs):
        qs_work=OperatorWorkHistory.objects.filter(operator=qs)
        if len(qs_work)>0:
            return [OP_HISTSerializer(qs_work.first()).data]
        else:
            return []
    class Meta:
        model = CompanyOperator
        fields = '__all__'
 