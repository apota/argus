"""
DynamoDB Reader Module

This module provides functionality for reading and exploring AWS DynamoDB resources.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class DynamoDBReader:
    """
    A class for reading AWS DynamoDB resources.
    
    This class provides methods to list and retrieve information about
    DynamoDB tables, items, and global secondary indexes.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the DynamoDB reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.dynamodb_client = self.client_manager.get_client('dynamodb')
        self.dynamodb_resource = self.client_manager.get_resource('dynamodb')
    
    def list_tables(self, limit: Optional[int] = None) -> List[str]:
        """
        List all DynamoDB tables in the account.
        
        Args:
            limit: Maximum number of tables to return
            
        Returns:
            List of table names
            
        Raises:
            AWSResourceError: If there's an error listing tables
        """
        try:
            logger.info("Listing DynamoDB tables")
            
            kwargs = {}
            if limit:
                kwargs['Limit'] = limit
            
            paginator = self.dynamodb_client.get_paginator('list_tables')
            page_iterator = paginator.paginate(
                PaginationConfig={'MaxItems': limit} if limit else {}
            )
            
            tables = []
            for page in page_iterator:
                tables.extend(page.get('TableNames', []))
            
            logger.info("Found %d DynamoDB tables", len(tables))
            return tables
            
        except ClientError as e:
            error_message = f"Failed to list DynamoDB tables: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table
            
        Returns:
            Table configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the table doesn't exist
            AWSResourceError: If there's an error retrieving the table
        """
        try:
            logger.info("Describing DynamoDB table: %s", table_name)
            
            response = self.dynamodb_client.describe_table(TableName=table_name)
            
            logger.info("Retrieved table information for %s", table_name)
            return response.get('Table', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"DynamoDB table not found: {table_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe DynamoDB table {table_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_table_item_count(self, table_name: str) -> int:
        """
        Get the approximate item count for a table.
        
        Args:
            table_name: Name of the DynamoDB table
            
        Returns:
            Approximate number of items in the table
            
        Raises:
            ResourceNotFoundError: If the table doesn't exist
            AWSResourceError: If there's an error retrieving the table info
        """
        try:
            table_info = self.describe_table(table_name)
            return table_info.get('ItemCount', 0)
            
        except (ResourceNotFoundError, AWSResourceError):
            raise
    
    def scan_table(self, table_name: str, limit: Optional[int] = None,
                  filter_expression: Optional[str] = None,
                  expression_attribute_names: Optional[Dict[str, str]] = None,
                  expression_attribute_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Scan a DynamoDB table and return items.
        
        Args:
            table_name: Name of the DynamoDB table
            limit: Maximum number of items to return
            filter_expression: Optional filter expression
            expression_attribute_names: Attribute name substitutions
            expression_attribute_values: Attribute value substitutions
            
        Returns:
            List of items from the table
            
        Raises:
            ResourceNotFoundError: If the table doesn't exist
            AWSResourceError: If there's an error scanning the table
        """
        try:
            logger.info("Scanning DynamoDB table: %s", table_name)
            
            kwargs = {'TableName': table_name}
            
            if limit:
                kwargs['Limit'] = limit
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            paginator = self.dynamodb_client.get_paginator('scan')
            page_iterator = paginator.paginate(**kwargs)
            
            items = []
            for page in page_iterator:
                items.extend(page.get('Items', []))
            
            logger.info("Scanned %d items from table %s", len(items), table_name)
            return items
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"DynamoDB table not found: {table_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to scan DynamoDB table {table_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def query_table(self, table_name: str, key_condition_expression: str,
                   limit: Optional[int] = None,
                   filter_expression: Optional[str] = None,
                   expression_attribute_names: Optional[Dict[str, str]] = None,
                   expression_attribute_values: Optional[Dict[str, Any]] = None,
                   index_name: Optional[str] = None,
                   scan_index_forward: bool = True) -> List[Dict[str, Any]]:
        """
        Query a DynamoDB table with a key condition.
        
        Args:
            table_name: Name of the DynamoDB table
            key_condition_expression: Key condition expression
            limit: Maximum number of items to return
            filter_expression: Optional filter expression
            expression_attribute_names: Attribute name substitutions
            expression_attribute_values: Attribute value substitutions
            index_name: Name of the index to query
            scan_index_forward: Whether to scan in ascending order
            
        Returns:
            List of items from the query
            
        Raises:
            ResourceNotFoundError: If the table doesn't exist
            AWSResourceError: If there's an error querying the table
        """
        try:
            logger.info("Querying DynamoDB table: %s", table_name)
            
            kwargs = {
                'TableName': table_name,
                'KeyConditionExpression': key_condition_expression,
                'ScanIndexForward': scan_index_forward
            }
            
            if limit:
                kwargs['Limit'] = limit
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            if index_name:
                kwargs['IndexName'] = index_name
            
            paginator = self.dynamodb_client.get_paginator('query')
            page_iterator = paginator.paginate(**kwargs)
            
            items = []
            for page in page_iterator:
                items.extend(page.get('Items', []))
            
            logger.info("Queried %d items from table %s", len(items), table_name)
            return items
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"DynamoDB table not found: {table_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to query DynamoDB table {table_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_item(self, table_name: str, key: Dict[str, Any],
                projection_expression: Optional[str] = None,
                expression_attribute_names: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific item from a DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table
            key: Primary key of the item to retrieve
            projection_expression: Optional projection expression
            expression_attribute_names: Attribute name substitutions
            
        Returns:
            The item if found, None otherwise
            
        Raises:
            ResourceNotFoundError: If the table doesn't exist
            AWSResourceError: If there's an error retrieving the item
        """
        try:
            logger.info("Getting item from DynamoDB table: %s", table_name)
            
            kwargs = {
                'TableName': table_name,
                'Key': key
            }
            
            if projection_expression:
                kwargs['ProjectionExpression'] = projection_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            response = self.dynamodb_client.get_item(**kwargs)
            
            item = response.get('Item')
            if item:
                logger.info("Retrieved item from table %s", table_name)
            else:
                logger.info("Item not found in table %s", table_name)
            
            return item
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"DynamoDB table not found: {table_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get item from DynamoDB table {table_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def batch_get_items(self, request_items: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get multiple items from one or more DynamoDB tables.
        
        Args:
            request_items: Request items specification for batch get
            
        Returns:
            Dictionary mapping table names to lists of items
            
        Raises:
            AWSResourceError: If there's an error retrieving the items
        """
        try:
            logger.info("Batch getting items from DynamoDB tables")
            
            response = self.dynamodb_client.batch_get_item(RequestItems=request_items)
            
            responses = response.get('Responses', {})
            total_items = sum(len(items) for items in responses.values())
            logger.info("Retrieved %d items from batch get operation", total_items)
            
            return responses
            
        except ClientError as e:
            error_message = f"Failed to batch get items from DynamoDB: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_backup(self, backup_arn: str) -> Dict[str, Any]:
        """
        Get detailed information about a DynamoDB backup.
        
        Args:
            backup_arn: ARN of the backup
            
        Returns:
            Backup configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the backup doesn't exist
            AWSResourceError: If there's an error retrieving the backup
        """
        try:
            logger.info("Describing DynamoDB backup: %s", backup_arn)
            
            response = self.dynamodb_client.describe_backup(BackupArn=backup_arn)
            
            logger.info("Retrieved backup information for %s", backup_arn)
            return response.get('BackupDescription', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BackupNotFoundException':
                error_message = f"DynamoDB backup not found: {backup_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe DynamoDB backup {backup_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_backups(self, table_name: Optional[str] = None,
                    time_range_lower_bound: Optional[str] = None,
                    time_range_upper_bound: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List DynamoDB backups.
        
        Args:
            table_name: Optional table name to filter backups
            time_range_lower_bound: Optional lower bound for backup creation time
            time_range_upper_bound: Optional upper bound for backup creation time
            
        Returns:
            List of backup summaries
            
        Raises:
            AWSResourceError: If there's an error listing backups
        """
        try:
            logger.info("Listing DynamoDB backups")
            
            kwargs = {}
            if table_name:
                kwargs['TableName'] = table_name
            if time_range_lower_bound:
                kwargs['TimeRangeLowerBound'] = time_range_lower_bound
            if time_range_upper_bound:
                kwargs['TimeRangeUpperBound'] = time_range_upper_bound
            
            response = self.dynamodb_client.list_backups(**kwargs)
            backups = response.get('BackupSummaries', [])
            
            logger.info("Found %d DynamoDB backups", len(backups))
            return backups
            
        except ClientError as e:
            error_message = f"Failed to list DynamoDB backups: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_global_table(self, global_table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a DynamoDB global table.
        
        Args:
            global_table_name: Name of the global table
            
        Returns:
            Global table configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the global table doesn't exist
            AWSResourceError: If there's an error retrieving the global table
        """
        try:
            logger.info("Describing DynamoDB global table: %s", global_table_name)
            
            response = self.dynamodb_client.describe_global_table(GlobalTableName=global_table_name)
            
            logger.info("Retrieved global table information for %s", global_table_name)
            return response.get('GlobalTableDescription', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'GlobalTableNotFoundException':
                error_message = f"DynamoDB global table not found: {global_table_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe DynamoDB global table {global_table_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_global_tables(self, region_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List DynamoDB global tables.
        
        Args:
            region_name: Optional region name to filter global tables
            
        Returns:
            List of global table summaries
            
        Raises:
            AWSResourceError: If there's an error listing global tables
        """
        try:
            logger.info("Listing DynamoDB global tables")
            
            kwargs = {}
            if region_name:
                kwargs['RegionName'] = region_name
            
            response = self.dynamodb_client.list_global_tables(**kwargs)
            global_tables = response.get('GlobalTables', [])
            
            logger.info("Found %d DynamoDB global tables", len(global_tables))
            return global_tables
            
        except ClientError as e:
            error_message = f"Failed to list DynamoDB global tables: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
