from django.shortcuts import render
from django.http import JsonResponse
from .forms import DiabetesForm
from .models import PredictionRecord
from . import ml_service


def index(request):
    result   = None
    form     = DiabetesForm()
    profiles = ml_service.get_risk_profiles(top_n=5)
    stats    = ml_service.get_dataset_stats()
    history  = PredictionRecord.objects.all()[:10]

    if request.method == "POST":
        form = DiabetesForm(request.POST)
        if form.is_valid():
            data   = form.cleaned_data
            result = ml_service.predict(data)

            # Save to database
            PredictionRecord.objects.create(
                pregnancies    = data['pregnancies'],
                glucose        = data['glucose'],
                blood_pressure = data['blood_pressure'],
                skin_thickness = data['skin_thickness'],
                insulin        = data['insulin'],
                bmi            = data['bmi'],
                dpf            = data['dpf'],
                age            = data['age'],
                prediction     = result['label'],
                confidence     = result['confidence'],
                risk_level     = result['risk_level'],
            )
            # Refresh history after new save
            history = PredictionRecord.objects.all()[:10]

    return render(request, "index.html", {
        "form":       form,
        "result":     result,
        "high_risk":  profiles['high_risk'],
        "low_risk":   profiles['low_risk'],
        "stats":      stats,
        "history":    history,
        "model_name": ml_service.MODEL_NAME,
        "model_acc":  ml_service.MODEL_ACCURACY,
    })
