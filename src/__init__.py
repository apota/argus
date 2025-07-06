"""
Argus - AWS Resource Explorer Library

A modular Python library for exploring AWS resources using Boto3.
Provides separate read and write modules for each AWS service.
"""

__version__ = "0.1.0"
__author__ = "Argus Development Team"

# Import main modules for easy access
from .common.aws_client import AWSClientManager
from .common.exceptions import AWSResourceError, ResourceNotFoundError

# Import service modules
from . import s3
from . import awslambda  # Renamed from lambda to avoid keyword conflict
from . import ecs
from . import stepfunction
from . import dynamodb
from . import eventbridge
from . import parameterstore
from . import sqs
from . import ec2
from . import cloudwatch

__all__ = [
    'AWSClientManager',
    'AWSResourceError', 
    'ResourceNotFoundError',
    's3',
    'awslambda',
    'ecs',
    'stepfunction',
    'dynamodb',
    'eventbridge',
    'parameterstore',
    'sqs',
    'ec2',
    'cloudwatch'
]
