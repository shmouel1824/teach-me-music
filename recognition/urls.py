from django.urls import path
from . import views

app_name = 'recognition'

urlpatterns = [
    path('recognize/', views.recognize_audio, name='recognize_audio'),
    path('warmup/',    views.warmup,          name='warmup'),
]