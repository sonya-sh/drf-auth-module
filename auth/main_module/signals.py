from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from rest_framework_simplejwt.tokens import RefreshToken
from django.dispatch import Signal

password_changed = Signal()


@receiver(password_changed)
def invalidate_refresh_token_on_password_change(sender, request, user, **kwargs):
    user = kwargs['user']
    refresh_token = refresh_token = request.data.get('refresh')
    
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            pass