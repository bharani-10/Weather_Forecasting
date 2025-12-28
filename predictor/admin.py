from django.contrib import admin
from django.db.models import Count, Avg
from django.utils.html import format_html
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Prediction model with analytics
    """
    list_display = [
        'city_with_flag', 
        'predicted_temperature_colored', 
        'predicted_humidity_bar', 
        'predicted_rain_badge', 
        'accuracy_indicator',
        'timestamp_formatted'
    ]
    
    list_filter = [
        'predicted_rain',
        'timestamp',
        'city',
        'predicted_temperature',
        'predicted_humidity',
    ]
    
    search_fields = [
        'city',
    ]
    
    readonly_fields = [
        'timestamp',
        'prediction_summary',
        'weather_comparison'
    ]
    
    ordering = ['-timestamp']
    
    fieldsets = (
        ('📍 Location', {
            'fields': ('city',),
            'classes': ('wide',)
        }),
        ('🌡️ Input Features', {
            'fields': (
                ('min_temp', 'max_temp'),
                ('wind_gust_speed', 'humidity'),
                ('pressure', 'current_temp')
            ),
            'classes': ('collapse',)
        }),
        ('🧠 AI Predictions', {
            'fields': (
                ('predicted_temperature', 'predicted_humidity'),
                'predicted_rain',
                'prediction_summary'
            ),
            'classes': ('wide',)
        }),
        ('📊 Analysis', {
            'fields': ('weather_comparison',),
            'classes': ('collapse',)
        }),
        ('⏰ Metadata', {
            'fields': ('timestamp',)
        })
    )
    
    actions = ['export_predictions', 'analyze_accuracy']
    
    def city_with_flag(self, obj):
        """Display city with country flag emoji"""
        flag_map = {
            'London': '🇬🇧', 'New York': '🇺🇸', 'Tokyo': '🇯🇵',
            'Paris': '🇫🇷', 'Sydney': '🇦🇺', 'Mumbai': '🇮🇳',
            'Berlin': '🇩🇪', 'Toronto': '🇨🇦', 'Dubai': '🇦🇪'
        }
        flag = flag_map.get(obj.city, '🌍')
        return format_html(f'{flag} <strong>{obj.city}</strong>')
    city_with_flag.short_description = '🏙️ City'
    
    def predicted_temperature_colored(self, obj):
        """Display temperature with color coding"""
        temp = obj.predicted_temperature
        if temp < 0:
            color = '#0066cc'  # Blue for freezing
        elif temp < 15:
            color = '#00cc66'  # Green for cold
        elif temp < 25:
            color = '#ffcc00'  # Yellow for mild
        else:
            color = '#ff6600'  # Orange for hot
        
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{temp:.1f}°C</span>'
        )
    predicted_temperature_colored.short_description = '🌡️ Temperature'
    
    def predicted_humidity_bar(self, obj):
        """Display humidity as a progress bar"""
        humidity = obj.predicted_humidity
        color = '#007bff' if humidity < 70 else '#28a745' if humidity < 85 else '#dc3545'
        
        return format_html(
            f'''
            <div style="width: 100px; background: #f0f0f0; border-radius: 10px; overflow: hidden;">
                <div style="width: {humidity}%; height: 20px; background: {color}; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 11px; font-weight: bold;">
                    {humidity:.0f}%
                </div>
            </div>
            '''
        )
    predicted_humidity_bar.short_description = '💧 Humidity'
    
    def predicted_rain_badge(self, obj):
        """Display rain prediction as a badge"""
        if obj.predicted_rain == 'Yes':
            return format_html(
                '<span style="background: #007bff; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 11px;">🌧️ Rain</span>'
            )
        else:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 11px;">☀️ Clear</span>'
            )
    predicted_rain_badge.short_description = '🌦️ Rain'
    
    def accuracy_indicator(self, obj):
        """Show prediction accuracy indicator"""
        # Simple accuracy calculation based on temperature difference
        temp_diff = abs(obj.predicted_temperature - obj.current_temp)
        if temp_diff < 2:
            return format_html('🎯 <span style="color: green;">High</span>')
        elif temp_diff < 5:
            return format_html('📊 <span style="color: orange;">Medium</span>')
        else:
            return format_html('📉 <span style="color: red;">Low</span>')
    accuracy_indicator.short_description = '🎯 Accuracy'
    
    def timestamp_formatted(self, obj):
        """Format timestamp nicely"""
        return obj.timestamp.strftime('%b %d, %Y at %I:%M %p')
    timestamp_formatted.short_description = '📅 Date & Time'
    
    def prediction_summary(self, obj):
        """Generate prediction summary"""
        return format_html(
            f'''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="color: #495057; margin-bottom: 10px;">🧠 AI Prediction Summary</h4>
                <p><strong>🌡️ Temperature:</strong> {obj.predicted_temperature:.1f}°C 
                   (Current: {obj.current_temp:.1f}°C)</p>
                <p><strong>💧 Humidity:</strong> {obj.predicted_humidity:.0f}% 
                   (Current: {obj.humidity}%)</p>
                <p><strong>🌧️ Rain Forecast:</strong> {obj.predicted_rain}</p>
                <p><strong>📍 Location:</strong> {obj.city}</p>
            </div>
            '''
        )
    prediction_summary.short_description = 'Prediction Summary'
    
    def weather_comparison(self, obj):
        """Compare current vs predicted weather"""
        temp_change = obj.predicted_temperature - obj.current_temp
        humidity_change = obj.predicted_humidity - obj.humidity
        
        temp_trend = "📈" if temp_change > 0 else "📉" if temp_change < 0 else "➡️"
        humidity_trend = "📈" if humidity_change > 0 else "📉" if humidity_change < 0 else "➡️"
        
        return format_html(
            f'''
            <div style="background: #e9ecef; padding: 15px; border-radius: 8px;">
                <h4 style="color: #495057; margin-bottom: 10px;">📊 Weather Analysis</h4>
                <p><strong>Temperature Trend:</strong> {temp_trend} {temp_change:+.1f}°C change</p>
                <p><strong>Humidity Trend:</strong> {humidity_trend} {humidity_change:+.0f}% change</p>
                <p><strong>Pressure:</strong> {obj.pressure} hPa</p>
                <p><strong>Wind Speed:</strong> {obj.wind_gust_speed:.1f} km/h</p>
            </div>
            '''
        )
    weather_comparison.short_description = 'Weather Analysis'
    
    def export_predictions(self, request, queryset):
        """Export selected predictions to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="weather_predictions.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'City', 'Current Temp', 'Predicted Temp', 'Current Humidity', 
            'Predicted Humidity', 'Rain Prediction', 'Timestamp'
        ])
        
        for prediction in queryset:
            writer.writerow([
                prediction.city,
                prediction.current_temp,
                prediction.predicted_temperature,
                prediction.humidity,
                prediction.predicted_humidity,
                prediction.predicted_rain,
                prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'Exported {queryset.count()} predictions to CSV.')
        return response
    export_predictions.short_description = "📥 Export selected predictions to CSV"
    
    def analyze_accuracy(self, request, queryset):
        """Analyze prediction accuracy"""
        total = queryset.count()
        if total == 0:
            self.message_user(request, 'No predictions selected for analysis.')
            return
        
        # Calculate average temperature accuracy
        temp_accuracy = sum(
            abs(p.predicted_temperature - p.current_temp) for p in queryset
        ) / total
        
        # Calculate humidity accuracy
        humidity_accuracy = sum(
            abs(p.predicted_humidity - p.humidity) for p in queryset
        ) / total
        
        self.message_user(
            request, 
            f'Analysis of {total} predictions: '
            f'Avg temp difference: {temp_accuracy:.1f}°C, '
            f'Avg humidity difference: {humidity_accuracy:.1f}%'
        )
    analyze_accuracy.short_description = "📊 Analyze prediction accuracy"
    
    def has_add_permission(self, request):
        # Disable adding predictions through admin
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context to changelist view"""
        extra_context = extra_context or {}
        
        # Add statistics
        total_predictions = Prediction.objects.count()
        cities_count = Prediction.objects.values('city').distinct().count()
        rain_predictions = Prediction.objects.filter(predicted_rain='Yes').count()
        
        extra_context.update({
            'total_predictions': total_predictions,
            'cities_count': cities_count,
            'rain_predictions': rain_predictions,
            'clear_predictions': total_predictions - rain_predictions,
        })
        
        return super().changelist_view(request, extra_context)