from django.urls import path
from .views import weekly_report_dashboard


app_name = "reports"


urlpatterns = [
    path(
        "weekly/",
        weekly_report_dashboard,
        name="weekly_report"
    ),
]