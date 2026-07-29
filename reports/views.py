from transactions.models import Transaction
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta


def weekly_report_dashboard(request):

    last_week = timezone.now() - timedelta(days=7)

    fraud_transactions = Transaction.objects.filter(
        status="FLAGGED",
        timestamp__gte=last_week
    )

    total_transactions = Transaction.objects.filter(
        timestamp__gte=last_week
    ).count()


    context = {
        "fraud_transactions": fraud_transactions,
        "total_transactions": total_transactions,
    }

    return render(
        request,
        "dashboard/weekly_report.html",
        context
    )