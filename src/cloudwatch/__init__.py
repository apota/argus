"""
CloudWatch module for AWS resource exploration.

This module provides read operations for Amazon CloudWatch logs, metrics,
and alarms. Write operations are not supported for CloudWatch.
"""

from .read.cloudwatch_reader import CloudWatchReader

__all__ = ['CloudWatchReader']
