from django.core.management.base import BaseCommand
from universities.models import University


class Command(BaseCommand):
    help = 'Create a default university for migration purposes'

    def handle(self, *args, **options):
        default_university, created = University.objects.get_or_create(
            name='Default University',
            defaults={
                'short_name': 'DEFAULT',
                'university_type': 'other',
                'city': 'Unknown',
                'state_province': 'Unknown',
                'country': 'Unknown',
                'description': 'Default university created for migration purposes',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created default university: {default_university.id}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Default university already exists: {default_university.id}'
                )
            )
        
        return str(default_university.id)
