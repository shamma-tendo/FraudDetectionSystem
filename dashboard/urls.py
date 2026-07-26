from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/<int:pk>/", views.transaction_detail, name="transaction_detail"),
    path("alerts/", views.alert_list, name="alert_list"),
    path("rules/", views.rules_list, name="rules_list"),
    path("accounts/", views.accounts_list, name="accounts_list"),
]