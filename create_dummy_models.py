#!/usr/bin/env python
"""
Create dummy ML models for testing purposes
"""

import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

def create_dummy_models():
    """Create and save dummy ML models"""
    
    # Create dummy training data
    np.random.seed(42)
    n_samples = 1000
    
    # Features: MinTemp, MaxTemp, WindGustSpeed, Humidity, Pressure, Temp
    X = np.random.rand(n_samples, 6) * 100
    
    # Temperature model (regression)
    y_temp = X[:, 0] + X[:, 1] + np.random.normal(0, 5, n_samples)  # Simple relationship
    temp_model = RandomForestRegressor(n_estimators=10, random_state=42)
    temp_model.fit(X, y_temp)
    
    # Humidity model (regression)
    y_humidity = X[:, 3] + np.random.normal(0, 10, n_samples)  # Based on current humidity
    humidity_model = RandomForestRegressor(n_estimators=10, random_state=42)
    humidity_model.fit(X, y_humidity)
    
    # Rain model (classification)
    y_rain = (X[:, 3] > 70).astype(int)  # Rain if humidity > 70%
    rain_model = RandomForestClassifier(n_estimators=10, random_state=42)
    rain_model.fit(X, y_rain)
    
    # Label encoder for rain prediction
    label_encoder = LabelEncoder()
    label_encoder.fit(['No', 'Yes'])
    
    # Save models
    models_dir = 'predictor/models'
    os.makedirs(models_dir, exist_ok=True)
    
    with open(f'{models_dir}/temperature_model.pkl', 'wb') as f:
        pickle.dump(temp_model, f)
    
    with open(f'{models_dir}/humidity_model.pkl', 'wb') as f:
        pickle.dump(humidity_model, f)
    
    with open(f'{models_dir}/rain_model.pkl', 'wb') as f:
        pickle.dump(rain_model, f)
    
    with open(f'{models_dir}/label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    print("✅ Dummy ML models created successfully!")
    print(f"   - Temperature model: {models_dir}/temperature_model.pkl")
    print(f"   - Humidity model: {models_dir}/humidity_model.pkl")
    print(f"   - Rain model: {models_dir}/rain_model.pkl")
    print(f"   - Label encoder: {models_dir}/label_encoder.pkl")

if __name__ == "__main__":
    create_dummy_models()