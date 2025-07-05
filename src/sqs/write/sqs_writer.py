"""
SQS Writer Module
Provides functionality to create, update, and manage AWS SQS queues and messages.
"""

from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

from ...common.aws_client import AWSClientManager
from ...common.exceptions import AWSResourceError, AWSPermissionException, ResourceNotFoundError


class SQSWriter:
    """
    Handles write operations for AWS SQS.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize the SQS writer.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.client = client_manager.get_client('sqs')
    
    def create_queue(self, queue_name: str, attributes: Optional[Dict[str, str]] = None,
                    tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new SQS queue.
        
        Args:
            queue_name (str): Name of the queue to create.
            attributes (Dict[str, str], optional): Queue attributes.
            tags (Dict[str, str], optional): Tags for the queue.
        
        Returns:
            Dict[str, Any]: Queue creation response.
        
        Raises:
            AWSResourceError: If queue creation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {'QueueName': queue_name}
            
            if attributes:
                params['Attributes'] = attributes
            
            if tags:
                params['tags'] = tags
            
            response = self.client.create_queue(**params)
            
            return {
                'queue_url': response['QueueUrl'],
                'queue_name': queue_name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to create queue '{queue_name}': {str(e)}") from e
            elif error_code == 'QueueNameExists':
                raise AWSResourceError(f"Queue '{queue_name}' already exists") from e
            else:
                raise AWSResourceError(f"Failed to create queue '{queue_name}': {str(e)}") from e
    
    def delete_queue(self, queue_url: str) -> bool:
        """
        Delete an SQS queue.
        
        Args:
            queue_url (str): URL of the queue to delete.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            AWSResourceError: If queue deletion fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.delete_queue(QueueUrl=queue_url)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete queue: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete queue: {str(e)}") from e
    
    def send_message(self, queue_url: str, message_body: str,
                    delay_seconds: Optional[int] = None,
                    message_attributes: Optional[Dict[str, Any]] = None,
                    message_system_attributes: Optional[Dict[str, Any]] = None,
                    message_deduplication_id: Optional[str] = None,
                    message_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to an SQS queue.
        
        Args:
            queue_url (str): URL of the queue.
            message_body (str): Body of the message.
            delay_seconds (int, optional): Delay before message becomes available.
            message_attributes (Dict[str, Any], optional): Message attributes.
            message_system_attributes (Dict[str, Any], optional): System attributes.
            message_deduplication_id (str, optional): Deduplication ID for FIFO queues.
            message_group_id (str, optional): Group ID for FIFO queues.
        
        Returns:
            Dict[str, Any]: Send message response.
        
        Raises:
            AWSResourceError: If sending message fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body
            }
            
            if delay_seconds is not None:
                params['DelaySeconds'] = delay_seconds
            
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            if message_system_attributes:
                params['MessageSystemAttributes'] = message_system_attributes
            
            if message_deduplication_id:
                params['MessageDeduplicationId'] = message_deduplication_id
            
            if message_group_id:
                params['MessageGroupId'] = message_group_id
            
            response = self.client.send_message(**params)
            
            return {
                'message_id': response['MessageId'],
                'md5_of_body': response['MD5OfBody'],
                'sequence_number': response.get('SequenceNumber')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to send message: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to send message: {str(e)}") from e
    
    def send_message_batch(self, queue_url: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send multiple messages to an SQS queue in a batch.
        
        Args:
            queue_url (str): URL of the queue.
            entries (List[Dict[str, Any]]): List of message entries.
        
        Returns:
            Dict[str, Any]: Batch send response.
        
        Raises:
            AWSResourceError: If batch send fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.send_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            
            return {
                'successful': response.get('Successful', []),
                'failed': response.get('Failed', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to send message batch: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to send message batch: {str(e)}") from e
    
    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """
        Delete a message from an SQS queue.
        
        Args:
            queue_url (str): URL of the queue.
            receipt_handle (str): Receipt handle of the message to delete.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            AWSResourceError: If message deletion fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete message: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete message: {str(e)}") from e
    
    def delete_message_batch(self, queue_url: str, entries: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Delete multiple messages from an SQS queue in a batch.
        
        Args:
            queue_url (str): URL of the queue.
            entries (List[Dict[str, str]]): List of receipt handles to delete.
        
        Returns:
            Dict[str, Any]: Batch delete response.
        
        Raises:
            AWSResourceError: If batch delete fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.delete_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            
            return {
                'successful': response.get('Successful', []),
                'failed': response.get('Failed', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete message batch: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete message batch: {str(e)}") from e
    
    def change_message_visibility(self, queue_url: str, receipt_handle: str,
                                visibility_timeout: int) -> bool:
        """
        Change the visibility timeout of a message in an SQS queue.
        
        Args:
            queue_url (str): URL of the queue.
            receipt_handle (str): Receipt handle of the message.
            visibility_timeout (int): New visibility timeout in seconds.
        
        Returns:
            bool: True if change was successful.
        
        Raises:
            AWSResourceError: If changing visibility fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to change message visibility: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to change message visibility: {str(e)}") from e
    
    def change_message_visibility_batch(self, queue_url: str,
                                      entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Change the visibility timeout of multiple messages in a batch.
        
        Args:
            queue_url (str): URL of the queue.
            entries (List[Dict[str, Any]]): List of visibility change entries.
        
        Returns:
            Dict[str, Any]: Batch visibility change response.
        
        Raises:
            AWSResourceError: If batch visibility change fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.change_message_visibility_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            
            return {
                'successful': response.get('Successful', []),
                'failed': response.get('Failed', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to change message visibility batch: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to change message visibility batch: {str(e)}") from e
    
    def set_queue_attributes(self, queue_url: str, attributes: Dict[str, str]) -> bool:
        """
        Set attributes for an SQS queue.
        
        Args:
            queue_url (str): URL of the queue.
            attributes (Dict[str, str]): Queue attributes to set.
        
        Returns:
            bool: True if setting attributes was successful.
        
        Raises:
            AWSResourceError: If setting attributes fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes=attributes
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to set queue attributes: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to set queue attributes: {str(e)}") from e
    
    def purge_queue(self, queue_url: str) -> bool:
        """
        Purge all messages from an SQS queue.
        
        Args:
            queue_url (str): URL of the queue to purge.
        
        Returns:
            bool: True if purging was successful.
        
        Raises:
            AWSResourceError: If purging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.purge_queue(QueueUrl=queue_url)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to purge queue: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to purge queue: {str(e)}") from e
    
    def tag_queue(self, queue_url: str, tags: Dict[str, str]) -> bool:
        """
        Add tags to an SQS queue.
        
        Args:
            queue_url (str): URL of the queue to tag.
            tags (Dict[str, str]): Tags to add to the queue.
        
        Returns:
            bool: True if tagging was successful.
        
        Raises:
            AWSResourceError: If tagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.tag_queue(
                QueueUrl=queue_url,
                Tags=tags
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to tag queue: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to tag queue: {str(e)}") from e
    
    def untag_queue(self, queue_url: str, tag_keys: List[str]) -> bool:
        """
        Remove tags from an SQS queue.
        
        Args:
            queue_url (str): URL of the queue to untag.
            tag_keys (List[str]): List of tag keys to remove.
        
        Returns:
            bool: True if untagging was successful.
        
        Raises:
            AWSResourceError: If untagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.untag_queue(
                QueueUrl=queue_url,
                TagKeys=tag_keys
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to untag queue: {str(e)}") from e
            elif error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise ResourceNotFoundError(f"Queue '{queue_url}' not found") from e
            else:
                raise AWSResourceError(f"Failed to untag queue: {str(e)}") from e
