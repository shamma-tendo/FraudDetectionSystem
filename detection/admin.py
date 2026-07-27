from django.contrib import admin
from .models import DetectionRule, RuleMatch


@admin.register(DetectionRule)
class DetectionRuleAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "is_active", "weight")
    list_editable = ("is_active", "weight")


@admin.register(RuleMatch)
class RuleMatchAdmin(admin.ModelAdmin):
    list_display = ("transaction", "rule", "note", "created_at")
    list_filter = ("rule",)
