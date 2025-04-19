from django.db import models, IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import time
import uuid
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
        # sio.connect('https://vieclamvp.vn/socket',
        # sio.connect('http://10.100.1.10/socket',
        sio.connect('http://localhost:5000',
            headers={
                'applicationkey': '@OAIIA3UHUIE21vczx@faWOOCS)=123SAF'
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

    print("Kết nối thành công sau khi thử lại!")

# Gọi hàm kết nối với retry
connect_with_retry()

# Tiếp tục với các thao tác tiếp theo nếu kết nối thành công
print("Tiến hành các thao tác tiếp theo sau khi kết nối thành công.")
