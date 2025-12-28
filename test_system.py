#!/usr/bin/env python
"""
Test script to verify the AI Weather Prediction System
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_prediction.settings')
django.setup()

from predictor.utils import WeatherMLPredictor, WeatherAPIClient, validate_city_input

def test_ml_models():
    """Test ML model loading and prediction"""
    print("🧠 Testing ML Models...")
    
    try:
        predictor = WeatherMLPredictor()
        
        # Test prediction with sample data
        sample_features = {
            'min_temp': 10.0,
            'max_temp': 25.0,
            'wind_gust_speed': 15.0,
            'humidity': 65.0,
            'pressure': 1013.0,
            'current_temp': 20.0
        }
        
        predictions = predictor.predict_weather(sample_features)
        
        print(f"✅ Temperature Prediction: {predictions['temperature']}°C")
        print(f"✅ Humidity Prediction: {predictions['humidity']}%")
        print(f"✅ Rain Prediction: {predictions['rain']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Model Error: {e}")
        return False

def test_api_client():
    """Test weather API client"""
    print("\n🌐 Testing Weather API...")
    
    try:
        client = WeatherAPIClient()
        weather_data = client.get_current_weather("London")
        
        print(f"✅ City: {weather_data['city']}")
        print(f"✅ Temperature: {weather_data['current_temp']}°C")
        print(f"✅ Humidity: {weather_data['humidity']}%")
        print(f"✅ Description: {weather_data['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("\n🔍 Testing Input Validation...")
    
    test_cases = [
        ("London", True),
        ("New York", True),
        ("", False),
        ("A", False),
        ("123", False),
        ("London123", False),
        ("São Paulo", True),
    ]
    
    all_passed = True
    for city, expected in test_cases:
        result = validate_city_input(city)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{city}' -> {result} (expected {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_database():
    """Test database operations"""
    print("\n💾 Testing Database...")
    
    try:
        from predictor.models import Prediction
        
        # Test creating a prediction
        prediction = Prediction.objects.create(
            city="Test City",
            min_temp=10.0,
            max_temp=25.0,
            wind_gust_speed=15.0,
            humidity=65.0,
            pressure=1013.0,
            current_temp=20.0,
            predicted_temperature=22.0,
            predicted_humidity=68.0,
            predicted_rain="No"
        )
        
        print(f"✅ Created prediction: {prediction}")
        
        # Test querying
        count = Prediction.objects.count()
        print(f"✅ Total predictions in database: {count}")
        
        # Clean up test data
        prediction.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Weather Prediction System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("ML Models", test_ml_models),
        ("Weather API", test_api_client),
        ("Input Validation", test_validation),
        ("Database", test_database),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your system is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)