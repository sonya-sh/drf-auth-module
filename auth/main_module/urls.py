from django.urls import path, re_path, include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, CustomPasswordResetViewSet, CustomRegistrationViewSet
from rest_framework import routers
from djoser.views import UserViewSet


router = routers.SimpleRouter()
router.register(r'users', CustomUserViewSet)
user_me_viewset = UserViewSet.as_view({
    'get': 'me',
    'put': 'me',
    'patch': 'me',
    'delete': 'me'
})
#urlpatterns = router.urls

urlpatterns = [
    #path('', include(router.urls)),

    #path('auth/', include('djoser.urls')),
    #path('auth/users/set_password_custom/', CustomUserViewSet.as_view({'post': 'set_password'}), name='set_password_custom'),
    path('auth/users/', CustomRegistrationViewSet.as_view({'post': 'create'}), name='create'),
    path('auth/users/activate/<uid>/<token>/', CustomRegistrationViewSet.as_view({'post': 'activation'}), name='activation'),
    
    path('auth/users/resend_activate/', CustomRegistrationViewSet.as_view({'post': 'resend_activation'}), name='resend_activation'),

    path('auth/users/me/', user_me_viewset, name='user-me'),

    path('auth/users/set_password/', UserViewSet.as_view({'post': 'set_password'}), name='set_password'),
    path('auth/users/reset_password/', CustomPasswordResetViewSet.as_view({'post': 'reset_password'}), name='reset_password'),
    path('auth/users/reset_password/confirm/<uid>/<token>/', CustomPasswordResetViewSet.as_view({'post': 'reset_password_confirm'}), name='reset_password_confirm'),
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('userslist/', CustomUserListAPIView.as_view()),

    ]
