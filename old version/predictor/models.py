from django.db import models
from django.utils import timezone


class PredictionRecord(models.Model):
    """Stores every prediction made through the web app."""

    # Patient inputs
    pregnancies    = models.IntegerField()
    glucose        = models.FloatField()
    blood_pressure = models.FloatField()
    skin_thickness = models.FloatField()
    insulin        = models.FloatField()
    bmi            = models.FloatField()
    dpf            = models.FloatField(verbose_name="Diabetes Pedigree Function")
    age            = models.IntegerField()

    # Prediction outputs
    prediction     = models.CharField(max_length=20)
    confidence     = models.FloatField()
    risk_level     = models.CharField(max_length=10)

    created_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Prediction Record"

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.prediction} ({self.confidence}%)"
