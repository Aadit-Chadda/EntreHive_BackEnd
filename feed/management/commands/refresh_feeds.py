from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from feed.models import TimelineFeedCache, ContentScore
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Refresh feed caches and update content scores to ensure feeds show current content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all timeline caches to force fresh generation'
        )
        parser.add_argument(
            '--update-scores',
            action='store_true',
            help='Update content scores for better feed ranking'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Refresh feeds for specific user (username)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Starting feed refresh process...")
        
        if options['clear_cache']:
            self._clear_caches(options.get('user'))
        
        if options['update_scores']:
            self._update_content_scores()
        
        # If no specific options, do both
        if not options['clear_cache'] and not options['update_scores']:
            self._clear_caches(options.get('user'))
            self._update_content_scores()
        
        self.stdout.write(self.style.SUCCESS("✅ Feed refresh completed!"))
        self.stdout.write("🎯 Tips:")
        self.stdout.write("   - Use --clear-cache to clear timeline caches")
        self.stdout.write("   - Use --update-scores to refresh content scoring")
        self.stdout.write("   - Use --user USERNAME to target specific user")

    def _clear_caches(self, username=None):
        """Clear timeline caches"""
        if username:
            try:
                user = User.objects.get(username=username)
                deleted_count, _ = TimelineFeedCache.objects.filter(user=user).delete()
                self.stdout.write(f"🧹 Cleared {deleted_count} cache entries for user: {username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ User '{username}' not found"))
        else:
            deleted_count, _ = TimelineFeedCache.objects.all().delete()
            self.stdout.write(f"🧹 Cleared {deleted_count} timeline cache entries")

    def _update_content_scores(self):
        """Update content scores for fresh ranking"""
        self.stdout.write("📊 Updating content scores...")
        
        from posts.models import Post
        from projects.models import Project
        import random
        
        # Update post scores
        posts = Post.objects.all()
        post_updates = 0
        for post in posts:
            score, created = ContentScore.objects.get_or_create(
                content_type='post',
                content_id=post.id,
                defaults={
                    'base_score': random.uniform(40.0, 95.0),
                    'engagement_score': random.uniform(0.0, 30.0),
                    'recency_score': self._calculate_recency_score(post.created_at),
                    'trending_score': random.uniform(0.0, 20.0),
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
            if not created:
                # Update existing score
                score.base_score = random.uniform(40.0, 95.0)
                score.engagement_score = random.uniform(0.0, 30.0)
                score.recency_score = self._calculate_recency_score(post.created_at)
                score.trending_score = random.uniform(0.0, 20.0)
                score.expires_at = timezone.now() + timedelta(hours=24)
                score.save()
            post_updates += 1
        
        # Update project scores
        projects = Project.objects.all()
        project_updates = 0
        for project in projects:
            score, created = ContentScore.objects.get_or_create(
                content_type='project',
                content_id=project.id,
                defaults={
                    'base_score': random.uniform(45.0, 90.0),
                    'engagement_score': random.uniform(10.0, 40.0),
                    'recency_score': self._calculate_recency_score(project.created_at),
                    'trending_score': random.uniform(0.0, 25.0),
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
            if not created:
                # Update existing score
                score.base_score = random.uniform(45.0, 90.0)
                score.engagement_score = random.uniform(10.0, 40.0)
                score.recency_score = self._calculate_recency_score(project.created_at)
                score.trending_score = random.uniform(0.0, 25.0)
                score.expires_at = timezone.now() + timedelta(hours=24)
                score.save()
            project_updates += 1
        
        self.stdout.write(f"✅ Updated scores for {post_updates} posts and {project_updates} projects")

    def _calculate_recency_score(self, created_at):
        """Calculate recency score based on age"""
        hours_old = (timezone.now() - created_at).total_seconds() / 3600
        # Decay over 7 days (168 hours)
        return max(0, 100 - (hours_old / 168) * 100)
