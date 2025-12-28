"""
Django management command for analyzing weather prediction accuracy and performance
Usage: python manage.py analyze_predictions [--days=30] [--export]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
import os

from predictor.models import Prediction


class Command(BaseCommand):
    help = 'Analyze weather prediction accuracy and generate reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export analysis to CSV file'
        )
        parser.add_argument(
            '--city',
            type=str,
            help='Analyze specific city only'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed analysis with individual predictions'
        )

    def handle(self, *args, **options):
        days = options['days']
        export = options['export']
        city_filter = options['city']
        detailed = options['detailed']

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Build queryset
        queryset = Prediction.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )

        if city_filter:
            queryset = queryset.filter(city__icontains=city_filter)

        total_predictions = queryset.count()

        if total_predictions == 0:
            self.stdout.write(
                self.style.WARNING(f'No predictions found for the last {days} days')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'\n🌤️  AI Weather Prediction Analysis Report')
        )
        self.stdout.write('=' * 60)

        # Basic Statistics
        self.stdout.write(f'\n📊 BASIC STATISTICS')
        self.stdout.write('-' * 30)
        self.stdout.write(f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
        self.stdout.write(f'Total Predictions: {total_predictions}')
        
        unique_cities = queryset.values('city').distinct().count()
        self.stdout.write(f'Unique Cities: {unique_cities}')

        rain_predictions = queryset.filter(predicted_rain='Yes').count()
        clear_predictions = total_predictions - rain_predictions
        self.stdout.write(f'Rain Predictions: {rain_predictions} ({rain_predictions/total_predictions*100:.1f}%)')
        self.stdout.write(f'Clear Predictions: {clear_predictions} ({clear_predictions/total_predictions*100:.1f}%)')

        # Temperature Analysis
        self.stdout.write(f'\n🌡️  TEMPERATURE ANALYSIS')
        self.stdout.write('-' * 30)
        
        temp_stats = queryset.aggregate(
            avg_predicted=Avg('predicted_temperature'),
            avg_current=Avg('current_temp')
        )
        
        avg_predicted_temp = temp_stats['avg_predicted'] or 0
        avg_current_temp = temp_stats['avg_current'] or 0
        
        self.stdout.write(f'Average Predicted Temperature: {avg_predicted_temp:.1f}°C')
        self.stdout.write(f'Average Current Temperature: {avg_current_temp:.1f}°C')
        self.stdout.write(f'Temperature Bias: {avg_predicted_temp - avg_current_temp:+.1f}°C')

        # Calculate temperature accuracy
        temp_differences = []
        for prediction in queryset:
            diff = abs(prediction.predicted_temperature - prediction.current_temp)
            temp_differences.append(diff)

        if temp_differences:
            avg_temp_error = sum(temp_differences) / len(temp_differences)
            self.stdout.write(f'Average Temperature Error: {avg_temp_error:.1f}°C')
            
            # Accuracy categories
            high_accuracy = sum(1 for diff in temp_differences if diff <= 2)
            medium_accuracy = sum(1 for diff in temp_differences if 2 < diff <= 5)
            low_accuracy = sum(1 for diff in temp_differences if diff > 5)
            
            self.stdout.write(f'High Accuracy (≤2°C): {high_accuracy} ({high_accuracy/total_predictions*100:.1f}%)')
            self.stdout.write(f'Medium Accuracy (2-5°C): {medium_accuracy} ({medium_accuracy/total_predictions*100:.1f}%)')
            self.stdout.write(f'Low Accuracy (>5°C): {low_accuracy} ({low_accuracy/total_predictions*100:.1f}%)')

        # Humidity Analysis
        self.stdout.write(f'\n💧 HUMIDITY ANALYSIS')
        self.stdout.write('-' * 30)
        
        humidity_stats = queryset.aggregate(
            avg_predicted=Avg('predicted_humidity'),
            avg_current=Avg('humidity')
        )
        
        avg_predicted_humidity = humidity_stats['avg_predicted'] or 0
        avg_current_humidity = humidity_stats['avg_current'] or 0
        
        self.stdout.write(f'Average Predicted Humidity: {avg_predicted_humidity:.1f}%')
        self.stdout.write(f'Average Current Humidity: {avg_current_humidity:.1f}%')
        self.stdout.write(f'Humidity Bias: {avg_predicted_humidity - avg_current_humidity:+.1f}%')

        # Calculate humidity accuracy
        humidity_differences = []
        for prediction in queryset:
            diff = abs(prediction.predicted_humidity - prediction.humidity)
            humidity_differences.append(diff)

        if humidity_differences:
            avg_humidity_error = sum(humidity_differences) / len(humidity_differences)
            self.stdout.write(f'Average Humidity Error: {avg_humidity_error:.1f}%')

        # Top Cities Analysis
        self.stdout.write(f'\n🏙️  TOP CITIES')
        self.stdout.write('-' * 30)
        
        top_cities = queryset.values('city').annotate(
            count=Count('city'),
            avg_temp=Avg('predicted_temperature'),
            avg_humidity=Avg('predicted_humidity'),
            rain_count=Count('city', filter=Q(predicted_rain='Yes'))
        ).order_by('-count')[:10]

        for i, city_data in enumerate(top_cities, 1):
            city = city_data['city']
            count = city_data['count']
            avg_temp = city_data['avg_temp']
            avg_humidity = city_data['avg_humidity']
            rain_count = city_data['rain_count']
            
            self.stdout.write(
                f'{i:2d}. {city:<15} | {count:3d} predictions | '
                f'{avg_temp:5.1f}°C avg | {avg_humidity:5.1f}% humidity | '
                f'{rain_count:2d} rain predictions'
            )

        # Daily Activity
        self.stdout.write(f'\n📅 DAILY ACTIVITY (Last 7 Days)')
        self.stdout.write('-' * 30)
        
        for i in range(7):
            date = (end_date - timedelta(days=i)).date()
            daily_count = queryset.filter(timestamp__date=date).count()
            bar = '█' * (daily_count // 2) if daily_count > 0 else ''
            self.stdout.write(f'{date} | {daily_count:3d} predictions | {bar}')

        # Detailed Analysis
        if detailed:
            self.stdout.write(f'\n🔍 DETAILED PREDICTIONS')
            self.stdout.write('-' * 60)
            self.stdout.write(f'{"City":<15} | {"Pred°C":<6} | {"Curr°C":<6} | {"Diff":<5} | {"Rain":<4} | {"Date":<10}')
            self.stdout.write('-' * 60)
            
            recent_predictions = queryset.order_by('-timestamp')[:20]
            for pred in recent_predictions:
                temp_diff = pred.predicted_temperature - pred.current_temp
                date_str = pred.timestamp.strftime('%m-%d')
                
                self.stdout.write(
                    f'{pred.city:<15} | {pred.predicted_temperature:6.1f} | '
                    f'{pred.current_temp:6.1f} | {temp_diff:+5.1f} | '
                    f'{pred.predicted_rain:<4} | {date_str:<10}'
                )

        # Export to CSV
        if export:
            self.export_analysis(queryset, days, city_filter)

        self.stdout.write(f'\n✅ Analysis completed successfully!')

    def export_analysis(self, queryset, days, city_filter):
        """Export analysis results to CSV file"""
        filename = f'weather_analysis_{days}days'
        if city_filter:
            filename += f'_{city_filter.lower().replace(" ", "_")}'
        filename += '.csv'
        
        filepath = os.path.join('reports', filename)
        os.makedirs('reports', exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'City', 'Timestamp', 'Current_Temp', 'Predicted_Temp', 'Temp_Difference',
                'Current_Humidity', 'Predicted_Humidity', 'Humidity_Difference',
                'Predicted_Rain', 'Pressure', 'Wind_Speed'
            ])
            
            # Write data
            for prediction in queryset.order_by('-timestamp'):
                temp_diff = prediction.predicted_temperature - prediction.current_temp
                humidity_diff = prediction.predicted_humidity - prediction.humidity
                
                writer.writerow([
                    prediction.city,
                    prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    prediction.current_temp,
                    prediction.predicted_temperature,
                    round(temp_diff, 2),
                    prediction.humidity,
                    prediction.predicted_humidity,
                    round(humidity_diff, 2),
                    prediction.predicted_rain,
                    prediction.pressure,
                    prediction.wind_gust_speed
                ])

        self.stdout.write(
            self.style.SUCCESS(f'📁 Analysis exported to: {filepath}')
        )