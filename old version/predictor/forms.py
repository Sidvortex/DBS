from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class DiabetesForm(forms.Form):
    pregnancies = forms.IntegerField(
        label='Pregnancies',
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        widget=forms.NumberInput(attrs={'placeholder': '0–20', 'class': 'form-control', 'min': 0, 'max': 20}),
        help_text="Number of times pregnant (0–20)"
    )
    glucose = forms.FloatField(
        label='Glucose (mg/dL)',
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        widget=forms.NumberInput(attrs={'placeholder': '70–200', 'class': 'form-control', 'min': 0, 'max': 300, 'step': '0.1'}),
        help_text="Plasma glucose concentration (0 = unknown, will use dataset mean)"
    )
    blood_pressure = forms.FloatField(
        label='Blood Pressure (mm Hg)',
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        widget=forms.NumberInput(attrs={'placeholder': '60–120', 'class': 'form-control', 'min': 0, 'max': 200, 'step': '0.1'}),
        help_text="Diastolic blood pressure (0 = unknown)"
    )
    skin_thickness = forms.FloatField(
        label='Skin Thickness (mm)',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'placeholder': '0–99', 'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.1'}),
        help_text="Triceps skinfold thickness (0 = unknown)"
    )
    insulin = forms.FloatField(
        label='Insulin (mu U/ml)',
        validators=[MinValueValidator(0), MaxValueValidator(900)],
        widget=forms.NumberInput(attrs={'placeholder': '0–846', 'class': 'form-control', 'min': 0, 'max': 900, 'step': '0.1'}),
        help_text="2-Hour serum insulin (0 = unknown)"
    )
    bmi = forms.FloatField(
        label='BMI (kg/m²)',
        validators=[MinValueValidator(0), MaxValueValidator(70)],
        widget=forms.NumberInput(attrs={'placeholder': '18.5–45', 'class': 'form-control', 'min': 0, 'max': 70, 'step': '0.1'}),
        help_text="Body mass index (0 = unknown)"
    )
    dpf = forms.FloatField(
        label='Diabetes Pedigree Function',
        validators=[MinValueValidator(0.0), MaxValueValidator(3.0)],
        widget=forms.NumberInput(attrs={'placeholder': '0.0–2.5', 'class': 'form-control', 'min': 0, 'max': 3, 'step': '0.001'}),
        help_text="Genetic diabetes risk score based on family history"
    )
    age = forms.IntegerField(
        label='Age (years)',
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        widget=forms.NumberInput(attrs={'placeholder': '1–120', 'class': 'form-control', 'min': 1, 'max': 120}),
        help_text="Age in years"
    )
