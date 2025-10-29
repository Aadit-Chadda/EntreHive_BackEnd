"""
Custom storage backends for AWS S3
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """Custom storage for media files"""
    location = 'media'
    file_overwrite = False
    querystring_auth = True
    


class StaticStorage(S3Boto3Storage):
    """Custom storage for static files"""
    location = 'static'
    file_overwrite = True  # We want to overwrite static files
    querystring_auth = True 