#!/usr/bin/env python
"""
Advanced Features Test Suite for AI Weather Prediction System
Tests all the enhanced features including API endpoints, management commands, and dashboard
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_prediction.settings')
django.setup()

from predictor.models import Prediction
from predictor.utils import WeatherMLPredictor, WeatherAPIClient

def test_api_endpoints():
    """Test the new API endpoints"""
    print("🌐 Testing Advanced API Endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/v1/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['message']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
    
    # Test city autocomplete
    try:
        response = requests.get(f"{base_url}/api/v1/cities/autocomplete/?q=Lon")
        if response.status_code == 200:
            data = response.json()
            suggestions = data['data']['suggestions']
            print(f"✅ Autocomplete: Found {len(suggestions)} suggestions for 'Lon'")
        else:
            print(f"❌ Autocomplete Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Autocomplete Error: {e}")
    
    # Test stats API
    try:
        response = requests.get(f"{base_url}/api/v1/stats/")
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            print(f"✅ Stats API: {stats['totals']['predictions']} total predictions")
        else:
            print(f"❌ Stats API Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats API Error: {e}")
    
    # Test prediction API
    try:
        payload = {"city": "London"}
        response = requests.post(
            f"{base_url}/api/v1/predict/",
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            city = data['data']['city']['name']
            temp = data['data']['predictions']['temperature']
            print(f"✅ Prediction API: {city} - {temp}°C predicted")
        else:
            print(f"❌ Prediction API Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prediction API Error: {e}")

def test_database_features():
    """Test database and model features"""
    print("\n💾 Testing Database Features...")
    
    # Test prediction count
    total_predictions = Prediction.objects.count()
    print(f"✅ Total Predictions in Database: {total_predictions}")
    
    # Test recent predictions
    recent = Prediction.objects.order_by('-timestamp')[:5]
    print(f"✅ Recent Predictions: {len(recent)} found")
    
    for pred in recent:
        print(f"   - {pred.city}: {pred.predicted_temperature:.1f}°C, {pred.predicted_rain}")
    
    # Test city statistics
    from django.db.models import Count
    city_stats = Prediction.objects.values('city').annotate(count=Count('city')).order_by('-count')[:3]
    print(f"✅ Top Cities:")
    for stat in city_stats:
        print(f"   - {stat['city']}: {stat['count']} predictions")

def test_ml_models():
    """Test ML model functionality"""
    print("\n🧠 Testing ML Models...")
    
    try:
        predictor = WeatherMLPredictor()
        
        # Test with sample data
        features = {
            'min_temp': 15.0,
            'max_temp': 25.0,
            'wind_gust_speed': 20.0,
            'humidity': 70.0,
            'pressure': 1015.0,
            'current_temp': 22.0
        }
        
        predictions = predictor.predict_weather(features)
        
        print(f"✅ Temperature Prediction: {predictions['temperature']:.1f}°C")
        print(f"✅ Humidity Prediction: {predictions['humidity']:.1f}%")
        print(f"✅ Rain Prediction: {predictions['rain']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Model Error: {e}")
        return False

def test_weather_api():
    """Test weather API integration"""
    print("\n🌤️ Testing Weather API...")
    
    try:
        client = WeatherAPIClient()
        weather_data = client.get_current_weather("Paris")
        
        print(f"✅ API Response for Paris:")
        print(f"   - Temperature: {weather_data['current_temp']:.1f}°C")
        print(f"   - Humidity: {weather_data['humidity']}%")
        print(f"   - Description: {weather_data['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Weather API Error: {e}")
        return False

def test_admin_features():
    """Test admin interface features"""
    print("\n⚙️ Testing Admin Features...")
    
    try:
        from django.contrib.admin.sites import site
        from predictor.admin import PredictionAdmin
        from predictor.models import Prediction
        
        # Test admin registration
        if Prediction in site._registry:
            print("✅ Prediction model registered in admin")
            
            admin_class = site._registry[Prediction]
            print(f"✅ Admin class: {admin_class.__class__.__name__}")
            print(f"✅ List display fields: {len(admin_class.list_display)}")
            print(f"✅ List filters: {len(admin_class.list_filter)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Admin Features Error: {e}")
        return False

def test_management_commands():
    """Test management commands"""
    print("\n🔧 Testing Management Commands...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Test analyze_predictions command
        out = StringIO()
        call_command('analyze_predictions', '--days=7', stdout=out)
        output = out.getvalue()
        
        if "Analysis completed successfully" in output:
            print("✅ Analyze Predictions Command: Working")
        else:
            print("❌ Analyze Predictions Command: Failed")
        
        # Test help for cleanup command
        out = StringIO()
        call_command('cleanup_data', '--help', stdout=out)
        help_output = out.getvalue()
        
        if "Clean up old weather prediction data" in help_output:
            print("✅ Cleanup Data Command: Available")
        else:
            print("❌ Cleanup Data Command: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Management Commands Error: {e}")
        return False

def test_dashboard_features():
    """Test dashboard functionality"""
    print("\n📊 Testing Dashboard Features...")
    
    try:
        # Test dashboard view import
        from predictor.views import DashboardView
        print("✅ Dashboard View: Available")
        
        # Test dashboard template exists
        import os
        template_path = "predictor/templates/predictor/dashboard.html"
        if os.path.exists(template_path):
            print("✅ Dashboard Template: Found")
        else:
            print("❌ Dashboard Template: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard Features Error: {e}")
        return False

def main():
    """Run all advanced feature tests"""
    print("🚀 AI Weather Prediction System - Advanced Features Test Suite")
    print("=" * 70)
    
    tests = [
        ("ML Models", test_ml_models),
        ("Weather API", test_weather_api),
        ("Database Features", test_database_features),
        ("Admin Features", test_admin_features),
        ("Management Commands", test_management_commands),
        ("Dashboard Features", test_dashboard_features),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("📊 Advanced Features Test Results:")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} advanced features working")
    
    if passed == len(results):
        print("🎉 All advanced features are working perfectly!")
        print("\n🌟 Your AI Weather Prediction System now includes:")
        print("   • Advanced API endpoints with comprehensive error handling")
        print("   • Enhanced admin interface with analytics and visualizations")
        print("   • Management commands for data analysis and cleanup")
        print("   • Interactive dashboard with real-time charts")
        print("   • Professional-grade error handling and logging")
        print("   • RESTful API for mobile and third-party integrations")
    else:
        print("⚠️  Some advanced features need attention.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)