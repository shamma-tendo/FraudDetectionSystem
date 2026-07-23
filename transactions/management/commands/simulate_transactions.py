import random
import time
from decimal import Decimal

from django.core.management.base import BaseCommand
from transactions.models import Account, Transaction

LOCATIONS = ["Kampala", "Entebbe", "Jinja", "Mbarara", "Gulu", "Unknown (abroad)"]


class Command(BaseCommand):
    help = (
        "Continuously creates random transactions so the dashboard has "
        "something to react to during a live demo. Ctrl+C to stop."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval", type=float, default=3.0, help="Seconds between transactions"
        )
        parser.add_argument(
            "--count", type=int, default=0, help="Stop after N transactions (0 = run forever)"
        )

    def handle(self, *args, **options):
        accounts = list(Account.objects.all())
        if not accounts:
            self.stdout.write(self.style.ERROR(
                "No accounts found. Create some Account records first "
                "(via admin or a fixture) before running this command."
            ))
            return

        interval = options["interval"]
        limit = options["count"]
        created = 0

        self.stdout.write(self.style.SUCCESS("Simulating transactions... Ctrl+C to stop"))
        try:
            while limit == 0 or created < limit:
                account = random.choice(accounts)
                # Occasionally generate a suspicious transaction so the demo
                # actually produces flagged alerts, not just clean traffic.
                is_suspicious = random.random() < 0.2
                amount = (
                    Decimal(random.randint(5_000_000, 20_000_000))
                    if is_suspicious
                    else Decimal(random.randint(5_000, 500_000))
                )
                location = (
                    random.choice(LOCATIONS[-1:])
                    if is_suspicious
                    else account.usual_location
                )

                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=random.choice(
                        Transaction.TransactionType.values
                    ),
                    amount=amount,
                    location=location,
                )
                created += 1
                self.stdout.write(
                    f"Created {txn.id} - {amount} UGX - risk {txn.risk_score} - {txn.status}"
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nStopped."))
