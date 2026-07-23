import uuid
from django.db import models


class Account(models.Model):
    """A bank account or customer being monitored for fraud."""

    account_number = models.CharField(max_length=20, unique=True)
    holder_name = models.CharField(max_length=150)
    usual_location = models.CharField(
        max_length=100,
        help_text="Typical city/region this account transacts from, e.g. Kampala",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.holder_name}"


class Transaction(models.Model):
    """A single financial transaction that gets screened by the detection engine."""

    class TransactionType(models.TextChoices):
        TRANSFER = "TRANSFER", "Transfer"
        PAYMENT = "PAYMENT", "Payment"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        DEPOSIT = "DEPOSIT", "Deposit"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending review"
        CLEARED = "CLEARED", "Cleared"
        FLAGGED = "FLAGGED", "Flagged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, default=TransactionType.TRANSFER
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    location = models.CharField(
        max_length=100, help_text="City/region the transaction originated from"
    )
    counterparty = models.CharField(
        max_length=150, blank=True, help_text="Recipient or merchant, if applicable"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    risk_score = models.PositiveSmallIntegerField(
        default=0, help_text="0-100 score assigned by the detection engine"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["account", "timestamp"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.account.account_number}"
