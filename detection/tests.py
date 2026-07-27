from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from detection.models import DetectionRule, RuleMatch
from transactions.models import Account, Transaction
from .services import evaluate_transaction


class BehavioralAnomalyDetectionTests(TestCase):
    def test_detects_unusual_amount_and_location_for_account_history(self):
        account = Account.objects.create(
            account_number="ACC-1001",
            holder_name="Jane Doe",
            usual_location="Kampala",
        )

        for amount in [1000, 1200, 1100]:
            Transaction.objects.create(
                account=account,
                transaction_type=Transaction.TransactionType.PAYMENT,
                amount=Decimal(amount),
                location="Kampala",
                counterparty="Shop",
            )

        rule = DetectionRule.objects.create(
            code=DetectionRule.RuleCode.BEHAVIORAL_ANOMALY,
            description="Transaction differs from recent account behavior",
            is_active=True,
            weight=40,
        )

        new_transaction = Transaction.objects.create(
            account=account,
            transaction_type=Transaction.TransactionType.PAYMENT,
            amount=Decimal("5000"),
            location="Nairobi",
            counterparty="Shop",
        )

        score = evaluate_transaction(new_transaction)

        self.assertGreaterEqual(score, rule.weight)
        self.assertTrue(RuleMatch.objects.filter(transaction=new_transaction, rule=rule).exists())
