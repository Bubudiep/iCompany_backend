from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'notes', UserNotesViewSet, basename='notes')
urlpatterns = [
    path("user/", UserView.as_view()),
    path("register/", NoteUserRegisterView.as_view()),
    path("login/", NoteUserLoginView.as_view()),
    path('', include(router.urls)),
]
