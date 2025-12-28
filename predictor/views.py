from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
import json

from .models import Prediction
from .utils import WeatherMLPredictor, WeatherAPIClient, validate_city_input, format_weather_data_for_prediction, format_city_display


class HomeView(View):
    """
    Home page view with project introduction and features
    """
    
    def get(self, request):
        context = {
            'title': 'AI Weather Prediction System',
            'features': [
                {
                    'icon': 'fas fa-thermometer-half',
                    'title': 'Temperature Prediction',
                    'description': 'Advanced ML algorithms predict temperature trends with high accuracy'
                },
                {
                    'icon': 'fas fa-tint',
                    'title': 'Humidity Forecasting',
                    'description': 'Precise humidity level predictions for better planning'
                },
                {
                    'icon': 'fas fa-cloud-rain',
                    'title': 'Rain Prediction',
                    'description': 'Smart rain forecasting to help you stay prepared'
                }
            ]
        }
        return render(request, 'predictor/home.html', context)


class DashboardView(View):
    """
    Analytics dashboard with comprehensive insights
    """
    
    def get(self, request):
        # Get basic statistics
        total_predictions = Prediction.objects.count()
        unique_cities = Prediction.objects.values('city').distinct().count()
        
        # Recent predictions (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_predictions = Prediction.objects.filter(timestamp__gte=week_ago).count()
        
        # Top cities
        top_cities = Prediction.objects.values('city').annotate(
            count=Count('city'),
            avg_temp=Avg('predicted_temperature'),
            avg_humidity=Avg('predicted_humidity')
        ).order_by('-count')[:10]
        
        context = {
            'title': 'Analytics Dashboard',
            'total_predictions': total_predictions,
            'unique_cities': unique_cities,
            'recent_predictions': recent_predictions,
            'top_cities': top_cities,
        }
        return render(request, 'predictor/dashboard.html', context)


class PredictView(View):
    """
    Weather prediction form and processing view
    """
    
    def get(self, request):
        context = {
            'title': 'Weather Prediction'
        }
        return render(request, 'predictor/predict.html', context)
    
    def post(self, request):
        city = request.POST.get('city', '').strip()
        
        # Validate input
        if not validate_city_input(city):
            messages.error(request, 'Please enter a valid city name (letters only, minimum 2 characters)')
            return render(request, 'predictor/predict.html', {'title': 'Weather Prediction'})
        
        try:
            # Initialize API client and ML predictor
            api_client = WeatherAPIClient()
            ml_predictor = WeatherMLPredictor()
            
            # Fetch current weather data
            weather_data = api_client.get_current_weather(city)
            
            # Format data for ML prediction
            features = format_weather_data_for_prediction(weather_data)
            
            # Make ML predictions
            predictions = ml_predictor.predict_weather(features)
            
            # Save prediction to database
            prediction_record = Prediction.objects.create(
                city=weather_data['city'],
                min_temp=features['min_temp'],
                max_temp=features['max_temp'],
                wind_gust_speed=features['wind_gust_speed'],
                humidity=features['humidity'],
                pressure=features['pressure'],
                current_temp=features['current_temp'],
                predicted_temperature=predictions['temperature'],
                predicted_humidity=predictions['humidity'],
                predicted_rain=predictions['rain']
            )
            
            # Prepare context for results page
            city_info = format_city_display(weather_data['city'], weather_data['country'])
            
            context = {
                'title': 'Prediction Results',
                'city_info': city_info,
                'current_weather': weather_data,
                'predictions': predictions,
                'features': features,
                'prediction_id': prediction_record.id
            }
            
            messages.success(request, f'Weather prediction completed for {weather_data["city"]}!')
            return render(request, 'predictor/result.html', context)
            
        except Exception as e:
            error_message = str(e)
            if 'city not found' in error_message.lower():
                messages.error(request, f'City "{city}" not found. Please check the spelling and try again.')
            elif 'api' in error_message.lower():
                messages.error(request, 'Weather service temporarily unavailable. Please try again later.')
            else:
                messages.error(request, f'An error occurred: {error_message}')
            
            return render(request, 'predictor/predict.html', {'title': 'Weather Prediction'})


class ResultView(View):
    """
    Display prediction results
    """
    
    def get(self, request, prediction_id=None):
        if prediction_id:
            try:
                prediction = Prediction.objects.get(id=prediction_id)
                context = {
                    'title': 'Prediction Results',
                    'prediction': prediction
                }
                return render(request, 'predictor/result.html', context)
            except Prediction.DoesNotExist:
                messages.error(request, 'Prediction not found.')
                return redirect('predictor:predict')
        else:
            return redirect('predictor:predict')


class HistoryView(View):
    """
    Display prediction history with pagination
    """
    
    def get(self, request):
        predictions_list = Prediction.objects.all().order_by('-timestamp')
        
        # Pagination
        paginator = Paginator(predictions_list, 10)  # Show 10 predictions per page
        page_number = request.GET.get('page')
        predictions = paginator.get_page(page_number)
        
        context = {
            'title': 'Prediction History',
            'predictions': predictions,
            'total_predictions': predictions_list.count()
        }
        return render(request, 'predictor/history.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class APIWeatherView(View):
    """
    API endpoint for AJAX weather data requests
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            city = data.get('city', '').strip()
            
            if not validate_city_input(city):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid city name'
                }, status=400)
            
            # Fetch weather data
            api_client = WeatherAPIClient()
            weather_data = api_client.get_current_weather(city)
            
            return JsonResponse({
                'success': True,
                'data': weather_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


def delete_prediction(request, prediction_id):
    """
    Delete a specific prediction (for history management)
    """
    if request.method == 'POST':
        try:
            prediction = Prediction.objects.get(id=prediction_id)
            city_name = prediction.city
            prediction.delete()
            messages.success(request, f'Prediction for {city_name} deleted successfully.')
        except Prediction.DoesNotExist:
            messages.error(request, 'Prediction not found.')
    
    return redirect('predictor:history')


def clear_all_predictions(request):
    """
    Clear all prediction history
    """
    if request.method == 'POST':
        count = Prediction.objects.count()
        Prediction.objects.all().delete()
        messages.success(request, f'All {count} predictions cleared successfully.')
    
    return redirect('predictor:history')