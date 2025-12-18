from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'posts', BaivietViewSet, basename='baiviet')
router.register(r'ips', KhuCongNghiepViewSet, basename='ips')
router.register(r'comp', CompanyListsViewSet, basename='comp')
router.register(r'tag', BaivietTuyendungTagsViewSet, basename='tag')
router.register(r'tin', BaivietTuyendungViewSet, basename='tin')
router.register(r'slice', AnhSliceViewSet, basename='slice')
urlpatterns = [
    path("user/", UserView.as_view()),
    path("in/", LoginView.as_view()),
    path("reg/", DangkyView.as_view()),
    path('', include(router.urls)),
]
