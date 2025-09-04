from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import time
from rest_framework import exceptions
import secrets
import uuid
from django.utils.timezone import make_aware, datetime
from django.utils.dateparse import parse_date
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import random
import string
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.db.models import F
import socketio
from django.core.exceptions import ObjectDoesNotExist
import time as time_module
from collections import defaultdict
from django.db.models import Count
import base64
from PIL import Image
from io import BytesIO
import difflib
import os, sys
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
import mimetypes


class Users(models.Model):
    oauth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        if not self.oauth_user:
            user = User.objects.create(
                username=f"vietz_user_{self.username}",
                password=self.password,
            )
            self.oauth_user = user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-id"]


class UserProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=[("male", "Nam"), ("female", "Nữ")], blank=True
    )
    avatar = models.TextField(blank=True, null=True)
    token = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        ordering = ["-id"]


class UserPlan(models.Model):
    name = models.CharField(
        max_length=100, unique=True
    )  # "Free", "Pro", "Enterprise"...
    max_storage_mb = models.IntegerField(default=300)
    max_apps = models.IntegerField(default=5)
    max_store = models.IntegerField(default=1)
    max_warehouse = models.IntegerField(default=1)
    max_categories = models.IntegerField(default=5)
    max_products = models.IntegerField(default=30)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]


class UserConfigs(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    plan = models.ForeignKey(UserPlan, on_delete=models.SET_NULL, null=True, blank=True)
    config = models.JSONField(default=dict, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Cấu hình của {self.user.username}"


class UserFile(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="uploads/viez/%Y/%m/%d/")
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # lưu theo byte
    file_type = models.CharField(max_length=100, blank=True)  # thêm trường này
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def save(self, *args, **kwargs):
        try:
            if self.file:  # Tự động lấy kích thước và tên file
                self.file_name = self.file.name
                self.file_size = self.file.size
                mime_type, _ = mimetypes.guess_type(self.file.name)
                if mime_type:
                    self.file_type = mime_type
                else:
                    self.file_type = (
                        os.path.splitext(self.file.name)[1].lower().replace(".", "")
                    )
            super().save(*args, **kwargs)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            print(f"{file_name}_{lineno}: {str(e)}")

    def __str__(self):
        return (
            f"{self.user.username} - {self.file_name} ({self.file_size / 1024:.1f} KB)"
        )

    def delete(self, *args, **kwargs):
        if self.file:
            if default_storage.exists(self.file.name):
                default_storage.delete(
                    self.file.name
                )  # Xoá file vật lý khi record bị xoá
        super().delete(*args, **kwargs)


def generate_app_id():
    while True:
        prefix = "170"
        suffix = "".join(str(random.randint(0, 9)) for _ in range(15))
        app_id = prefix + suffix
        if not UserApps.objects.filter(app_id=app_id).exists():
            return app_id


class AppCategorys(models.Model):
    name = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class UserApps(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_approve = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    category = models.ForeignKey(
        AppCategorys, on_delete=models.SET_NULL, null=True, blank=True
    )
    app_id = models.CharField(max_length=50, unique=True, default=generate_app_id)
    avatar = models.TextField(null=True, blank=True)
    descriptions = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Cấu hình của {self.user.username}"


class UserAppsConfigs(models.Model):
    app = models.ForeignKey(UserApps, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    configs = models.JSONField(default=dict, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Cấu hình của {self.app.name}"


class ProductsCategorys(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.category_name}"


class UserProducts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    danhmuc = models.ForeignKey(
        ProductsCategorys, on_delete=models.SET_NULL, null=True, blank=True
    )
    avatar = models.ForeignKey(
        UserFile, on_delete=models.SET_NULL, null=True, blank=True
    )
    product_name = models.CharField(max_length=50)
    info = models.CharField(max_length=225)
    descriptions = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.product_name}"


class UserProductsType(models.Model):
    product = models.ForeignKey(UserProducts, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    oldprice = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.product.product_name} {self.type_name}"


class Warehouse(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Area(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


class Rack(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


class Shelf(models.Model):
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name="shelves")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.rack} - {self.name}"


class Bin(models.Model):  # Ngăn trong kệ
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name="bins")
    name = models.CharField(max_length=50)  # Ví dụ: "Ngăn A", "Ngăn B"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.shelf} - {self.name}"


class UserStore(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    store_name = models.CharField(max_length=50, blank=True, null=True)
    store_logo = models.TextField(blank=True, null=True)
    store_collabs = models.TextField(blank=True, null=True)
    store_hotline = models.CharField(max_length=50, blank=True, null=True)
    descriptions = models.CharField(max_length=225, blank=True, null=True)
    preview_img = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.store_id:
            while True:
                new_id = uuid.uuid4().hex[:18]
                if not UserStore.objects.filter(store_id=new_id).exists():
                    self.store_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.store_name}"


class StoreMember(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    oauth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    username = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    zalo_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    last_login = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )
        if not self.oauth_user:
            user = User.objects.create(
                username=f"{self.store.store_id}_{self.zalo_id}",
                password=self.password,
            )
            self.oauth_user = user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.store.store_name} {self.username}"


class StoreNewsCtl(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    descriptions = models.CharField(max_length=225, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class StoreSlides(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True, null=True)
    short = models.CharField(max_length=225, blank=True, null=True)
    img_base64 = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"


class StoreCollabs(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=225, blank=True, null=True)
    img_base64 = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class StoreFeedbacks(models.Model):
    store = models.ForeignKey(
        UserStore, on_delete=models.CASCADE, blank=True, null=True
    )
    member = models.ForeignKey(
        StoreMember, on_delete=models.CASCADE, blank=True, null=True
    )

    image = models.TextField(blank=True, null=True)
    comment = models.CharField(max_length=50, blank=True, null=True)
    rate = models.IntegerField(default=5)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"


class StoreNews(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    image_base64 = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        StoreNewsCtl, on_delete=models.SET_NULL, blank=True, null=True
    )
    title = models.CharField(max_length=50, blank=True, null=True)
    short = models.CharField(max_length=225, blank=True, null=True)
    descriptions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"


class StoreProductsCtl(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    descriptions = models.CharField(max_length=225, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class StoreProducts(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    category = models.ManyToManyField(StoreProductsCtl, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    short = models.CharField(max_length=225, blank=True, null=True)
    img_base64 = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0, blank=True, null=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    min_unit = models.IntegerField(default=1)
    unit = models.CharField(default="cái", max_length=20, blank=True, null=True)
    descriptions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"


class StoreSales(models.Model):
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    products = models.ManyToManyField(StoreProducts, blank=True)
    type = models.CharField(
        max_length=10,
        choices=[("percent", "Phần trăm"), ("price", "Giá")],
        default="price",
    )
    percent = models.IntegerField(default=0, blank=True, null=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    descriptions = models.TextField(max_length=5000, blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class MemberCart(models.Model):
    member = models.ForeignKey(StoreMember, on_delete=models.CASCADE)
    product = models.ForeignKey(StoreProducts, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.store.store_name} {self.username}"


class Order(models.Model):
    customer = models.ForeignKey(StoreMember, on_delete=models.CASCADE)
    store = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0)
    order_code = models.CharField(
        max_length=30, unique=True, editable=False, blank=True, null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Chờ xử lý"),
            ("processing", "Đang xử lý"),
            ("completed", "Hoàn thành"),
            ("cancelled", "Đã hủy"),
        ],
        default="pending",
    )
    note = models.TextField(blank=True, null=True)  # ghi chú
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_code:
            # Ví dụ: OD202408160001 (OD + ngày + random)
            today = timezone.now().strftime("%m%d")
            random = get_random_string(6).upper()
            self.order_code = f"DH-{today}-{random}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("StoreProducts", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)  # giá tại thời điểm mua
    subtotal = models.IntegerField(default=0)  # thành tiền

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    user = models.ForeignKey(
        StoreMember, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} bởi {self.user} lúc {self.created_at}"
