"""
AWS DynamoDB service package for reading and writing DynamoDB resources.
"""

from .read.dynamodb_reader import DynamoDBReader
from .write.dynamodb_writer import DynamoDBWriter

__all__ = ['DynamoDBReader', 'DynamoDBWriter']
