"""
Elastic Beanstalk module for AWS resource exploration.

This module provides read and write operations for AWS Elastic Beanstalk
applications, environments, application versions, and configurations.
"""

from .read.ebs_reader import EBSReader
from .write.ebs_writer import EBSWriter

__all__ = ['EBSReader', 'EBSWriter']
