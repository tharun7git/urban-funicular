from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
from .views import UserViewSet, PhotoViewSet, FolderViewSet, test_api,add_photo_custom

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'folders', FolderViewSet, basename='folder')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('rest_framework.urls')),
    path('test/', test_api),  # This is correct if test_api is a function-based view
    path('addphoto/', add_photo_custom, name='add_photo_custom'),
]
