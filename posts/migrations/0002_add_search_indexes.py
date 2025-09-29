# Generated manually for search optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Add text search indexes for better performance
            sql=[
                "CREATE INDEX IF NOT EXISTS idx_post_content_search ON posts_post(content);",
                "CREATE INDEX IF NOT EXISTS idx_post_author_search ON posts_post(author_id);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_post_content_search;",
                "DROP INDEX IF EXISTS idx_post_author_search;",
            ]
        ),
    ]
