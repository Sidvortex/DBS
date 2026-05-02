from django.contrib import admin
from django.urls import path, include
from predictor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predictor/', include('predictor.urls')),
    path('', views.index, name='index'),  # Homepage
]
