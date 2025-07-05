"""
EventBridge Reader Module

This module provides functionality for reading and exploring AWS EventBridge resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class EventBridgeReader:
    """
    A class for reading AWS EventBridge resources.
    
    This class provides methods to list and retrieve information about
    event buses, rules, and targets.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the EventBridge reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.events_client = self.client_manager.get_client('events')
    
    def list_event_buses(self, name_prefix: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all event buses in the account.
        
        Args:
            name_prefix: Optional prefix to filter event bus names
            limit: Maximum number of event buses to return
            
        Returns:
            List of event bus configurations
            
        Raises:
            AWSResourceError: If there's an error listing event buses
        """
        try:
            logger.info("Listing EventBridge event buses")
            
            kwargs = {}
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            if limit:
                kwargs['Limit'] = limit
            
            response = self.events_client.list_event_buses(**kwargs)
            event_buses = response.get('EventBuses', [])
            
            logger.info("Found %d EventBridge event buses", len(event_buses))
            return event_buses
            
        except ClientError as e:
            error_message = f"Failed to list EventBridge event buses: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_event_bus(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific event bus.
        
        Args:
            name: Name of the event bus (uses default if not specified)
            
        Returns:
            Event bus configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the event bus doesn't exist
            AWSResourceError: If there's an error retrieving the event bus
        """
        try:
            logger.info("Describing EventBridge event bus: %s", name or 'default')
            
            kwargs = {}
            if name:
                kwargs['Name'] = name
            
            response = self.events_client.describe_event_bus(**kwargs)
            
            logger.info("Retrieved event bus information for %s", name or 'default')
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"EventBridge event bus not found: {name or 'default'}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe EventBridge event bus {name or 'default'}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_rules(self, event_bus_name: Optional[str] = None,
                  name_prefix: Optional[str] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List EventBridge rules.
        
        Args:
            event_bus_name: Name of the event bus (uses default if not specified)
            name_prefix: Optional prefix to filter rule names
            limit: Maximum number of rules to return
            
        Returns:
            List of rule configurations
            
        Raises:
            AWSResourceError: If there's an error listing rules
        """
        try:
            logger.info("Listing EventBridge rules for event bus: %s", event_bus_name or 'default')
            
            kwargs = {}
            if event_bus_name:
                kwargs['EventBusName'] = event_bus_name
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            if limit:
                kwargs['Limit'] = limit
            
            paginator = self.events_client.get_paginator('list_rules')
            page_iterator = paginator.paginate(**kwargs)
            
            rules = []
            for page in page_iterator:
                rules.extend(page.get('Rules', []))
            
            logger.info("Found %d EventBridge rules", len(rules))
            return rules
            
        except ClientError as e:
            error_message = f"Failed to list EventBridge rules: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_rule(self, name: str, event_bus_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific rule.
        
        Args:
            name: Name of the rule
            event_bus_name: Name of the event bus (uses default if not specified)
            
        Returns:
            Rule configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the rule doesn't exist
            AWSResourceError: If there's an error retrieving the rule
        """
        try:
            logger.info("Describing EventBridge rule: %s", name)
            
            kwargs = {'Name': name}
            if event_bus_name:
                kwargs['EventBusName'] = event_bus_name
            
            response = self.events_client.describe_rule(**kwargs)
            
            logger.info("Retrieved rule information for %s", name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"EventBridge rule not found: {name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe EventBridge rule {name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_targets_by_rule(self, rule: str, event_bus_name: Optional[str] = None,
                           limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List targets for a specific rule.
        
        Args:
            rule: Name of the rule
            event_bus_name: Name of the event bus (uses default if not specified)
            limit: Maximum number of targets to return
            
        Returns:
            List of target configurations
            
        Raises:
            ResourceNotFoundError: If the rule doesn't exist
            AWSResourceError: If there's an error listing targets
        """
        try:
            logger.info("Listing targets for EventBridge rule: %s", rule)
            
            kwargs = {'Rule': rule}
            if event_bus_name:
                kwargs['EventBusName'] = event_bus_name
            if limit:
                kwargs['Limit'] = limit
            
            paginator = self.events_client.get_paginator('list_targets_by_rule')
            page_iterator = paginator.paginate(**kwargs)
            
            targets = []
            for page in page_iterator:
                targets.extend(page.get('Targets', []))
            
            logger.info("Found %d targets for rule %s", len(targets), rule)
            return targets
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"EventBridge rule not found: {rule}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list targets for EventBridge rule {rule}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_partner_event_sources(self, name_prefix: Optional[str] = None,
                                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List partner event sources.
        
        Args:
            name_prefix: Optional prefix to filter event source names
            limit: Maximum number of event sources to return
            
        Returns:
            List of partner event source configurations
            
        Raises:
            AWSResourceError: If there's an error listing partner event sources
        """
        try:
            logger.info("Listing EventBridge partner event sources")
            
            kwargs = {}
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            if limit:
                kwargs['Limit'] = limit
            
            response = self.events_client.list_partner_event_sources(**kwargs)
            sources = response.get('PartnerEventSources', [])
            
            logger.info("Found %d EventBridge partner event sources", len(sources))
            return sources
            
        except ClientError as e:
            error_message = f"Failed to list EventBridge partner event sources: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_replays(self, name_prefix: Optional[str] = None,
                    state: Optional[str] = None,
                    event_source_arn: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List EventBridge replays.
        
        Args:
            name_prefix: Optional prefix to filter replay names
            state: Optional state filter (STARTING, RUNNING, CANCELLING, COMPLETED, CANCELLED, FAILED)
            event_source_arn: Optional event source ARN filter
            limit: Maximum number of replays to return
            
        Returns:
            List of replay configurations
            
        Raises:
            AWSResourceError: If there's an error listing replays
        """
        try:
            logger.info("Listing EventBridge replays")
            
            kwargs = {}
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            if state:
                kwargs['State'] = state
            if event_source_arn:
                kwargs['EventSourceArn'] = event_source_arn
            if limit:
                kwargs['Limit'] = limit
            
            response = self.events_client.list_replays(**kwargs)
            replays = response.get('Replays', [])
            
            logger.info("Found %d EventBridge replays", len(replays))
            return replays
            
        except ClientError as e:
            error_message = f"Failed to list EventBridge replays: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_replay(self, replay_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific replay.
        
        Args:
            replay_name: Name of the replay
            
        Returns:
            Replay configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the replay doesn't exist
            AWSResourceError: If there's an error retrieving the replay
        """
        try:
            logger.info("Describing EventBridge replay: %s", replay_name)
            
            response = self.events_client.describe_replay(ReplayName=replay_name)
            
            logger.info("Retrieved replay information for %s", replay_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"EventBridge replay not found: {replay_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe EventBridge replay {replay_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_archives(self, name_prefix: Optional[str] = None,
                     event_source_arn: Optional[str] = None,
                     state: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List EventBridge archives.
        
        Args:
            name_prefix: Optional prefix to filter archive names
            event_source_arn: Optional event source ARN filter
            state: Optional state filter (ENABLED, DISABLED, CREATING, UPDATING, CREATE_FAILED, UPDATE_FAILED)
            limit: Maximum number of archives to return
            
        Returns:
            List of archive configurations
            
        Raises:
            AWSResourceError: If there's an error listing archives
        """
        try:
            logger.info("Listing EventBridge archives")
            
            kwargs = {}
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            if event_source_arn:
                kwargs['EventSourceArn'] = event_source_arn
            if state:
                kwargs['State'] = state
            if limit:
                kwargs['Limit'] = limit
            
            response = self.events_client.list_archives(**kwargs)
            archives = response.get('Archives', [])
            
            logger.info("Found %d EventBridge archives", len(archives))
            return archives
            
        except ClientError as e:
            error_message = f"Failed to list EventBridge archives: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_archive(self, archive_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific archive.
        
        Args:
            archive_name: Name of the archive
            
        Returns:
            Archive configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the archive doesn't exist
            AWSResourceError: If there's an error retrieving the archive
        """
        try:
            logger.info("Describing EventBridge archive: %s", archive_name)
            
            response = self.events_client.describe_archive(ArchiveName=archive_name)
            
            logger.info("Retrieved archive information for %s", archive_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"EventBridge archive not found: {archive_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe EventBridge archive {archive_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
