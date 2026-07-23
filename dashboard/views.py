from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from transactions.models import Transaction
from alerts.models import Alert


@login_required
def dashboard_home(request):
    recent_transactions = Transaction.objects.select_related("account")[:25]
    open_alerts = Alert.objects.filter(is_resolved=False).select_related(
        "transaction", "transaction__account"
    )[:25]
    stats = {
        "total_today": Transaction.objects.count(),  # tighten with a date filter later
        "flagged_count": Transaction.objects.filter(
            status=Transaction.Status.FLAGGED
        ).count(),
        "open_alerts": open_alerts.count(),
    }
    return render(
        request,
        "dashboard/home.html",
        {
            "transactions": recent_transactions,
            "alerts": open_alerts,
            "stats": stats,
        },
    )


@login_required
def poll_alerts(request):
    """
    Polled every few seconds from the dashboard's JS (see home.html).
    ?since=<alert_id> returns only alerts newer than that ID, so the
    frontend can append rather than re-render the whole table.
    """
    since_id = request.GET.get("since", 0)
    new_alerts = Alert.objects.filter(id__gt=since_id, is_resolved=False).values(
        "id", "severity", "message", "created_at"
    )
    return JsonResponse({"alerts": list(new_alerts)})
