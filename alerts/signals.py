from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from transactions.models import Transaction
from .models import Alert


@receiver(post_save, sender=Transaction)
def create_alert_when_flagged(sender, instance, created, **kwargs):
    if instance.status == Transaction.Status.FLAGGED and not hasattr(instance, "alert"):

        alert = Alert.objects.create(
            transaction=instance,
            severity=Alert.severity_for_score(instance.risk_score),
            message=(
                f"Flagged {instance.transaction_type.lower()} of "
                f"{instance.amount} UGX on account {instance.account.account_number}"
            ),
        )

        # ✅ EMAIL GOES HERE (inside function)
        send_mail(
            subject="🚨 Fraud Alert Detected",
            message=(
                f"Suspicious transaction detected:\n\n"
                f"Amount: {instance.amount} UGX\n"
                f"Risk Score: {instance.risk_score}\n"
                f"Account: {instance.account.account_number}"
            ),
            from_email="noreply@yourapp.com",
            recipient_list=["admin@example.com"],
            fail_silently=True,
        )