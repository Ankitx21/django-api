from django.db import models

class DailyEnergyPrediction(models.Model):
    date = models.DateField(unique=True)
    hour = models.IntegerField()
    energy_predicted = models.FloatField()
    energy_lowerbound = models.FloatField()

    class Meta:
        unique_together = ('date', 'hour')

    def __str__(self):
        return f"{self.date} - Hour {self.hour}"
# Create your models here.
