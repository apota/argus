"""
AWS Lambda service package for reading and writing Lambda resources.
"""

from .read.lambda_reader import LambdaReader
from .write.lambda_writer import LambdaWriter

__all__ = ['LambdaReader', 'LambdaWriter']
