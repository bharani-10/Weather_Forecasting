import pickle
import requests
import pandas as pd
import numpy as np
from django.conf import settings
from django.core.cache import cache
import os

class WeatherMLPredictor:
    """
    Utility class for loading ML models and making predictions
    """
    
    def __init__(self):
        self.models_path = os.path.join(settings.BASE_DIR, 'predictor', 'models')
        self.temp_model = None
        self.humidity_model = None
        self.rain_model = None
        self.label_encoder = None
        self._load_models()
    
    def _load_models(self):
        """Load all ML models from pickle files with caching"""
        try:
            # Check cache first
            cached_models = cache.get('ml_models')
            if cached_models:
                self.temp_model = cached_models['temp']
                self.humidity_model = cached_models['humidity']
                self.rain_model = cached_models['rain']
                self.label_encoder = cached_models['encoder']
                return
            
            # Load models from files
            with open(os.path.join(self.models_path, 'temperature_model.pkl'), 'rb') as f:
                self.temp_model = pickle.load(f)
            
            with open(os.path.join(self.models_path, 'humidity_model.pkl'), 'rb') as f:
                self.humidity_model = pickle.load(f)
            
            with open(os.path.join(self.models_path, 'rain_model.pkl'), 'rb') as f:
                self.rain_model = pickle.load(f)
            
            with open(os.path.join(self.models_path, 'label_encoder.pkl'), 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Cache models for 1 hour
            cache.set('ml_models', {
                'temp': self.temp_model,
                'humidity': self.humidity_model,
                'rain': self.rain_model,
                'encoder': self.label_encoder
            }, 3600)
            
        except Exception as e:
            raise Exception(f"Error loading ML models: {str(e)}")
    
    def predict_weather(self, features):
        """
        Make predictions using loaded models
        
        Args:
            features (dict): Dictionary containing weather features
            
        Returns:
            dict: Predictions for temperature, humidity, and rain
        """
        try:
            # Prepare feature array based on training data structure
            # Features: MinTemp, MaxTemp, WindGustSpeed, Humidity, Pressure, Temp
            feature_array = np.array([[
                features['min_temp'],
                features['max_temp'],
                features['wind_gust_speed'],
                features['humidity'],
                features['pressure'],
                features['current_temp']
            ]])
            
            # Make predictions
            temp_pred = self.temp_model.predict(feature_array)[0]
            humidity_pred = self.humidity_model.predict(feature_array)[0]
            rain_pred_encoded = self.rain_model.predict(feature_array)[0]
            
            # Decode rain prediction
            rain_pred = self.label_encoder.inverse_transform([rain_pred_encoded])[0]
            
            return {
                'temperature': round(temp_pred, 2),
                'humidity': round(humidity_pred, 2),
                'rain': rain_pred
            }
            
        except Exception as e:
            raise Exception(f"Error making predictions: {str(e)}")


class WeatherAPIClient:
    """
    Client for fetching real-time weather data from OpenWeatherMap API
    """
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_BASE_URL
    
    def get_current_weather(self, city):
        """
        Fetch current weather data for a city
        
        Args:
            city (str): City name
            
        Returns:
            dict: Weather data or None if error
        """
        try:
            url = f"{self.base_url}weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant features
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'current_temp': data['main']['temp'],
                'min_temp': data['main']['temp_min'],
                'max_temp': data['main']['temp_max'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'wind_gust_speed': data.get('wind', {}).get('gust', data.get('wind', {}).get('speed', 10)),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid API response format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching weather data: {str(e)}")
    
    def get_forecast(self, city, days=5):
        """
        Fetch weather forecast for a city
        
        Args:
            city (str): City name
            days (int): Number of days (max 5 for free API)
            
        Returns:
            dict: Forecast data or None if error
        """
        try:
            url = f"{self.base_url}forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Error fetching forecast: {str(e)}")


def validate_city_input(city):
    """
    Validate city input
    
    Args:
        city (str): City name
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not city or len(city.strip()) < 2:
        return False
    
    # Basic validation - letters, spaces, hyphens, apostrophes, and accented characters
    import re
    pattern = r"^[a-zA-ZÀ-ÿ\s\-']+$"
    return bool(re.match(pattern, city.strip()))


def get_country_name(country_code):
    """
    Convert country code to full country name
    
    Args:
        country_code (str): ISO country code
        
    Returns:
        str: Full country name
    """
    country_mapping = {
        'GB': 'United Kingdom',
        'UK': 'United Kingdom',
        'US': 'United States',
        'JP': 'Japan',
        'FR': 'France',
        'AU': 'Australia',
        'IN': 'India',
        'DE': 'Germany',
        'CA': 'Canada',
        'AE': 'United Arab Emirates',
        'SG': 'Singapore',
        'ES': 'Spain',
        'IT': 'Italy',
        'NL': 'Netherlands',
        'RU': 'Russia',
        'TR': 'Turkey',
        'TH': 'Thailand',
        'KR': 'South Korea',
        'HK': 'Hong Kong',
        'AT': 'Austria',
        'CZ': 'Czech Republic',
        'HU': 'Hungary',
        'PL': 'Poland',
        'BR': 'Brazil',
        'MX': 'Mexico',
        'AR': 'Argentina',
        'CL': 'Chile',
        'CO': 'Colombia',
        'PE': 'Peru',
        'VE': 'Venezuela',
        'CN': 'China',
        'MY': 'Malaysia',
        'ID': 'Indonesia',
        'PH': 'Philippines',
        'VN': 'Vietnam',
        'EG': 'Egypt',
        'ZA': 'South Africa',
        'NG': 'Nigeria',
        'KE': 'Kenya',
        'MA': 'Morocco',
        'NO': 'Norway',
        'SE': 'Sweden',
        'DK': 'Denmark',
        'FI': 'Finland',
        'IS': 'Iceland',
        'CH': 'Switzerland',
        'BE': 'Belgium',
        'LU': 'Luxembourg',
        'PT': 'Portugal',
        'GR': 'Greece',
        'IE': 'Ireland',
        'IL': 'Israel',
        'SA': 'Saudi Arabia',
        'QA': 'Qatar',
        'KW': 'Kuwait',
        'BH': 'Bahrain',
        'OM': 'Oman',
        'JO': 'Jordan',
        'LB': 'Lebanon',
        'NZ': 'New Zealand'
    }
    
    return country_mapping.get(country_code.upper(), country_code)


def format_city_display(city_name, country_code):
    """
    Format city and country for professional display
    
    Args:
        city_name (str): City name
        country_code (str): Country code
        
    Returns:
        dict: Formatted city information
    """
    return {
        'name': city_name.title(),
        'country': country_code.upper(),
        'country_full': get_country_name(country_code),
        'display': f"{city_name.title()}, {get_country_name(country_code)}"
    }


def format_weather_data_for_prediction(weather_data):
    """
    Format weather API data for ML model prediction
    
    Args:
        weather_data (dict): Raw weather data from API
        
    Returns:
        dict: Formatted features for ML model
    """
    return {
        'min_temp': weather_data['min_temp'],
        'max_temp': weather_data['max_temp'],
        'wind_gust_speed': weather_data['wind_gust_speed'],
        'humidity': weather_data['humidity'],
        'pressure': weather_data['pressure'],
        'current_temp': weather_data['current_temp']
    }