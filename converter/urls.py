"""
URL configuration for converter app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('convert-excel', views.ConvertExcelView.as_view(), name='convert-excel'),
    path('info', views.ServiceInfoView.as_view(), name='service-info'),
    path('health', views.HealthCheckView.as_view(), name='health-check'),
]
