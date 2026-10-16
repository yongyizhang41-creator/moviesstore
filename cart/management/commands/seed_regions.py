from django.core.management.base import BaseCommand
from django.db import transaction

from cart.models import Region


class Command(BaseCommand):
    help = 'Create or update the starter regions for the popularity map.'

    @transaction.atomic
    def handle(self, *args, **options):
        # Approximate representative points for markers, not state boundaries.
        regions = [
            ('US-AL', 'Alabama', 32.8, -86.8),
            ('US-AK', 'Alaska', 64.0, -152.0),
            ('US-AZ', 'Arizona', 34.3, -111.7),
            ('US-AR', 'Arkansas', 34.9, -92.4),
            ('US-CA', 'California', 37.0, -119.5),
            ('US-CO', 'Colorado', 39.0, -105.5),
            ('US-CT', 'Connecticut', 41.6, -72.7),
            ('US-DE', 'Delaware', 39.0, -75.5),
            ('US-FL', 'Florida', 28.6, -82.4),
            ('US-GA', 'Georgia', 33.0, -83.5),
            ('US-HI', 'Hawaii', 20.8, -156.3),
            ('US-ID', 'Idaho', 44.2, -114.5),
            ('US-IL', 'Illinois', 40.0, -89.0),
            ('US-IN', 'Indiana', 40.0, -86.1),
            ('US-IA', 'Iowa', 42.0, -93.5),
            ('US-KS', 'Kansas', 38.5, -98.0),
            ('US-KY', 'Kentucky', 37.5, -85.3),
            ('US-LA', 'Louisiana', 31.0, -92.0),
            ('US-ME', 'Maine', 45.3, -69.0),
            ('US-MD', 'Maryland', 39.0, -76.7),
            ('US-MA', 'Massachusetts', 42.3, -71.8),
            ('US-MI', 'Michigan', 44.3, -85.6),
            ('US-MN', 'Minnesota', 46.0, -94.5),
            ('US-MS', 'Mississippi', 32.7, -89.7),
            ('US-MO', 'Missouri', 38.5, -92.5),
            ('US-MT', 'Montana', 47.0, -110.0),
            ('US-NE', 'Nebraska', 41.5, -99.8),
            ('US-NV', 'Nevada', 39.0, -116.6),
            ('US-NH', 'New Hampshire', 43.8, -71.6),
            ('US-NJ', 'New Jersey', 40.1, -74.5),
            ('US-NM', 'New Mexico', 34.5, -106.0),
            ('US-NY', 'New York', 43.0, -75.0),
            ('US-NC', 'North Carolina', 35.5, -79.8),
            ('US-ND', 'North Dakota', 47.5, -100.5),
            ('US-OH', 'Ohio', 40.3, -82.8),
            ('US-OK', 'Oklahoma', 35.5, -97.5),
            ('US-OR', 'Oregon', 44.0, -120.5),
            ('US-PA', 'Pennsylvania', 41.0, -77.5),
            ('US-RI', 'Rhode Island', 41.7, -71.5),
            ('US-SC', 'South Carolina', 33.8, -80.9),
            ('US-SD', 'South Dakota', 44.5, -100.0),
            ('US-TN', 'Tennessee', 35.8, -86.4),
            ('US-TX', 'Texas', 31.0, -99.0),
            ('US-UT', 'Utah', 39.3, -111.7),
            ('US-VT', 'Vermont', 44.0, -72.7),
            ('US-VA', 'Virginia', 37.5, -79.0),
            ('US-WA', 'Washington', 47.4, -120.7),
            ('US-WV', 'West Virginia', 38.6, -80.6),
            ('US-WI', 'Wisconsin', 44.5, -89.5),
            ('US-WY', 'Wyoming', 43.0, -107.5),
        ]

        for code, name, latitude, longitude in regions:
            region, created = Region.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'latitude': latitude,
                    'longitude': longitude,
                },
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action}: {region.code} - {region.name}')

        self.stdout.write(self.style.SUCCESS('Starter regions are ready.'))
