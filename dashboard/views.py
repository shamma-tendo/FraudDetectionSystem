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


    context = {

        "total_transactions": 1245,

        "fraud_transactions": 43,

        "safe_transactions": 1202,

        "average_risk": 23,

        "transactions": transactions,

    }


    return render(
        request,
        "dashboard/dashboard.html",
        context
    )