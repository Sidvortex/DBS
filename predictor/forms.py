from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

W = {'class': 'mac-input'}

class DiabetesForm(forms.Form):
    pregnancies    = forms.IntegerField(label='Pregnancies',    validators=[MinValueValidator(0), MaxValueValidator(20)],  widget=forms.NumberInput(attrs={**W,'placeholder':'0–20','min':0,'max':20}),         help_text='Number of times pregnant (0–20)')
    glucose        = forms.FloatField(  label='Glucose (mg/dL)',validators=[MinValueValidator(0), MaxValueValidator(300)], widget=forms.NumberInput(attrs={**W,'placeholder':'70–200','step':'0.1'}),            help_text='Plasma glucose (0 = unknown)')
    blood_pressure = forms.FloatField(  label='Blood Pressure', validators=[MinValueValidator(0), MaxValueValidator(200)], widget=forms.NumberInput(attrs={**W,'placeholder':'60–120','step':'0.1'}),            help_text='Diastolic BP mm Hg (0 = unknown)')
    skin_thickness = forms.FloatField(  label='Skin Thickness', validators=[MinValueValidator(0), MaxValueValidator(100)], widget=forms.NumberInput(attrs={**W,'placeholder':'0–99','step':'0.1'}),              help_text='Triceps skinfold mm (0 = unknown)')
    insulin        = forms.FloatField(  label='Insulin (mu U/ml)',validators=[MinValueValidator(0),MaxValueValidator(900)],widget=forms.NumberInput(attrs={**W,'placeholder':'0–846','step':'0.1'}),             help_text='2-hr serum insulin (0 = unknown)')
    bmi            = forms.FloatField(  label='BMI (kg/m²)',    validators=[MinValueValidator(0), MaxValueValidator(70)],  widget=forms.NumberInput(attrs={**W,'placeholder':'18.5–45','step':'0.1'}),           help_text='Body mass index (0 = unknown)')
    dpf            = forms.FloatField(  label='Pedigree Function',validators=[MinValueValidator(0),MaxValueValidator(3)],  widget=forms.NumberInput(attrs={**W,'placeholder':'0.0–2.5','step':'0.001'}),         help_text='Diabetes pedigree function')
    age            = forms.IntegerField(label='Age (years)',    validators=[MinValueValidator(1), MaxValueValidator(120)], widget=forms.NumberInput(attrs={**W,'placeholder':'1–120'}),                          help_text='Age in years')

class HeartDiseaseForm(forms.Form):
    age      = forms.IntegerField(label='Age',            validators=[MinValueValidator(1),  MaxValueValidator(120)], widget=forms.NumberInput(attrs={**W,'placeholder':'28–80'}),           help_text='Age in years')
    sex      = forms.ChoiceField( label='Sex',            choices=[(1,'Male'),(0,'Female')],                          widget=forms.Select(attrs={**W}))
    cp       = forms.ChoiceField( label='Chest Pain Type',choices=[(0,'Typical Angina'),(1,'Atypical Angina'),(2,'Non-Anginal'),(3,'Asymptomatic')], widget=forms.Select(attrs={**W}),      help_text='Type of chest pain')
    trestbps = forms.FloatField(  label='Resting BP (mm Hg)',validators=[MinValueValidator(80),MaxValueValidator(200)],widget=forms.NumberInput(attrs={**W,'placeholder':'90–200','step':'1'}),help_text='Resting blood pressure')
    chol     = forms.FloatField(  label='Cholesterol (mg/dL)',validators=[MinValueValidator(100),MaxValueValidator(600)],widget=forms.NumberInput(attrs={**W,'placeholder':'120–400','step':'1'}),help_text='Serum cholesterol')
    fbs      = forms.ChoiceField( label='Fasting Blood Sugar > 120?', choices=[(0,'No'),(1,'Yes')], widget=forms.Select(attrs={**W}))
    restecg  = forms.ChoiceField( label='Resting ECG',    choices=[(0,'Normal'),(1,'ST-T Abnormality'),(2,'LV Hypertrophy')], widget=forms.Select(attrs={**W}))
    thalach  = forms.FloatField(  label='Max Heart Rate', validators=[MinValueValidator(60),MaxValueValidator(210)],   widget=forms.NumberInput(attrs={**W,'placeholder':'70–210','step':'1'}), help_text='Max heart rate achieved')
    exang    = forms.ChoiceField( label='Exercise Angina',choices=[(0,'No'),(1,'Yes')],                                widget=forms.Select(attrs={**W}),                                      help_text='Exercise-induced angina')
    oldpeak  = forms.FloatField(  label='ST Depression',  validators=[MinValueValidator(0), MaxValueValidator(7)],    widget=forms.NumberInput(attrs={**W,'placeholder':'0.0–6.2','step':'0.1'}),help_text='ST depression vs rest')
    slope    = forms.ChoiceField( label='ST Slope',       choices=[(0,'Upsloping'),(1,'Flat'),(2,'Downsloping')],     widget=forms.Select(attrs={**W}),                                      help_text='Peak exercise ST slope')
    ca       = forms.ChoiceField( label='Major Vessels',  choices=[(0,'0'),(1,'1'),(2,'2'),(3,'3')],                  widget=forms.Select(attrs={**W}),                                      help_text='Vessels coloured by fluoroscopy')
    thal     = forms.ChoiceField( label='Thalassemia',    choices=[(1,'Normal'),(2,'Fixed Defect'),(3,'Reversible Defect')], widget=forms.Select(attrs={**W}))
