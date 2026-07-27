from django.conf import settings
from django.db import models
from transactions.models import Transaction


class Alert(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"


    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="alert")
    severity = models.CharField(max_length=10, choices=Severity.choices)
    message = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity}] {self.message}"

    @staticmethod
    def severity_for_score(risk_score: int) -> str:
        if risk_score >= 85:
            return Alert.Severity.HIGH
        if risk_score >= 60:
            return Alert.Severity.MEDIUM
        return Alert.Severity.LOW
