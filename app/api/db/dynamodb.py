import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from app.api.core.config import settings

# Initialize a DynamoDB resource
def get_dynamodb_resource():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        return dynamodb
    except (NoCredentialsError, PartialCredentialsError):
        raise ValueError("AWS credentials not found or incomplete.")
