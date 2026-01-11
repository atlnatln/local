# -*- coding: utf-8 -*-
"""
Bağ Evi Monitoring URL Configuration
Production monitoring endpoints
"""

from django.urls import path
from . import monitoring_views

app_name = 'bag_evi_monitoring'

urlpatterns = [
    path('health/', monitoring_views.bag_evi_health_check, name='health_check'),
    path('stats/', monitoring_views.bag_evi_performance_stats, name='performance_stats'),
    path('clear-cache/', monitoring_views.bag_evi_clear_cache, name='clear_cache'),
    path('clear-analytics/', monitoring_views.bag_evi_clear_analytics, name='clear_analytics'),
    path('system-info/', monitoring_views.bag_evi_system_info, name='system_info'),
]
