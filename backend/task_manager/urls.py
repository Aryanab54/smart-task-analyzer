from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_tasks, name='analyze_tasks'),
    path('suggest/', views.suggest_tasks, name='suggest_tasks'),
    path('add/', views.add_task_to_suggestions, name='add_task'),
]