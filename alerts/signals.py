from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Transaction
from .models import Alert


@receiver(post_save, sender=Transaction)
def create_alert_when_flagged(sender, instance, created, **kwargs):
    # Runs after detection.signals has already scored the transaction, since
    # Django processes receivers in the order their apps were registered
    # (make sure 'detection' comes before 'alerts' in INSTALLED_APPS).
    if instance.status == Transaction.Status.FLAGGED and not hasattr(instance, "alert"):
        Alert.objects.create(
            transaction=instance,
            severity=Alert.severity_for_score(instance.risk_score),
            message=(
                f"Flagged {instance.transaction_type.lower()} of "
                f"{instance.amount} on account {instance.account.account_number}"
            ),
        )
