from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
# router.register(r'profile', UserProfileViewSet, basename='userprofile')
urlpatterns = [
    # path('s/order/', MemberOrder.as_view(), name='s_order'),
]