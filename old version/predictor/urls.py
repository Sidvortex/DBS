from django.urls import path
from . import views  # ✅ Correct import from `predictor`

urlpatterns = [
    path('index/', views.index, name='index'),  # ✅ Make sure `index()` exists in `views.py`
]
