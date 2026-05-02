from django.db import models
from django.utils import timezone

class PredictionRecord(models.Model):
    DISEASE_CHOICES = [('diabetes','Diabetes'),('heart','Heart Disease')]

    disease        = models.CharField(max_length=20, choices=DISEASE_CHOICES, default='diabetes')
    prediction     = models.CharField(max_length=30)
    confidence     = models.FloatField()
    risk_level     = models.CharField(max_length=10)

    # Shared
    age            = models.IntegerField()

    # Diabetes fields (nullable so heart records work too)
    pregnancies    = models.IntegerField(null=True, blank=True)
    glucose        = models.FloatField(null=True, blank=True)
    blood_pressure = models.FloatField(null=True, blank=True)
    skin_thickness = models.FloatField(null=True, blank=True)
    insulin        = models.FloatField(null=True, blank=True)
    bmi            = models.FloatField(null=True, blank=True)
    dpf            = models.FloatField(null=True, blank=True)

    # Heart fields (nullable)
    sex            = models.IntegerField(null=True, blank=True)
    cp             = models.IntegerField(null=True, blank=True)
    trestbps       = models.FloatField(null=True, blank=True)
    chol           = models.FloatField(null=True, blank=True)
    fbs            = models.IntegerField(null=True, blank=True)
    restecg        = models.IntegerField(null=True, blank=True)
    thalach        = models.FloatField(null=True, blank=True)
    exang          = models.IntegerField(null=True, blank=True)
    oldpeak        = models.FloatField(null=True, blank=True)
    slope          = models.IntegerField(null=True, blank=True)
    ca             = models.IntegerField(null=True, blank=True)
    thal           = models.IntegerField(null=True, blank=True)

    created_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.disease}] {self.prediction} ({self.confidence}%)"
