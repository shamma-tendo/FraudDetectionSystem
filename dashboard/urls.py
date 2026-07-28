from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/<uuid:pk>/", views.transaction_detail, name="transaction_detail"),
    path("alerts/", views.alert_list, name="alert_list"),
    path("alerts/<int:pk>/resolve/", views.resolve_alert, name="resolve_alert"),
    path("rules/", views.rules_list, name="rules_list"),
    path("accounts/", views.accounts_list, name="accounts_list"),
    path("poll-alerts/", views.poll_alerts, name="poll_alerts"),
    path("poll-transactions/", views.poll_transactions, name="poll_transactions"), #new function for transaction  
    path("poll-stats/", views.poll_stats, name="poll_stats"),                       # NEW function for stats and charts
]
