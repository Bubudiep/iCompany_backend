from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import *
@receiver(post_save, sender=UserProfile)
def handle_transaction_save(sender, instance, created, **kwargs):
    if created:
        user = instance
        print(f"Đã tạo user: {user.full_name}")
    else:
        print(f"User {instance.user.username} đã được cập nhật.")


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
            "functions": [
                {"code": "chat_send", "name": "Gửi tin nhắn"},
                {"code": "chat_history", "name": "Xem lịch sử"},
                {"code": "chat_group", "name": "Tạo nhóm chat"},
                {"code": "chat_setting", "name": "Cài đặt chat"},
            ]
        },
        {
            "appID": "app_booking",
            "name": "Đặt lịch",
            "description": "Đặt lịch hẹn",
            "isActive": True,
            "functions": [
                {"code": "booking_create", "name": "Tạo lịch hẹn"},
                {"code": "booking_cancel", "name": "Hủy lịch"},
                {"code": "booking_reminder", "name": "Nhắc nhở"},
            ]
        },
        {
            "appID": "app_dashboard",
            "name": "Tổng quan",
            "description": "Tổng quan",
            "isActive": True,
            "functions": [
                {"code": "dashboard_view", "name": "Xem báo cáo"},
            ]
        },
        {
            "appID": "app_staff",
            "name": "Nhân viên",
            "description": "Quản lý danh sách nhân viên và phòng ban, sơ đồ tổ chức",
            "isActive": True,
            "functions": [
                {"code": "staff_list", "name": "Danh sách nhân viên"},
                {"code": "staff_department", "name": "Quản lý phòng ban"},
                {"code": "staff_chart", "name": "Sơ đồ tổ chức"},
            ]
        },
        {
            "appID": "app_setting",
            "name": "Cài đặt",
            "description": "Cấu hình công ty",
            "isActive": True,
            "functions": [
                {"code": "setting_company", "name": "Thông tin công ty"},
                {"code": "setting_permissions", "name": "Phân quyền"},
            ]
        },
        {
            "appID": "app_ticketapproval",
            "name": "Phê duyệt",
            "description": "Phê duyệt hạng mục",
            "isActive": True,
            "functions": [
                {"code": "approval_ticket", "name": "Phê duyệt phiếu"},
                {"code": "approval_history", "name": "Lịch sử phê duyệt"},
            ]
        },
    ]

    for app_data in default_apps:
        app_obj, _ = MiniApp.objects.get_or_create(appID=app_data["appID"], defaults={
            "name": app_data["name"],
            "description": app_data["description"],
            "isActive": app_data["isActive"]
        })

        for func_data in app_data.get("functions", []):
            MiniAppFunction.objects.get_or_create(
                mini_app=app_obj,
                code=func_data["code"],
                defaults={
                    "name": func_data["name"],
                    "description": func_data.get("description", "")
                }
            )