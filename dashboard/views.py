from django.shortcuts import render


def dashboard(request):

    transactions = [

        {
            "customer": "John Smith",
            "amount": 50000,
            "location": "Kampala",
            "risk": 15,
            "status": "Safe",
        },


        {
            "customer": "Sarah Johnson",
            "amount": 3500000,
            "location": "Dubai",
            "risk": 90,
            "status": "Fraud",
        },


        {
            "customer": "Michael Brown",
            "amount": 250000,
            "location": "Nairobi",
            "risk": 40,
            "status": "Review",
        },


        {
            "customer": "Grace Wilson",
            "amount": 75000,
            "location": "Kampala",
            "risk": 10,
            "status": "Safe",
        },

    ]

    alerts = [

    {
        "message": "High amount transaction detected",
        "severity": "High",
        "time": "2 mins ago"
    },

    {
        "message": "Transaction from unusual location",
        "severity": "Medium",
        "time": "7 mins ago"
    },

    {
        "message": "Multiple rapid transactions detected",
        "severity": "Critical",
        "time": "12 mins ago"
    },

    {
        "message": "Risk score exceeded threshold",
        "severity": "High",
        "time": "20 mins ago"
    }

]
    context = {

        "total_transactions": 1245,

        "fraud_transactions": 43,

        "safe_transactions": 1202,

        "average_risk": 23,

        "transactions": transactions,
          "alerts": alerts,
           # NEW — needed for the fraud-cases-per-day bar chart
    "weekly_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "weekly_fraud_counts": [3, 6, 2, 8, 5, 9, 4],  # replace with a real DB query, e.g. grouped by day

    }


    return render(
        request,
        "dashboard/home.html",
        context
    )


def home(request):
    return dashboard(request)


def transaction_list(request):
    return dashboard(request)


def transaction_detail(request, pk=None):
    return dashboard(request)


def alert_list(request):
    return dashboard(request)


def rules_list(request):
    return dashboard(request)


def accounts_list(request):
    return dashboard(request)