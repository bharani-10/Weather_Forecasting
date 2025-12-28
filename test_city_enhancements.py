#!/usr/bin/env python
"""
Test script for enhanced city/location functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_prediction.settings')
django.setup()

from predictor.utils import format_city_display, get_country_name, validate_city_input

def test_city_formatting():
    """Test city formatting functionality"""
    print("🧪 Testing City Formatting Functionality")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ('london', 'GB'),
        ('new york', 'US'),
        ('tokyo', 'JP'),
        ('paris', 'FR'),
        ('sydney', 'AU'),
        ('mumbai', 'IN'),
        ('dubai', 'AE'),
        ('singapore', 'SG')
    ]
    
    for city, country in test_cases:
        formatted = format_city_display(city, country)
        print(f"✅ {city.upper()}, {country} → {formatted['display']}")
    
    print("\n🌍 Testing Country Name Mapping")
    print("=" * 50)
    
    country_codes = ['GB', 'US', 'JP', 'FR', 'AU', 'IN', 'DE', 'CA', 'AE', 'SG']
    for code in country_codes:
        full_name = get_country_name(code)
        print(f"✅ {code} → {full_name}")
    
    print("\n🔍 Testing City Input Validation")
    print("=" * 50)
    
    valid_cities = ['London', 'New York', 'São Paulo', "O'Connor", 'Saint-Denis']
    invalid_cities = ['L', '123', 'City123', '', '   ']
    
    for city in valid_cities:
        result = validate_city_input(city)
        print(f"✅ '{city}' → Valid: {result}")
    
    for city in invalid_cities:
        result = validate_city_input(city)
        print(f"❌ '{city}' → Valid: {result}")

if __name__ == '__main__':
    test_city_formatting()
    print("\n🎉 All tests completed!")