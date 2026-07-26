from django.contrib import admin
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "holder_name", "usual_location", "created_at")
    search_fields = ("account_number", "holder_name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "transaction_type", "amount", "location", "risk_score", "status", "timestamp")
    list_filter = ("status", "transaction_type")
    search_fields = ("account__account_number", "location")
