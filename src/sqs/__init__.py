"""
AWS SQS service package for reading and writing SQS resources.
"""

from .read.sqs_reader import SQSReader
from .write.sqs_writer import SQSWriter

__all__ = ['SQSReader', 'SQSWriter']
