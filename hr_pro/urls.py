from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'posts', BaivietViewSet, basename='baiviet')
urlpatterns = [
    path("user/", UserView.as_view()),
    path("in/", LoginView.as_view()),
    path('', include(router.urls)),
]
