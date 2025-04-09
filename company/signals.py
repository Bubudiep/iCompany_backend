from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import *
from .serializers import *

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
    
@receiver(post_save, sender=Company)
def handle_transaction_save(sender, instance, created, **kwargs):
    if created:
        company = instance
        print(f"Đã tạo công ty: {company.name}")
        # Đăng ký app free
    else:
        print(f"User {company.name} đã được cập nhật.")

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
            