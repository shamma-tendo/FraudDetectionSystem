from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.contrib import messages

from transactions.models import Transaction, Account
from alerts.models import Alert
from detection.models import DetectionRule


@login_required
def dashboard_home(request):
    today = timezone.localdate()
    todays_transactions = Transaction.objects.filter(timestamp__date=today)

    stats = {
        "total_today": todays_transactions.count(),
        "flagged_today": todays_transactions.filter(status=Transaction.Status.FLAGGED).count(),
        "cleared_today": todays_transactions.filter(status=Transaction.Status.CLEARED).count(),
        "volume_today": todays_transactions.aggregate(total=Sum("amount"))["total"] or 0,
        "open_alerts": Alert.objects.filter(is_resolved=False).count(),
    }

    # Risk distribution for the chart: how many transactions land in each band.
    risk_bands = {
        "low (0-29)": Transaction.objects.filter(risk_score__lt=30).count(),
        "medium (30-59)": Transaction.objects.filter(risk_score__gte=30, risk_score__lt=60).count(),
        "high (60+)": Transaction.objects.filter(risk_score__gte=60).count(),
    }

    recent_transactions = Transaction.objects.select_related("account")[:12]
    open_alerts = (
        Alert.objects.filter(is_resolved=False)
        .select_related("transaction", "transaction__account")[:8]
    )

    latest_alert_id = Alert.objects.order_by("-id").values_list("id", flat=True).first() or 0

    return render(request, "dashboard/home.html", {
        "stats": stats,
        "risk_bands": risk_bands,
        "transactions": recent_transactions,
        "alerts": open_alerts,
        "latest_alert_id": latest_alert_id,
    })


@login_required
def transaction_list(request):
    qs = Transaction.objects.select_related("account").all()

    status = request.GET.get("status", "")
    txn_type = request.GET.get("type", "")
    search = request.GET.get("q", "")

    if status:
        qs = qs.filter(status=status)
    if txn_type:
        qs = qs.filter(transaction_type=txn_type)
    if search:
        qs = qs.filter(
            Q(account__account_number__icontains=search)
            | Q(account__holder_name__icontains=search)
            | Q(location__icontains=search)
        )

    return render(request, "dashboard/transaction_list.html", {
        "transactions": qs[:200],
        "status_choices": Transaction.Status.choices,
        "type_choices": Transaction.TransactionType.choices,
        "current_status": status,
        "current_type": txn_type,
        "current_search": search,
    })


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(
        Transaction.objects.select_related("account").prefetch_related("rule_matches__rule"), pk=pk
    )
    return render(request, "dashboard/transaction_detail.html", {"transaction": transaction})


@login_required
def alert_list(request):
    show_resolved = request.GET.get("show_resolved") == "1"
    qs = Alert.objects.select_related("transaction", "transaction__account")
    if not show_resolved:
        qs = qs.filter(is_resolved=False)
    return render(request, "dashboard/alert_list.html", {
        "alerts": qs,
        "show_resolved": show_resolved,
    })


@login_required
def resolve_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == "POST":
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, f"Alert #{alert.pk} marked resolved.")
    return redirect("dashboard:alert_list")


@login_required
def rules_list(request):
    rules = DetectionRule.objects.all()
    return render(request, "dashboard/rules_list.html", {"rules": rules})


@login_required
def accounts_list(request):
    accounts = Account.objects.annotate(txn_count=Count("transactions"))
    return render(request, "dashboard/accounts_list.html", {"accounts": accounts})


@login_required
def poll_alerts(request):
    """Polled every few seconds from the dashboard's JS for a live-feed feel."""
    since_id = request.GET.get("since", 0)
    new_alerts = list(
        Alert.objects.filter(id__gt=since_id, is_resolved=False)
        .select_related("transaction")
        .values("id", "severity", "message", "created_at", "transaction_id")
    )
    for a in new_alerts:
        a["created_at"] = a["created_at"].strftime("%H:%M:%S")
        a["transaction_id"] = str(a["transaction_id"])
    return JsonResponse({"alerts": new_alerts})

@login_required
def poll_overview(request):
    """
    Polled every few seconds from the Overview page so stat cards, the risk
    chart, and the recent-transactions table update live without a manual
    refresh — the counterpart to poll_alerts, which only handles the alert
    feed.
    """
    today = timezone.localdate()
    todays_transactions = Transaction.objects.filter(timestamp__date=today)

    stats = {
        "total_today": todays_transactions.count(),
        "flagged_today": todays_transactions.filter(status=Transaction.Status.FLAGGED).count(),
        "volume_today": float(todays_transactions.aggregate(total=Sum("amount"))["total"] or 0),
        "open_alerts": Alert.objects.filter(is_resolved=False).count(),
    }

    risk_bands = {
        "low": Transaction.objects.filter(risk_score__lt=30).count(),
        "medium": Transaction.objects.filter(risk_score__gte=30, risk_score__lt=60).count(),
        "high": Transaction.objects.filter(risk_score__gte=60).count(),
    }

    recent = Transaction.objects.select_related("account")[:12]
    transactions = [
        {
            "id": str(t.id),
            "account_number": t.account.account_number,
            "type_display": t.get_transaction_type_display(),
            "amount": float(t.amount),
            "location": t.location,
            "risk_score": t.risk_score,
            "status": t.status,
            "status_display": t.get_status_display(),
            "detail_url": reverse("dashboard:transaction_detail", args=[t.id]),
        }
        for t in recent
    ]

    return JsonResponse({"stats": stats, "risk_bands": risk_bands, "transactions": transactions})
