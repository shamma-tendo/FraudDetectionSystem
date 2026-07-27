from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Transaction
from .services import evaluate_transaction


@receiver(post_save, sender=Transaction)
def run_detection_on_new_transaction(sender, instance, created, **kwargs):
    """Screens every new transaction the instant it's saved."""
    if created:
        evaluate_transaction(instance)
