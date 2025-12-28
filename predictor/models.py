from django.db import models
from django.utils import timezone

class Prediction(models.Model):
    """
    Model to store weather predictions and their results
    """
    city = models.CharField(max_length=100)
    
    # Input features
    min_temp = models.FloatField()
    max_temp = models.FloatField()
    wind_gust_speed = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    current_temp = models.FloatField()
    
    # Predictions
    predicted_temperature = models.FloatField()
    predicted_humidity = models.FloatField()
    predicted_rain = models.CharField(max_length=10)  # 'Yes' or 'No'
    
    # Metadata
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.city} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"