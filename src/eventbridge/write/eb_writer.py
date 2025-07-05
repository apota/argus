"""
EventBridge Writer Module
Provides functionality to create, update, and manage AWS EventBridge rules and targets.
"""

import json
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, AWSPermissionException, ResourceNotFoundError


class EventBridgeWriter:
    """
    Handles write operations for AWS EventBridge.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize the EventBridge writer.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.client = client_manager.get_client('events')
    
    def create_event_bus(self, name: str, event_source_name: Optional[str] = None,
                        tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new EventBridge event bus.
        
        Args:
            name (str): Name of the event bus.
            event_source_name (str, optional): Event source name for partner event bus.
            tags (List[Dict[str, str]], optional): Tags for the event bus.
        
        Returns:
            Dict[str, Any]: Event bus creation response.
        
        Raises:
            AWSResourceError: If event bus creation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {'Name': name}
            
            if event_source_name:
                params['EventSourceName'] = event_source_name
            
            if tags:
                params['Tags'] = tags
            
            response = self.client.create_event_bus(**params)
            
            return {
                'event_bus_arn': response['EventBusArn'],
                'name': name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to create event bus '{name}': {str(e)}") from e
            elif error_code == 'ResourceAlreadyExistsException':
                raise AWSResourceError(f"Event bus '{name}' already exists") from e
            else:
                raise AWSResourceError(f"Failed to create event bus '{name}': {str(e)}") from e
    
    def delete_event_bus(self, name: str) -> bool:
        """
        Delete an EventBridge event bus.
        
        Args:
            name (str): Name of the event bus to delete.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            AWSResourceError: If event bus deletion fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If event bus doesn't exist.
        """
        try:
            self.client.delete_event_bus(Name=name)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete event bus '{name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Event bus '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete event bus '{name}': {str(e)}") from e
    
    def put_rule(self, name: str, event_pattern: Optional[Dict[str, Any]] = None,
                schedule_expression: Optional[str] = None, state: str = 'ENABLED',
                description: Optional[str] = None, event_bus_name: Optional[str] = None,
                tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create or update an EventBridge rule.
        
        Args:
            name (str): Name of the rule.
            event_pattern (Dict[str, Any], optional): Event pattern for the rule.
            schedule_expression (str, optional): Schedule expression for time-based rules.
            state (str): State of the rule ('ENABLED' or 'DISABLED').
            description (str, optional): Description of the rule.
            event_bus_name (str, optional): Name of the event bus.
            tags (List[Dict[str, str]], optional): Tags for the rule.
        
        Returns:
            Dict[str, Any]: Rule creation response.
        
        Raises:
            AWSResourceError: If rule creation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {
                'Name': name,
                'State': state
            }
            
            if event_pattern:
                params['EventPattern'] = json.dumps(event_pattern)
            
            if schedule_expression:
                params['ScheduleExpression'] = schedule_expression
            
            if description:
                params['Description'] = description
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            if tags:
                params['Tags'] = tags
            
            response = self.client.put_rule(**params)
            
            return {
                'rule_arn': response['RuleArn'],
                'name': name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to create rule '{name}': {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to create rule '{name}': {str(e)}") from e
    
    def delete_rule(self, name: str, event_bus_name: Optional[str] = None,
                   force: bool = False) -> bool:
        """
        Delete an EventBridge rule.
        
        Args:
            name (str): Name of the rule to delete.
            event_bus_name (str, optional): Name of the event bus.
            force (bool): Whether to force deletion even if targets exist.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            AWSResourceError: If rule deletion fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If rule doesn't exist.
        """
        try:
            params = {'Name': name}
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            if force:
                params['Force'] = force
            
            self.client.delete_rule(**params)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete rule '{name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Rule '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete rule '{name}': {str(e)}") from e
    
    def put_targets(self, rule: str, targets: List[Dict[str, Any]],
                   event_bus_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Add targets to an EventBridge rule.
        
        Args:
            rule (str): Name of the rule.
            targets (List[Dict[str, Any]]): List of targets to add.
            event_bus_name (str, optional): Name of the event bus.
        
        Returns:
            Dict[str, Any]: Put targets response.
        
        Raises:
            AWSResourceError: If adding targets fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If rule doesn't exist.
        """
        try:
            params = {
                'Rule': rule,
                'Targets': targets
            }
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            response = self.client.put_targets(**params)
            
            return {
                'failed_entry_count': response.get('FailedEntryCount', 0),
                'failed_entries': response.get('FailedEntries', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to add targets to rule '{rule}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Rule '{rule}' not found") from e
            else:
                raise AWSResourceError(f"Failed to add targets to rule '{rule}': {str(e)}") from e
    
    def remove_targets(self, rule: str, ids: List[str],
                      event_bus_name: Optional[str] = None,
                      force: bool = False) -> Dict[str, Any]:
        """
        Remove targets from an EventBridge rule.
        
        Args:
            rule (str): Name of the rule.
            ids (List[str]): List of target IDs to remove.
            event_bus_name (str, optional): Name of the event bus.
            force (bool): Whether to force removal.
        
        Returns:
            Dict[str, Any]: Remove targets response.
        
        Raises:
            AWSResourceError: If removing targets fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If rule doesn't exist.
        """
        try:
            params = {
                'Rule': rule,
                'Ids': ids
            }
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            if force:
                params['Force'] = force
            
            response = self.client.remove_targets(**params)
            
            return {
                'failed_entry_count': response.get('FailedEntryCount', 0),
                'failed_entries': response.get('FailedEntries', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to remove targets from rule '{rule}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Rule '{rule}' not found") from e
            else:
                raise AWSResourceError(f"Failed to remove targets from rule '{rule}': {str(e)}") from e
    
    def put_events(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send custom events to EventBridge.
        
        Args:
            entries (List[Dict[str, Any]]): List of event entries to send.
        
        Returns:
            Dict[str, Any]: Put events response.
        
        Raises:
            AWSResourceError: If sending events fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.put_events(Entries=entries)
            
            return {
                'failed_entry_count': response.get('FailedEntryCount', 0),
                'entries': response.get('Entries', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to send events: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to send events: {str(e)}") from e
    
    def enable_rule(self, name: str, event_bus_name: Optional[str] = None) -> bool:
        """
        Enable an EventBridge rule.
        
        Args:
            name (str): Name of the rule to enable.
            event_bus_name (str, optional): Name of the event bus.
        
        Returns:
            bool: True if enabling was successful.
        
        Raises:
            AWSResourceError: If enabling rule fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If rule doesn't exist.
        """
        try:
            params = {'Name': name}
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            self.client.enable_rule(**params)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to enable rule '{name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Rule '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to enable rule '{name}': {str(e)}") from e
    
    def disable_rule(self, name: str, event_bus_name: Optional[str] = None) -> bool:
        """
        Disable an EventBridge rule.
        
        Args:
            name (str): Name of the rule to disable.
            event_bus_name (str, optional): Name of the event bus.
        
        Returns:
            bool: True if disabling was successful.
        
        Raises:
            AWSResourceError: If disabling rule fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If rule doesn't exist.
        """
        try:
            params = {'Name': name}
            
            if event_bus_name:
                params['EventBusName'] = event_bus_name
            
            self.client.disable_rule(**params)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to disable rule '{name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Rule '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to disable rule '{name}': {str(e)}") from e
    
    def tag_resource(self, resource_arn: str, tags: List[Dict[str, str]]) -> bool:
        """
        Add tags to an EventBridge resource.
        
        Args:
            resource_arn (str): ARN of the resource to tag.
            tags (List[Dict[str, str]]): List of tags to add.
        
        Returns:
            bool: True if tagging was successful.
        
        Raises:
            AWSResourceError: If tagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.tag_resource(
                ResourceARN=resource_arn,
                Tags=tags
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to tag resource: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to tag resource: {str(e)}") from e
    
    def untag_resource(self, resource_arn: str, tag_keys: List[str]) -> bool:
        """
        Remove tags from an EventBridge resource.
        
        Args:
            resource_arn (str): ARN of the resource to untag.
            tag_keys (List[str]): List of tag keys to remove.
        
        Returns:
            bool: True if untagging was successful.
        
        Raises:
            AWSResourceError: If untagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.untag_resource(
                ResourceARN=resource_arn,
                TagKeys=tag_keys
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to untag resource: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to untag resource: {str(e)}") from e
