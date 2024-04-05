from celery import shared_task
from .email import PasswordResetEmail
from djoser.email import PasswordChangedConfirmationEmail, ActivationEmail, ConfirmationEmail
from .models import CustomUser
from datetime import datetime, timedelta
from pytz import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


@shared_task
def send_reset_password_email_task(context, to):
    try:
        user = CustomUser.objects.get(id=context.get('user'))
        context['user'] = user
        PasswordResetEmail(context=context).send(to)
    except Exception as exc:
        print(f"Failed to send reset password email: {exc}")


@shared_task
def send_reset_password_confirmation_email_task(context, to):
    try:
        user = CustomUser.objects.get(id=context.get('user'))
        context['user'] = user
        PasswordChangedConfirmationEmail(context=context).send(to)
    except Exception as exc:
        print(f"Failed: {exc}")


@shared_task
def send_activation_email_task(context, to):
    try:
        user = CustomUser.objects.get(id=context.get('user'))
        context['user'] = user
        ActivationEmail(context=context).send(to)
    except Exception as exc:
        print(f"Failed: {exc}")


@shared_task
def send_confirmation_email_task(context, to):
    try:
        user = CustomUser.objects.get(id=context.get('user'))
        context['user'] = user
        ConfirmationEmail(context=context).send(to)
    except Exception as exc:
        print(f"Failed: {exc}")

