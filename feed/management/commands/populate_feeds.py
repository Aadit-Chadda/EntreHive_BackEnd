from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from feed.models import FeedConfiguration


class Command(BaseCommand):
    help = 'Populate feeds for all users and create default feed configurations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting feed population...'))
        
        # Create default feed configurations for all users
        users_without_config = User.objects.exclude(feed_config__isnull=False)
        configs_created = 0
        
        for user in users_without_config:
            config, created = FeedConfiguration.objects.get_or_create(user=user)
            if created:
                configs_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {configs_created} feed configurations')
        )
        
        self.stdout.write(
            self.style.SUCCESS('Feed population completed successfully!')
        )
