from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import time
from rest_framework import exceptions
import uuid
from django.db.models import Q,F
from decouple import config
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

# Khởi tạo client
sio = socketio.Client()

# Sự kiện khi kết nối thành công
@sio.event
def connect():
    print("✅ Đã kết nối tới server")

# Nhận phản hồi từ server
@sio.on('chat_response')
def on_chat_response(data):
    print("📥 Server trả về:", data)

# Khi bị ngắt kết nối
@sio.event
def disconnect():
    print("❌ Mất kết nối")

# Kiểm tra kết nối trước khi kết nối
def check_connection():
    try:
        print(f"Kết nối tới {config('SOCKET')}")
        sio.connect(config('SOCKET'),
            headers={
                'applicationkey': config('SOCKET_KEY')
            })
        # Chờ một chút để xem kết nối có thành công không
        time_module.sleep(2)  # Chờ 2 giây

        if sio.connected:
            print("✅ Đã kết nối tới server.")
            return True
        else:
            print("❌ Không thể kết nối tới server.")
    except socketio.exceptions.ConnectionError as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False

# Kết nối lại nếu kết nối thất bại
def connect_with_retry():
    while not check_connection():
        print("⏳ Đang thử kết nối lại...")
        time_module.sleep(5)  # Chờ 5 giây trước khi thử lại

# Gọi hàm kết nối với retry
connect_with_retry()

# Tiếp tục với các thao tác tiếp theo nếu kết nối thành công
print("Tiến hành các thao tác tiếp theo sau khi kết nối thành công.")

def resize_base64_image(base64_str, size=(20, 20)):
    try:
        if base64_str.startswith('data:image'):
            header, base64_data = base64_str.split(',', 1)
        else:
            header = 'data:image/png;base64'
            base64_data = base64_str
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        image = image.convert("RGBA")
        image = image.resize(size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        resized_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"{header},{resized_base64}"
    except Exception as e:
        print(f"{e}")
        return None  # fallback nếu lỗi