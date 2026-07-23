from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Transaction
from .services import evaluate_transaction


@receiver(post_save, sender=Transaction)
def run_detection_on_new_transaction(sender, instance, created, **kwargs):
    """
    Runs the rule engine the moment a transaction is saved for the first time.
    This is what makes the system feel 'real-time': no separate cron job or
    button click is needed, screening happens inline with transaction creation.
    """
    if created:
        evaluate_transaction(instance)
