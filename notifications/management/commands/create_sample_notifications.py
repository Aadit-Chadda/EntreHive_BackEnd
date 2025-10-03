from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create notifications for',
            required=True
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return

        # Get another user to act as sender
        other_users = User.objects.exclude(id=user.id)[:3]
        
        if not other_users:
            self.stdout.write(self.style.WARNING('No other users found to create sample notifications'))
            return

        # Create sample notifications
        for i, sender in enumerate(other_users):
            # Follow notification
            Notification.create_follow_notification(sender, user)
            self.stdout.write(self.style.SUCCESS(f'Created follow notification from {sender.username}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created sample notifications for {username}'))

