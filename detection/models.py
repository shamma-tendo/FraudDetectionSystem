from django.db import models
from transactions.models import Account, Transaction


class AccountBehaviorProfile(models.Model):
    """Stores recent behavior patterns for an account to compare against new transactions."""

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="behavior_profile")
    average_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    common_location = models.CharField(max_length=100, blank=True)
    common_hour = models.PositiveSmallIntegerField(null=True, blank=True)
    transaction_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Behavior profile for {self.account}"


class DetectionRule(models.Model):
    """
    A single fraud-detection rule, e.g. 'high amount' or 'unusual location'.
    Rules are stored as data (not hardcoded logic) so thresholds can be tuned
    live from the Django admin without touching code.
    """

    class RuleCode(models.TextChoices):
        HIGH_AMOUNT = "HIGH_AMOUNT", "Amount above threshold"
        VELOCITY = "VELOCITY", "Too many transactions in a short window"
        UNUSUAL_LOCATION = "UNUSUAL_LOCATION", "Location differs from account history"
        ODD_HOURS = "ODD_HOURS", "Transaction during odd hours"
        BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY", "Transaction differs from recent account behavior"

    code = models.CharField(max_length=30, choices=RuleCode.choices, unique=True)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    weight = models.PositiveSmallIntegerField(
        default=25, help_text="Points added to risk_score when this rule fires"
    )

    amount_threshold = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    velocity_window_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    velocity_max_count = models.PositiveSmallIntegerField(null=True, blank=True)
    odd_hours_start = models.PositiveSmallIntegerField(null=True, blank=True)
    odd_hours_end = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.description


class RuleMatch(models.Model):
    """Records which rule(s) fired for a given transaction, and why."""

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="rule_matches")
    rule = models.ForeignKey(DetectionRule, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rule.code} on {self.transaction_id}"
