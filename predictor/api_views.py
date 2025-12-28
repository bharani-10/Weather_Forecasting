"""
Advanced API Views for AI Weather Prediction System
RESTful API endpoints for mobile apps and third-party integrations
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
import json
import logging
from datetime import datetime, timedelta

from .models import Prediction
from .utils import WeatherMLPredictor, WeatherAPIClient, validate_city_input, format_weather_data_for_prediction

logger = logging.getLogger(__name__)

class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return JsonResponse({
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, status=status_code)
    
    @staticmethod
    def error(message="An error occurred", status_code=400, error_code=None):
        return JsonResponse({
            'success': False,
            'message': message,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat()
        }, status=status_code)

@method_decorator(csrf_exempt, name='dispatch')
class WeatherPredictionAPI(View):
    """
    Main API endpoint for weather predictions
    """
    
    def post(self, request):
        """Make a weather prediction for a city"""
        try:
            data = json.loads(request.body)
            city = data.get('city', '').strip()
            
            # Validate input
            if not validate_city_input(city):
                return APIResponse.error(
                    "Invalid city name. Please provide a valid city name with at least 2 characters.",
                    status_code=400,
                    error_code="INVALID_CITY"
                )
            
            # Initialize clients
            api_client = WeatherAPIClient()
            ml_predictor = WeatherMLPredictor()
            
            # Fetch current weather
            try:
                weather_data = api_client.get_current_weather(city)
            except Exception as e:
                logger.error(f"Weather API error for {city}: {str(e)}")
                return APIResponse.error(
                    f"Unable to fetch weather data for {city}. Please check the city name.",
                    status_code=404,
                    error_code="CITY_NOT_FOUND"
                )
            
            # Format features for ML
            features = format_weather_data_for_prediction(weather_data)
            
            # Make predictions
            try:
                predictions = ml_predictor.predict_weather(features)
            except Exception as e:
                logger.error(f"ML prediction error: {str(e)}")
                return APIResponse.error(
                    "Prediction service temporarily unavailable. Please try again later.",
                    status_code=503,
                    error_code="PREDICTION_ERROR"
                )
            
            # Save to database
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
            
            # Prepare response
            response_data = {
                'prediction_id': prediction_record.id,
                'city': {
                    'name': weather_data['city'],
                    'country': weather_data['country']
                },
                'current_weather': {
                    'temperature': weather_data['current_temp'],
                    'humidity': weather_data['humidity'],
                    'pressure': weather_data['pressure'],
                    'description': weather_data['description'],
                    'icon': weather_data['icon']
                },
                'predictions': {
                    'temperature': predictions['temperature'],
                    'humidity': predictions['humidity'],
                    'rain': predictions['rain']
                },
                'confidence': {
                    'temperature': 92,  # Mock confidence scores
                    'humidity': 89,
                    'rain': 95
                },
                'timestamp': prediction_record.timestamp.isoformat()
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Weather prediction completed for {weather_data['city']}"
            )
            
        except json.JSONDecodeError:
            return APIResponse.error(
                "Invalid JSON format in request body",
                status_code=400,
                error_code="INVALID_JSON"
            )
        except Exception as e:
            logger.error(f"Unexpected error in prediction API: {str(e)}")
            return APIResponse.error(
                "Internal server error. Please try again later.",
                status_code=500,
                error_code="INTERNAL_ERROR"
            )

@method_decorator(csrf_exempt, name='dispatch')
class PredictionHistoryAPI(View):
    """
    API endpoint for prediction history
    """
    
    def get(self, request):
        """Get prediction history with pagination and filtering"""
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            limit = min(int(request.GET.get('limit', 10)), 100)  # Max 100 per page
            city_filter = request.GET.get('city', '').strip()
            rain_filter = request.GET.get('rain', '').strip()
            days = int(request.GET.get('days', 30))  # Last N days
            
            # Build query
            queryset = Prediction.objects.all()
            
            # Apply filters
            if city_filter:
                queryset = queryset.filter(city__icontains=city_filter)
            
            if rain_filter in ['Yes', 'No']:
                queryset = queryset.filter(predicted_rain=rain_filter)
            
            # Date filter
            if days > 0:
                since_date = datetime.now() - timedelta(days=days)
                queryset = queryset.filter(timestamp__gte=since_date)
            
            # Order by timestamp
            queryset = queryset.order_by('-timestamp')
            
            # Paginate
            paginator = Paginator(queryset, limit)
            predictions_page = paginator.get_page(page)
            
            # Format predictions
            predictions_data = []
            for prediction in predictions_page:
                predictions_data.append({
                    'id': prediction.id,
                    'city': prediction.city,
                    'current_weather': {
                        'temperature': prediction.current_temp,
                        'humidity': prediction.humidity,
                        'pressure': prediction.pressure
                    },
                    'predictions': {
                        'temperature': prediction.predicted_temperature,
                        'humidity': prediction.predicted_humidity,
                        'rain': prediction.predicted_rain
                    },
                    'timestamp': prediction.timestamp.isoformat()
                })
            
            response_data = {
                'predictions': predictions_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': predictions_page.has_next(),
                    'has_previous': predictions_page.has_previous()
                },
                'filters': {
                    'city': city_filter,
                    'rain': rain_filter,
                    'days': days
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(predictions_data)} predictions"
            )
            
        except ValueError as e:
            return APIResponse.error(
                "Invalid parameter format",
                status_code=400,
                error_code="INVALID_PARAMETER"
            )
        except Exception as e:
            logger.error(f"Error in history API: {str(e)}")
            return APIResponse.error(
                "Unable to retrieve prediction history",
                status_code=500,
                error_code="HISTORY_ERROR"
            )

@method_decorator(csrf_exempt, name='dispatch')
class PredictionStatsAPI(View):
    """
    API endpoint for prediction statistics
    """
    
    def get(self, request):
        """Get prediction statistics and analytics"""
        try:
            days = int(request.GET.get('days', 30))
            since_date = datetime.now() - timedelta(days=days)
            
            # Base queryset
            queryset = Prediction.objects.filter(timestamp__gte=since_date)
            
            # Basic stats
            total_predictions = queryset.count()
            unique_cities = queryset.values('city').distinct().count()
            rain_predictions = queryset.filter(predicted_rain='Yes').count()
            clear_predictions = total_predictions - rain_predictions
            
            # Temperature stats
            temp_stats = queryset.aggregate(
                avg_predicted_temp=Avg('predicted_temperature'),
                avg_current_temp=Avg('current_temp')
            )
            
            # Humidity stats
            humidity_stats = queryset.aggregate(
                avg_predicted_humidity=Avg('predicted_humidity'),
                avg_current_humidity=Avg('humidity')
            )
            
            # Top cities
            top_cities = list(queryset.values('city')
                            .annotate(count=Count('city'))
                            .order_by('-count')[:10])
            
            # Daily prediction counts (last 7 days)
            daily_counts = []
            for i in range(7):
                date = datetime.now().date() - timedelta(days=i)
                count = queryset.filter(timestamp__date=date).count()
                daily_counts.append({
                    'date': date.isoformat(),
                    'count': count
                })
            
            response_data = {
                'period': {
                    'days': days,
                    'start_date': since_date.date().isoformat(),
                    'end_date': datetime.now().date().isoformat()
                },
                'totals': {
                    'predictions': total_predictions,
                    'cities': unique_cities,
                    'rain_predictions': rain_predictions,
                    'clear_predictions': clear_predictions
                },
                'averages': {
                    'predicted_temperature': round(temp_stats['avg_predicted_temp'] or 0, 1),
                    'current_temperature': round(temp_stats['avg_current_temp'] or 0, 1),
                    'predicted_humidity': round(humidity_stats['avg_predicted_humidity'] or 0, 1),
                    'current_humidity': round(humidity_stats['avg_current_humidity'] or 0, 1)
                },
                'top_cities': top_cities,
                'daily_activity': daily_counts
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Statistics for the last {days} days"
            )
            
        except ValueError:
            return APIResponse.error(
                "Invalid days parameter",
                status_code=400,
                error_code="INVALID_DAYS"
            )
        except Exception as e:
            logger.error(f"Error in stats API: {str(e)}")
            return APIResponse.error(
                "Unable to retrieve statistics",
                status_code=500,
                error_code="STATS_ERROR"
            )

@require_http_methods(["GET"])
def api_health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        prediction_count = Prediction.objects.count()
        
        # Test ML models
        predictor = WeatherMLPredictor()
        
        # Test API client
        api_client = WeatherAPIClient()
        
        return APIResponse.success(
            data={
                'status': 'healthy',
                'database': 'connected',
                'ml_models': 'loaded',
                'api_client': 'ready',
                'total_predictions': prediction_count,
                'version': '1.0.0'
            },
            message="System is healthy"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return APIResponse.error(
            "System health check failed",
            status_code=503,
            error_code="HEALTH_CHECK_FAILED"
        )

@require_http_methods(["GET"])
def api_cities_autocomplete(request):
    """Autocomplete endpoint for city suggestions"""
    try:
        query = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 20)
        
        if len(query) < 2:
            return APIResponse.error(
                "Query must be at least 2 characters",
                status_code=400,
                error_code="QUERY_TOO_SHORT"
            )
        
        # Popular cities for autocomplete
        popular_cities = [
            'London', 'New York', 'Tokyo', 'Paris', 'Sydney', 'Mumbai', 'Berlin',
            'Toronto', 'Dubai', 'Singapore', 'Los Angeles', 'Chicago', 'Madrid',
            'Rome', 'Amsterdam', 'Barcelona', 'Moscow', 'Istanbul', 'Bangkok',
            'Seoul', 'Hong Kong', 'Vienna', 'Prague', 'Budapest', 'Warsaw',
            'Stockholm', 'Oslo', 'Copenhagen', 'Helsinki', 'Dublin', 'Lisbon',
            'Athens', 'Cairo', 'Lagos', 'Nairobi', 'Cape Town', 'Johannesburg',
            'São Paulo', 'Rio de Janeiro', 'Buenos Aires', 'Lima', 'Santiago',
            'Mexico City', 'Vancouver', 'Montreal', 'Miami', 'San Francisco'
        ]
        
        # Filter cities based on query
        suggestions = [
            city for city in popular_cities 
            if query.lower() in city.lower()
        ][:limit]
        
        # Also get cities from database
        db_cities = list(
            Prediction.objects.filter(city__icontains=query)
            .values_list('city', flat=True)
            .distinct()[:limit]
        )
        
        # Combine and deduplicate
        all_suggestions = list(set(suggestions + db_cities))[:limit]
        
        return APIResponse.success(
            data={
                'query': query,
                'suggestions': all_suggestions,
                'count': len(all_suggestions)
            },
            message=f"Found {len(all_suggestions)} city suggestions"
        )
        
    except ValueError:
        return APIResponse.error(
            "Invalid limit parameter",
            status_code=400,
            error_code="INVALID_LIMIT"
        )
    except Exception as e:
        logger.error(f"Error in autocomplete API: {str(e)}")
        return APIResponse.error(
            "Unable to get city suggestions",
            status_code=500,
            error_code="AUTOCOMPLETE_ERROR"
        )