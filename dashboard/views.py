from django.shortcuts import render


def dashboard(request):

    context = {

        "total_transactions": 1245,

        "fraud_transactions": 43,

        "safe_transactions": 1202,

        "average_risk": 23,

    }


    return render(
        request,
        "dashboard/dashboard.html",
        context
    )