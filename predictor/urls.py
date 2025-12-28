from django.urls import path
from . import views, api_views

app_name = 'predictor'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('predict/', views.PredictView.as_view(), name='predict'),
    path('result/<int:prediction_id>/', views.ResultView.as_view(), name='result'),
    path('history/', views.HistoryView.as_view(), name='history'),
    
    # Legacy API endpoints
    path('api/weather/', views.APIWeatherView.as_view(), name='api_weather'),
    
    # Advanced API endpoints
    path('api/v1/predict/', api_views.WeatherPredictionAPI.as_view(), name='api_predict'),
    path('api/v1/history/', api_views.PredictionHistoryAPI.as_view(), name='api_history'),
    path('api/v1/stats/', api_views.PredictionStatsAPI.as_view(), name='api_stats'),
    path('api/v1/health/', api_views.api_health_check, name='api_health'),
    path('api/v1/cities/autocomplete/', api_views.api_cities_autocomplete, name='api_autocomplete'),
    
    # Management actions
    path('delete/<int:prediction_id>/', views.delete_prediction, name='delete_prediction'),
    path('clear-all/', views.clear_all_predictions, name='clear_all'),
]