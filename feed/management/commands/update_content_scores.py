from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import logging

from feed.models import ContentScore
from posts.models import Post
from projects.models import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update content scores for posts and projects (background task)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days of content to update (default: 7)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for processing (default: 100)'
        )

    def handle(self, *args, **options):
        days = options['days']
        batch_size = options['batch_size']
        
        self.stdout.write(" Starting content score updates...")
        
        # Update scores for recent content
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Update post scores
        posts_updated = self._update_post_scores(cutoff_date, batch_size)
        self.stdout.write(f" Updated scores for {posts_updated} posts")
        
        # Update project scores
        projects_updated = self._update_project_scores(cutoff_date, batch_size)
        self.stdout.write(f" Updated scores for {projects_updated} projects")
        
        # Clean up expired scores
        expired_deleted = self._cleanup_expired_scores()
        self.stdout.write(f" Cleaned up {expired_deleted} expired score records")
        
        self.stdout.write(self.style.SUCCESS("Content score update completed!"))

    def _update_post_scores(self, cutoff_date, batch_size):
        """Update scores for posts"""
        updated_count = 0
        
        # Get recent posts with engagement data
        posts = Post.objects.filter(
            created_at__gte=cutoff_date,
            visibility__in=['public', 'university']
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-created_at')
        
        for i in range(0, posts.count(), batch_size):
            batch = posts[i:i + batch_size]
            
            for post in batch:
                try:
                    score, created = ContentScore.objects.get_or_create(
                        content_type='post',
                        content_id=post.id,
                        defaults={
                            'base_score': 50.0,
                            'engagement_score': 0.0,
                            'recency_score': 0.0,
                            'trending_score': 0.0,
                            'expires_at': timezone.now() + timedelta(hours=24)
                        }
                    )
                    
                    # Calculate scores
                    recency_score = self._calculate_recency_score(post.created_at)
                    engagement_score = self._calculate_engagement_score(
                        post.likes_count, post.comments_count
                    )
                    
                    # Update scores
                    score.recency_score = recency_score
                    score.engagement_score = engagement_score
                    score.base_score = min(100.0, 
                        (recency_score * 0.4) + 
                        (engagement_score * 0.4) + 
                        (score.trending_score * 0.2)
                    )
                    score.expires_at = timezone.now() + timedelta(hours=24)
                    score.save()
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating score for post {post.id}: {e}")
                    continue
        
        return updated_count
    
    def _update_project_scores(self, cutoff_date, batch_size):
        """Update scores for projects"""
        updated_count = 0
        
        # Get recent projects
        projects = Project.objects.filter(
            created_at__gte=cutoff_date,
            visibility__in=['public', 'university']
        ).order_by('-created_at')
        
        for i in range(0, projects.count(), batch_size):
            batch = projects[i:i + batch_size]
            
            for project in batch:
                try:
                    score, created = ContentScore.objects.get_or_create(
                        content_type='project',
                        content_id=project.id,
                        defaults={
                            'base_score': 50.0,
                            'engagement_score': 0.0,
                            'recency_score': 0.0,
                            'trending_score': 0.0,
                            'expires_at': timezone.now() + timedelta(hours=24)
                        }
                    )
                    
                    # Calculate scores
                    recency_score = self._calculate_recency_score(project.created_at)
                    engagement_score = self._calculate_project_engagement_score(project)
                    
                    # Update scores
                    score.recency_score = recency_score
                    score.engagement_score = engagement_score
                    score.base_score = min(100.0, 
                        (recency_score * 0.4) + 
                        (engagement_score * 0.4) + 
                        (score.trending_score * 0.2)
                    )
                    score.expires_at = timezone.now() + timedelta(hours=24)
                    score.save()
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating score for project {project.id}: {e}")
                    continue
        
        return updated_count
    
    def _calculate_recency_score(self, created_at):
        """Calculate recency score (0-100)"""
        hours_old = (timezone.now() - created_at).total_seconds() / 3600
        # Decay over 7 days (168 hours)
        recency_score = max(0, 100 - (hours_old / 168) * 100)
        return recency_score
    
    def _calculate_engagement_score(self, likes_count, comments_count):
        """Calculate engagement score for posts (0-100)"""
        engagement_points = (likes_count * 2) + (comments_count * 5)
        # Normalize to 0-100 scale
        engagement_score = min(100, engagement_points * 2)  # Rough scaling
        return engagement_score
    
    def _calculate_project_engagement_score(self, project):
        """Calculate engagement score for projects (0-100)"""
        base_score = 30  # Base score for having a project
        
        # Add points for needs (shows project is actively seeking help)
        if hasattr(project, 'needs') and project.needs:
            base_score += len(project.needs) * 10
        
        # Add points for team members (shows collaboration)
        team_count = project.team_members.count() if hasattr(project, 'team_members') else 0
        base_score += team_count * 5
        
        return min(100, base_score)
    
    def _cleanup_expired_scores(self):
        """Remove expired content scores"""
        now = timezone.now()
        expired_scores = ContentScore.objects.filter(expires_at__lt=now)
        count = expired_scores.count()
        expired_scores.delete()
        return count
