"""
AWS EventBridge service package for reading and writing EventBridge resources.
"""

from .read.eb_reader import EventBridgeReader
from .write.eb_writer import EventBridgeWriter

__all__ = ['EventBridgeReader', 'EventBridgeWriter']
