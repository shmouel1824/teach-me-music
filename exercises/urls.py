from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('',              views.play,          name='play'),
    path('next-note/',    views.next_note,     name='next_note'),
    path('submit/',       views.submit_answer, name='submit'),
    path('reset/',        views.reset_session, name='reset'),
    path('bandit-stats/', views.bandit_stats,  name='bandit_stats'),
    path('reset-bandit/', views.reset_bandit,  name='reset_bandit'),
]