"""
The anomaly detection engine.

Kept as plain functions (not tied to signals or views) so your group can
unit test it directly: build_transaction with fake data, call
evaluate_transaction, assert on the resulting risk_score.
"""

from datetime import timedelta
from django.utils import timezone

from transactions.models import Transaction
from .models import DetectionRule, RuleMatch

FLAG_THRESHOLD = 60  # risk_score at/above this marks the transaction as FLAGGED


def evaluate_transaction(transaction: Transaction) -> int:
    """
    Runs all active rules against a transaction, records matches,
    updates risk_score and status, and returns the final score.
    """
    total_score = 0
    active_rules = DetectionRule.objects.filter(is_active=True)

    for rule in active_rules:
        fired, note = _check_rule(rule, transaction)
        if fired:
            total_score += rule.weight
            RuleMatch.objects.create(transaction=transaction, rule=rule, note=note)

    transaction.risk_score = min(total_score, 100)
    transaction.status = (
        Transaction.Status.FLAGGED
        if transaction.risk_score >= FLAG_THRESHOLD
        else Transaction.Status.CLEARED
    )
    transaction.save(update_fields=["risk_score", "status"])
    return transaction.risk_score


def _check_rule(rule: DetectionRule, transaction: Transaction):
    if rule.code == DetectionRule.RuleCode.HIGH_AMOUNT:
        return _check_high_amount(rule, transaction)
    if rule.code == DetectionRule.RuleCode.VELOCITY:
        return _check_velocity(rule, transaction)
    if rule.code == DetectionRule.RuleCode.UNUSUAL_LOCATION:
        return _check_unusual_location(rule, transaction)
    if rule.code == DetectionRule.RuleCode.ODD_HOURS:
        return _check_odd_hours(rule, transaction)
    return False, ""


def _check_high_amount(rule, transaction):
    if rule.amount_threshold is None:
        return False, ""
    if transaction.amount >= rule.amount_threshold:
        return True, f"Amount {transaction.amount} >= threshold {rule.amount_threshold}"
    return False, ""


def _check_velocity(rule, transaction):
    if not rule.velocity_window_minutes or not rule.velocity_max_count:
        return False, ""
    window_start = transaction.timestamp - timedelta(minutes=rule.velocity_window_minutes)
    recent_count = Transaction.objects.filter(
        account=transaction.account,
        timestamp__gte=window_start,
        timestamp__lte=transaction.timestamp,
    ).count()
    if recent_count > rule.velocity_max_count:
        return True, f"{recent_count} transactions in {rule.velocity_window_minutes} min window"
    return False, ""


def _check_unusual_location(rule, transaction):
    usual = transaction.account.usual_location.strip().lower()
    current = transaction.location.strip().lower()
    if usual and current and usual != current:
        return True, f"Usual location '{usual}' differs from '{current}'"
    return False, ""


def _check_odd_hours(rule, transaction):
    if rule.odd_hours_start is None or rule.odd_hours_end is None:
        return False, ""
    local_hour = timezone.localtime(transaction.timestamp).hour
    start, end = rule.odd_hours_start, rule.odd_hours_end
    # Handles ranges that wrap past midnight, e.g. 1am - 4am
    if start <= end:
        in_window = start <= local_hour < end
    else:
        in_window = local_hour >= start or local_hour < end
    if in_window:
        return True, f"Transaction at {local_hour}:00 falls in odd-hours window"
    return False, ""
