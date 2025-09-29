# Generated manually for search optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_banner_gradient_project_banner_image_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Add text search indexes for better performance
            sql=[
                "CREATE INDEX IF NOT EXISTS idx_project_title_search ON projects_project(title);",
                "CREATE INDEX IF NOT EXISTS idx_project_summary_search ON projects_project(summary);",
                "CREATE INDEX IF NOT EXISTS idx_project_owner_search ON projects_project(owner_id);",
                "CREATE INDEX IF NOT EXISTS idx_project_categories_search ON projects_project(categories);",
                "CREATE INDEX IF NOT EXISTS idx_project_tags_search ON projects_project(tags);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_project_title_search;",
                "DROP INDEX IF EXISTS idx_project_summary_search;",
                "DROP INDEX IF EXISTS idx_project_owner_search;",
                "DROP INDEX IF EXISTS idx_project_categories_search;",
                "DROP INDEX IF EXISTS idx_project_tags_search;",
            ]
        ),
    ]
