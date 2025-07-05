"""
EC2 module for AWS resource exploration.

This module provides read and write operations for Amazon EC2 instances,
security groups, key pairs, and other EC2 resources.
"""

from .read.ec2_reader import EC2Reader
from .write.ec2_writer import EC2Writer

__all__ = ['EC2Reader', 'EC2Writer']
