from django.db import models
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
# Kết nối tới server, gửi headers kèm theo
sio.connect('http://localhost:5000',
    headers={
      'applicationkey': '@OAIIA3UHUIE21vczx@faWOOCS)=123SAF'
    }
  )