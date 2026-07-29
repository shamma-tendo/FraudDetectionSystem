from django.db import models


class WeeklyReport(models.Model):
    week_start = models.DateField()
    week_end = models.DateField()

    total_transactions = models.IntegerField()
    fraudulent_transactions = models.IntegerField()

    total_amount = models.FloatField()
    fraud_amount = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Report {self.week_start} - {self.week_end}"