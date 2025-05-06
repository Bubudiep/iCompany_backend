from django.urls import path, include
from rest_framework import routers
from .views import *
from . import json

router = routers.DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
]