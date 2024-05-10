from django import utils
from djoser import signals, utils
from djoser.conf import settings
from djoser.views import UserViewSet
from djoser.compat import get_user_email
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

#from rest_framework_simplejwt.tokens import RefreshToken
from .jwt_tokens.tokens import CustomRefreshToken, redis_client
from .models import CustomUser
from .serializers import *
from .tasks import send_reset_password_email_task, send_reset_password_confirmation_email_task, send_activation_email_task, send_confirmation_email_task


class CustomUserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserListSerializer
    permission_classes = (IsAuthenticated, )

# class LogoutAPIView(APIView):
#     permission_classes = (IsAuthenticated, )
#     def post(self, request):
#         try:
            
#             refresh_token = request.data.get('refresh')
#             RefreshToken(refresh_token).blacklist()
            
#             return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'detail': f'Error logging out: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class CustomRegistrationViewSet(UserViewSet):

    @staticmethod
    def notify_user_registration(user_id):
        redis_client.publish('user_registration', user_id)

    def get_email_context(self, user):
        site = get_current_site(self.request)
        return {
            'user': user.id,
            'domain': getattr(settings, 'DOMAIN', '') or site.domain,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'site_name': getattr(settings, 'SITE_NAME', '') or site.name
        }
    
    # обернуть в транзакцию?
    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = self.get_email_context(user)
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            #settings.EMAIL.activation(self.request, context).send(to)
            send_activation_email_task.delay(context, to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            #settings.EMAIL.confirmation(self.request, context).send(to)
            send_confirmation_email_task.delay(context, to)

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )
        refresh = CustomRefreshToken.for_user(user)
        access = refresh.access_token
        self.notify_user_registration(user.id)
        if settings.SEND_CONFIRMATION_EMAIL:
            user = serializer.user
            context = self.get_email_context(user)
            to = [get_user_email(user)]
            #settings.EMAIL.confirmation(self.request, context).send(to)
            send_confirmation_email_task.delay(context, to)

        return Response({
            'refresh': str(refresh),
            'access': str(access)
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user:
            context = get_user_email(user)
            to = [get_user_email(user)]
            #settings.EMAIL.activation(self.request, context).send(to)
            send_activation_email_task.delay(context, to)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomPasswordResetViewSet(UserViewSet):

    def get_email_context(self, user):
        site = get_current_site(self.request)
        return {
            'user': user.id,
            'domain': getattr(settings, 'DOMAIN', '') or site.domain,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'site_name': getattr(settings, 'SITE_NAME', '') or site.name
        }
    
    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = self.get_email_context(user)
            to = [get_user_email(user)]
            send_reset_password_email_task.delay(context, to)
            #settings.EMAIL.password_reset(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            user = serializer.user
            context = self.get_email_context(user)
            to = [get_user_email(user)]
            send_reset_password_confirmation_email_task.delay(context, to)
            
            #settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)