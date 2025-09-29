from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'notes', UserNotesViewSet, basename='notes')
router.register(r'khachhang', NoteCustomerViewSet, basename='khachhang')
router.register(r'loaighichu', NoteTypeViewSet, basename='loaighichu')
router.register(r'profile', UserProfileViewSet, basename='profile')
urlpatterns = [
    path("user/", UserView.as_view()),
    path("changepass/", ChangePassView.as_view()),
    path("register/", NoteUserRegisterView.as_view()),
    path("login/", NoteUserLoginView.as_view()),
    path('', include(router.urls)),
]
