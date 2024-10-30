from src.core.config import settings
from src.media.repositories import S3Repository


def get_s3_repository(bucket_name: str) -> S3Repository:
    return S3Repository(
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secrret_key,
        endpoint_url=settings.s3.endpoint_url,
        bucket_name=bucket_name,
    )
