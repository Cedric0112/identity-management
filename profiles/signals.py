from allauth.account.signals import email_confirmed
from django.contrib import messages
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from .models import DeletedAccountLog
from django.utils.safestring import mark_safe

@receiver(email_confirmed)
def activate_user_on_confirm(sender, request, email_address, **kwargs):
    user = email_address.user
    if not user.is_active:
        user.is_active = True
        user.save()

    # if request:
    #     messages.success(request, f"You have confirmed {email_address.email}.")

@receiver(user_logged_in)
def notify_staff_of_deletions(sender, user, request, **kwargs):
    if user.is_staff:
        logs = DeletedAccountLog.objects.all().order_by("-deleted_at")
        if logs.exists():
            request.session["staff_deletion_notices"] = [
                mark_safe(f"{log.username} has deleted their account.")
                for log in logs
            ]
            DeletedAccountLog.objects.all().delete()
