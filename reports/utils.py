from datetime import date, timedelta
from django.db.models import Sum

from transactions.models import Transaction
from .models import WeeklyReport



def generate_weekly_report():

    today = date.today()

    week_start = today - timedelta(days=7)
    week_end = today


    transactions = Transaction.objects.filter(
        timestamp__date__range=[
            week_start,
            week_end
        ]
    )


    total_transactions = transactions.count()


    fraudulent = transactions.filter(
        status="fraud"
    )


    fraudulent_transactions = fraudulent.count()


    total_amount = transactions.aggregate(
        Sum("amount")
    )["amount__sum"] or 0


    fraud_amount = fraudulent.aggregate(
        Sum("amount")
    )["amount__sum"] or 0



    report = WeeklyReport.objects.create(

        week_start=week_start,

        week_end=week_end,

        total_transactions=total_transactions,

        fraudulent_transactions=fraudulent_transactions,

        total_amount=total_amount,

        fraud_amount=fraud_amount
    )


    return report