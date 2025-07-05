"""
SQS Reader Module

This module provides functionality for reading and exploring AWS SQS resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class SQSReader:
    """
    A class for reading AWS SQS resources.
    
    This class provides methods to list and retrieve information about
    SQS queues, messages, and dead letter queues.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the SQS reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.sqs_client = self.client_manager.get_client('sqs')
    
    def list_queues(self, queue_name_prefix: Optional[str] = None,
                   max_results: Optional[int] = None) -> List[str]:
        """
        List all SQS queues in the account.
        
        Args:
            queue_name_prefix: Optional prefix to filter queue names
            max_results: Maximum number of queues to return
            
        Returns:
            List of queue URLs
            
        Raises:
            AWSResourceError: If there's an error listing queues
        """
        try:
            logger.info("Listing SQS queues")
            
            kwargs = {}
            if queue_name_prefix:
                kwargs['QueueNamePrefix'] = queue_name_prefix
            if max_results:
                kwargs['MaxResults'] = max_results
            
            response = self.sqs_client.list_queues(**kwargs)
            queue_urls = response.get('QueueUrls', [])
            
            logger.info("Found %d SQS queues", len(queue_urls))
            return queue_urls
            
        except ClientError as e:
            error_message = f"Failed to list SQS queues: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_queue_url(self, queue_name: str, queue_owner_aws_account_id: Optional[str] = None) -> str:
        """
        Get the URL for a specific queue.
        
        Args:
            queue_name: Name of the SQS queue
            queue_owner_aws_account_id: Optional AWS account ID of the queue owner
            
        Returns:
            Queue URL
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error retrieving the queue URL
        """
        try:
            logger.info("Getting SQS queue URL: %s", queue_name)
            
            kwargs = {'QueueName': queue_name}
            if queue_owner_aws_account_id:
                kwargs['QueueOwnerAWSAccountId'] = queue_owner_aws_account_id
            
            response = self.sqs_client.get_queue_url(**kwargs)
            queue_url = response.get('QueueUrl', '')
            
            logger.info("Retrieved queue URL for %s", queue_name)
            return queue_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                error_message = f"SQS queue not found: {queue_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get SQS queue URL {queue_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_queue_attributes(self, queue_url: str, 
                           attribute_names: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Get attributes for a specific queue.
        
        Args:
            queue_url: URL of the SQS queue
            attribute_names: Optional list of attribute names to retrieve (default: All)
            
        Returns:
            Dictionary of queue attributes
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error retrieving queue attributes
        """
        try:
            logger.info("Getting SQS queue attributes: %s", queue_url)
            
            kwargs = {'QueueUrl': queue_url}
            if attribute_names:
                kwargs['AttributeNames'] = attribute_names
            else:
                kwargs['AttributeNames'] = ['All']
            
            response = self.sqs_client.get_queue_attributes(**kwargs)
            attributes = response.get('Attributes', {})
            
            logger.info("Retrieved %d attributes for queue", len(attributes))
            return attributes
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                error_message = f"SQS queue not found: {queue_url}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get SQS queue attributes {queue_url}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def receive_messages(self, queue_url: str, max_number_of_messages: int = 1,
                        wait_time_seconds: int = 0, visibility_timeout_seconds: Optional[int] = None,
                        message_attribute_names: Optional[List[str]] = None,
                        attribute_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Receive messages from a queue.
        
        Args:
            queue_url: URL of the SQS queue
            max_number_of_messages: Maximum number of messages to receive (1-10)
            wait_time_seconds: Wait time for long polling (0-20 seconds)
            visibility_timeout_seconds: Visibility timeout for received messages
            message_attribute_names: Message attribute names to retrieve
            attribute_names: System attribute names to retrieve
            
        Returns:
            List of received messages
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error receiving messages
        """
        try:
            logger.info("Receiving messages from SQS queue: %s", queue_url)
            
            kwargs = {
                'QueueUrl': queue_url,
                'MaxNumberOfMessages': max_number_of_messages,
                'WaitTimeSeconds': wait_time_seconds
            }
            
            if visibility_timeout_seconds is not None:
                kwargs['VisibilityTimeoutSeconds'] = visibility_timeout_seconds
            if message_attribute_names:
                kwargs['MessageAttributeNames'] = message_attribute_names
            if attribute_names:
                kwargs['AttributeNames'] = attribute_names
            
            response = self.sqs_client.receive_message(**kwargs)
            messages = response.get('Messages', [])
            
            logger.info("Received %d messages from queue", len(messages))
            return messages
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                error_message = f"SQS queue not found: {queue_url}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to receive messages from SQS queue {queue_url}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def peek_messages(self, queue_url: str, max_number_of_messages: int = 1) -> List[Dict[str, Any]]:
        """
        Peek at messages in a queue without removing them (using visibility timeout of 0).
        
        Args:
            queue_url: URL of the SQS queue
            max_number_of_messages: Maximum number of messages to peek at (1-10)
            
        Returns:
            List of messages (visibility timeout set to 0 for immediate re-availability)
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error peeking at messages
        """
        try:
            logger.info("Peeking at messages in SQS queue: %s", queue_url)
            
            messages = self.receive_messages(
                queue_url=queue_url,
                max_number_of_messages=max_number_of_messages,
                visibility_timeout_seconds=0  # Make messages immediately available again
            )
            
            logger.info("Peeked at %d messages in queue", len(messages))
            return messages
            
        except (ResourceNotFoundError, AWSResourceError):
            raise
    
    def get_queue_message_count(self, queue_url: str) -> Dict[str, int]:
        """
        Get message counts for a queue.
        
        Args:
            queue_url: URL of the SQS queue
            
        Returns:
            Dictionary with message count information
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error retrieving message counts
        """
        try:
            logger.info("Getting message counts for SQS queue: %s", queue_url)
            
            attributes = self.get_queue_attributes(
                queue_url,
                ['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible', 
                 'ApproximateNumberOfMessagesDelayed']
            )
            
            counts = {
                'visible_messages': int(attributes.get('ApproximateNumberOfMessages', 0)),
                'invisible_messages': int(attributes.get('ApproximateNumberOfMessagesNotVisible', 0)),
                'delayed_messages': int(attributes.get('ApproximateNumberOfMessagesDelayed', 0))
            }
            
            total_messages = sum(counts.values())
            counts['total_messages'] = total_messages
            
            logger.info("Queue has %d total messages", total_messages)
            return counts
            
        except (ResourceNotFoundError, AWSResourceError):
            raise
    
    def list_dead_letter_source_queues(self, queue_url: str) -> List[str]:
        """
        List source queues that have the specified queue as their dead letter queue.
        
        Args:
            queue_url: URL of the dead letter queue
            
        Returns:
            List of source queue URLs
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error listing source queues
        """
        try:
            logger.info("Listing dead letter source queues for: %s", queue_url)
            
            response = self.sqs_client.list_dead_letter_source_queues(QueueUrl=queue_url)
            source_queues = response.get('queueUrls', [])
            
            logger.info("Found %d source queues for dead letter queue", len(source_queues))
            return source_queues
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                error_message = f"SQS queue not found: {queue_url}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list dead letter source queues {queue_url}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_queue_tags(self, queue_url: str) -> Dict[str, str]:
        """
        List tags for a specific queue.
        
        Args:
            queue_url: URL of the SQS queue
            
        Returns:
            Dictionary of queue tags
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error retrieving queue tags
        """
        try:
            logger.info("Listing tags for SQS queue: %s", queue_url)
            
            response = self.sqs_client.list_queue_tags(QueueUrl=queue_url)
            tags = response.get('Tags', {})
            
            logger.info("Found %d tags for queue", len(tags))
            return tags
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                error_message = f"SQS queue not found: {queue_url}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list SQS queue tags {queue_url}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_queue_info_summary(self, queue_url: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of queue information.
        
        Args:
            queue_url: URL of the SQS queue
            
        Returns:
            Dictionary with comprehensive queue information
            
        Raises:
            ResourceNotFoundError: If the queue doesn't exist
            AWSResourceError: If there's an error retrieving queue information
        """
        try:
            logger.info("Getting comprehensive info for SQS queue: %s", queue_url)
            
            # Extract queue name from URL
            queue_name = queue_url.split('/')[-1]
            
            # Get attributes
            attributes = self.get_queue_attributes(queue_url)
            
            # Get message counts
            message_counts = self.get_queue_message_count(queue_url)
            
            # Get tags
            try:
                tags = self.list_queue_tags(queue_url)
            except AWSResourceError:
                tags = {}
            
            # Get dead letter source queues if this is a DLQ
            try:
                source_queues = self.list_dead_letter_source_queues(queue_url)
            except AWSResourceError:
                source_queues = []
            
            summary = {
                'queue_name': queue_name,
                'queue_url': queue_url,
                'attributes': attributes,
                'message_counts': message_counts,
                'tags': tags,
                'dead_letter_source_queues': source_queues,
                'is_fifo': queue_name.endswith('.fifo'),
                'is_dead_letter_queue': len(source_queues) > 0
            }
            
            logger.info("Retrieved comprehensive info for queue %s", queue_name)
            return summary
            
        except (ResourceNotFoundError, AWSResourceError):
            raise
