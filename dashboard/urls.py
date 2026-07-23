from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("poll-alerts/", views.poll_alerts, name="poll_alerts"),
]
