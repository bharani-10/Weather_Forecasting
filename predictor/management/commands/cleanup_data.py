"""
Django management command for cleaning up old prediction data
Usage: python manage.py cleanup_data [--days=90] [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta

from predictor.models import Prediction


class Command(BaseCommand):
    help = 'Clean up old weather prediction data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete predictions older than N days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--keep-cities',
            nargs='+',
            help='Keep predictions for specific cities regardless of age'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        keep_cities = options['keep_cities'] or []

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find old predictions
        old_predictions = Prediction.objects.filter(timestamp__lt=cutoff_date)
        
        # Exclude cities to keep
        if keep_cities:
            old_predictions = old_predictions.exclude(city__in=keep_cities)

        count = old_predictions.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ No predictions older than {days} days found.')
            )
            return

        self.stdout.write(f'\n🧹 Data Cleanup Report')
        self.stdout.write('=' * 40)
        self.stdout.write(f'Cutoff Date: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'Predictions to delete: {count}')

        if keep_cities:
            self.stdout.write(f'Protected cities: {", ".join(keep_cities)}')

        # Show breakdown by city
        city_breakdown = old_predictions.values('city').annotate(
            count=models.Count('city')
        ).order_by('-count')

        if city_breakdown:
            self.stdout.write(f'\n📊 Breakdown by city:')
            for city_data in city_breakdown[:10]:
                city = city_data['city']
                city_count = city_data['count']
                self.stdout.write(f'  {city}: {city_count} predictions')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n🔍 DRY RUN: Would delete {count} predictions')
            )
            self.stdout.write('Use without --dry-run to actually delete the data')
        else:
            # Confirm deletion
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  This will permanently delete {count} predictions!')
            )
            
            confirm = input('Are you sure you want to continue? (yes/no): ')
            
            if confirm.lower() == 'yes':
                deleted_count, _ = old_predictions.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully deleted {deleted_count} predictions')
                )
                
                # Show remaining count
                remaining = Prediction.objects.count()
                self.stdout.write(f'📊 Remaining predictions: {remaining}')
            else:
                self.stdout.write(
                    self.style.WARNING('❌ Cleanup cancelled')
                )