from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'files', UserFileViewSet, basename='userfiles')
router.register(r'apps', UserAppsViewSet, basename='userapps')
router.register(r's/news', StoreNewsViewSet, basename='s_news')
router.register(r's/feedbacks', StoreFeedbacksViewSet, basename='s_feedbacks')
router.register(r's/collabs', StoreCollabsViewSet, basename='s_collabs')
router.register(r's/slices', StoreSlidesViewSet, basename='s_slices')
router.register(r's/carts', MemberCartViewSet, basename='s_carts')
router.register(r's/products', StoreProductsViewSet, basename='s_products')
urlpatterns = [
    path('me/', MyInfo.as_view(), name='me'),
    path('login/', Login.as_view(), name='login'),
    path('zlogin/', ZaloMemberLogin.as_view(), name='zlogin'),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCD
# ADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU