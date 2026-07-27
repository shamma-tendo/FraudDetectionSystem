from datetime import timedelta
from django.utils import timezone
from .models import Transaction, Alert, UserProfile, FraudRuleConfig

def evaluate_transaction(account_number, amount, location):
    # Fetch active configuration or use fallback defaults
    config = FraudRuleConfig.objects.first()
    max_amount = config.max_transaction_amount if config else 10000.00
    max_velocity = config.max_velocity_count if config else 5
    velocity_seconds = config.velocity_timeframe_seconds if config else 30

    reasons = []
    severity = 'LOW'

    # --- RULE 1: Dynamic High Amount Threshold ---
    if amount > max_amount:
        reasons.append(f"Amount exceeds threshold (${max_amount:,.2f})")
        severity = 'HIGH'

    # --- RULE 2: Dynamic High Velocity Check ---
    timeframe = timezone.now() - timedelta(seconds=velocity_seconds)
    recent_tx_count = Transaction.objects.filter(
        account_number=account_number,
        timestamp__gte=timeframe
    ).count()

    if recent_tx_count >= max_velocity:
        reasons.append(f"High velocity: {recent_tx_count + 1} transactions in {velocity_seconds}s")
        severity = 'HIGH'

    # --- RULE 3: Location Anomaly ---
    profile = UserProfile.objects.filter(account_number=account_number).first()
    if profile and profile.home_country.lower() != location.lower():
        reasons.append(f"Location anomaly: Transaction in '{location}', home is '{profile.home_country}'")
        if severity != 'HIGH':
            severity = 'MEDIUM'

    # --- Save Transaction & Alert ---
    is_flagged = len(reasons) > 0
    flag_reason_str = " | ".join(reasons) if is_flagged else ""

    transaction = Transaction.objects.create(
        account_number=account_number,
        amount=amount,
        location=location,
        is_suspicious=is_flagged,
        flag_reason=flag_reason_str
    )

    if is_flagged:
        Alert.objects.create(
            transaction=transaction,
            rule_triggered=flag_reason_str,
            severity=severity
        )

    return transaction