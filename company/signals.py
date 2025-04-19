from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from .models import *
from .serializers import *
import threading

_thread_locals = threading.local()
@receiver(post_save, sender=ChatMessage)
def handle_transaction_save(sender, instance, created, **kwargs):
    if created:
        # Cập nhật thời gian cuối có tin nhắn cho phòng chat
        instance.room.last_have_message_at = now()
        instance.room.save(update_fields=['last_have_message_at'])
        # Cập nhật hoặc tạo mới bản ghi ChatDate
        chat_date,_ = ChatDate.objects.get_or_create(room=instance.room, date=now().date())
        chat_date.total_messages = F('total_messages') + 1
        chat_date.save(update_fields=['total_messages'])
        if instance.socket_sended==False:
            instance.socket_sended=True
            instance.save(update_fields=['socket_sended'])
            sio.emit('backend_event', {
                'type': 'chat_message',
                'room': AppChatRoomSerializer(instance.room).data,
                'data':  ChatMessageSerializer(instance).data,
                'key': instance.room.company.key
            })
    
@receiver(pre_save, sender=CompanyOperator)
def store_old_operator_data(sender, instance, **kwargs):
    if instance.pk:  # Chỉ lưu khi đã có trong DB
        try:
            old_instance = CompanyOperator.objects.get(pk=instance.pk)
            _thread_locals.old_operator_data = CompanyOperatorSerializer(old_instance).data
        except CompanyOperator.DoesNotExist:
            _thread_locals.old_operator_data = None
    else:
        _thread_locals.old_operator_data = None

# IGNORED_FIELDS = ["updated_at"]
# @receiver(post_save, sender=CompanyOperator)
# def handle_transaction_save(sender, instance, created, **kwargs):
#     current_data = CompanyOperatorSerializer(instance).data
#     old_data = getattr(_thread_locals, "old_operator_data", None)
#     qs_staff = CompanyStaff.objects.get(user__user=user,company=instance.company)
#     # Nếu là tạo mới thì lưu toàn bộ
#     if created or not old_data:
#         OperatorUpdateHistory.objects.create(
#             operator=instance,
#             old_data=None,
#             new_data=current_data,
#             notes="Khởi tạo tài khoản"
#         )
#     else:
#         # So sánh từng trường và chỉ lấy các trường thay đổi
#         changed_data = {
#             key: current_data[key]
#             for key in current_data
#             if key not in IGNORED_FIELDS and old_data.get(key) != current_data.get(key)
#         }
#         if changed_data:  # Chỉ tạo lịch sử nếu có sự thay đổi
#             OperatorUpdateHistory.objects.create(
#                 operator=instance,
#                 old_data={k: old_data[k] for k in changed_data if k in old_data},
#                 new_data=changed_data,
#                 notes="Cập nhật thông tin tài khoản"
#             )
#     _thread_locals.old_operator_data = None

@receiver(post_save, sender=Company)
def handle_transaction_save(sender, instance, created, **kwargs):
    if created:
        company = instance
        print(f"Đã tạo công ty: {company.name}")
        if not User.objects.filter(username=f"{company.key}_admin").exists():
            user = User.objects.create(username=f"{company.key}_admin", password=make_password(uuid.uuid4().hex.upper()))
            staff = CompanyUser.objects.create(user=user, company=company, username="admin", password="1234")  # Có thể mã hóa password sau
            cstaff = CompanyStaff.objects.create(company=company, user=staff,cardID="Admin", isActive=True, isSuperAdmin=True, isAdmin=True)
            print(f"Tài khoản admin cho công ty {company.name} đã được tạo.")
        else:
            print(f"Tài khoản admin cho công ty {company.name} đã tồn tại.")
    else:
        print(f"Công ty {instance.name} đã được cập nhật.")

@receiver(post_save, sender=CompanyStaff)
def handle_transaction_save(sender, instance, created, **kwargs):
    staff = instance
    if created:
        # Tạo profile
        sio.emit('backend_event', {
            'type': 'user_created',
            'data':  CompanyStaffDetailsSerializer(instance).data,
            'key': instance.company.key
        })
        print(f"Đã tạo nhân viên: {staff.cardID}")
    else:
        print(f"{staff.cardID} đã được cập nhật.")
        
# Khởi tạo ban đầu
@receiver(post_migrate)
def create_default_miniapps(sender, **kwargs):
    print("🚀 Signal chạy: tạo miniapps mặc định...")
    if sender.name != 'company':  # thay bằng tên app của bạn
        return
    default_apps = [
        {
            "appID": "app_chat",
            "name": "Chat",
            "description": "Ứng dụng chat giữa người dùng",
            "isActive": True,
            "public": True,
            "functions": [
                {"code": "chat_send","public": True, "name": "Gửi tin nhắn"},
                {"code": "chat_history","public": True, "name": "Xem lịch sử"},
                {"code": "chat_group","public": True, "name": "Tạo nhóm chat"},
                {"code": "chat_setting","public": True, "name": "Cài đặt chat"},
            ]
        },
        {
            "appID": "app_booking",
            "name": "Đặt lịch",
            "description": "Đặt lịch hẹn",
            "isActive": True,
            "public": True,
            "functions": [
                {"code": "booking_create", "public": True, "name": "Tạo lịch hẹn"},
                {"code": "booking_cancel", "public": True, "name": "Hủy lịch"},
                {"code": "booking_reminder", "public": True, "name": "Nhắc nhở"},
            ]
        },
        {
            "appID": "app_dashboard",
            "name": "Tổng quan",
            "description": "Tổng quan",
            "public": True,
            "isActive": True,
            "functions": [
                {"code": "dashboard_view", "public": True, "name": "Xem báo cáo"},
            ]
        },
        {
            "appID": "app_staff",
            "name": "Nhân viên",
            "public": True,
            "description": "Quản lý danh sách nhân viên và phòng ban, sơ đồ tổ chức",
            "isActive": True,
            "functions": [
                {"code": "staff_list", "public": True, "name": "Danh sách nhân viên"},
                {"code": "staff_department", "public": True, "name": "Quản lý phòng ban"},
                {"code": "staff_chart", "public": True, "name": "Sơ đồ tổ chức"},
            ]
        },
        {
            "appID": "app_setting",
            "name": "Cài đặt",
            "description": "Cấu hình công ty",
            "isActive": True,
            "public": True,
            "functions": [
                {"code": "setting_company", "public": True, "name": "Thông tin công ty"},
                {"code": "setting_permissions", "public": True, "name": "Phân quyền"},
            ]
        },
        {
            "appID": "app_ticketapproval",
            "name": "Phê duyệt",
            "public": True,
            "description": "Phê duyệt hạng mục",
            "isActive": True,
            "functions": [
                {"code": "approval_ticket", "public": True, "name": "Phê duyệt phiếu"},
                {"code": "approval_history", "public": True, "name": "Lịch sử phê duyệt"},
            ]
        },
    ]

    for app_data in default_apps:
        app_obj, _ = MiniApp.objects.update_or_create(appID=app_data["appID"], defaults={
            "name": app_data["name"],
            "description": app_data["description"],
            "isActive": app_data["isActive"],
            "public": app_data["public"]
        })

        for func_data in app_data.get("functions", []):
            MiniAppFunction.objects.update_or_create(
                mini_app=app_obj,
                code=func_data["code"],
                defaults={
                    "name": func_data["name"],
                    "public": func_data["public"],
                    "description": func_data.get("description", "")
                }
            )
            