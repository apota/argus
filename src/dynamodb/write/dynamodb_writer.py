"""
DynamoDB Writer Module
Provides functionality to create, update, and manage AWS DynamoDB tables and items.
"""

from typing import Dict, Any, Optional, List, Union
from botocore.exceptions import ClientError
from decimal import Decimal

from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, AWSPermissionException, ResourceNotFoundError


class DynamoDBWriter:
    """
    Handles write operations for AWS DynamoDB.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize the DynamoDB writer.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.client = client_manager.get_client('dynamodb')
        self.resource = client_manager.get_resource('dynamodb')
    
    def create_table(self, table_name: str, key_schema: List[Dict[str, str]],
                    attribute_definitions: List[Dict[str, str]],
                    billing_mode: str = 'PAY_PER_REQUEST',
                    provisioned_throughput: Optional[Dict[str, int]] = None,
                    global_secondary_indexes: Optional[List[Dict[str, Any]]] = None,
                    local_secondary_indexes: Optional[List[Dict[str, Any]]] = None,
                    stream_specification: Optional[Dict[str, Any]] = None,
                    sse_specification: Optional[Dict[str, Any]] = None,
                    tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new DynamoDB table.
        
        Args:
            table_name (str): Name of the table to create.
            key_schema (List[Dict[str, str]]): Key schema for the table.
            attribute_definitions (List[Dict[str, str]]): Attribute definitions.
            billing_mode (str): Billing mode ('PAY_PER_REQUEST' or 'PROVISIONED').
            provisioned_throughput (Dict[str, int], optional): Provisioned throughput settings.
            global_secondary_indexes (List[Dict[str, Any]], optional): GSI definitions.
            local_secondary_indexes (List[Dict[str, Any]], optional): LSI definitions.
            stream_specification (Dict[str, Any], optional): DynamoDB Streams settings.
            sse_specification (Dict[str, Any], optional): Server-side encryption settings.
            tags (List[Dict[str, str]], optional): Tags for the table.
        
        Returns:
            Dict[str, Any]: Table creation response.
        
        Raises:
            AWSResourceError: If table creation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'BillingMode': billing_mode
            }
            
            if billing_mode == 'PROVISIONED' and provisioned_throughput:
                params['ProvisionedThroughput'] = provisioned_throughput
            
            if global_secondary_indexes:
                params['GlobalSecondaryIndexes'] = global_secondary_indexes
            
            if local_secondary_indexes:
                params['LocalSecondaryIndexes'] = local_secondary_indexes
            
            if stream_specification:
                params['StreamSpecification'] = stream_specification
            
            if sse_specification:
                params['SSESpecification'] = sse_specification
            
            if tags:
                params['Tags'] = tags
            
            response = self.client.create_table(**params)
            
            return {
                'table_name': table_name,
                'table_arn': response['TableDescription']['TableArn'],
                'table_status': response['TableDescription']['TableStatus'],
                'creation_date_time': response['TableDescription']['CreationDateTime']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to create table '{table_name}': {str(e)}") from e
            elif error_code == 'ResourceInUseException':
                raise AWSResourceError(f"Table '{table_name}' already exists") from e
            else:
                raise AWSResourceError(f"Failed to create table '{table_name}': {str(e)}") from e
    
    def delete_table(self, table_name: str) -> Dict[str, Any]:
        """
        Delete a DynamoDB table.
        
        Args:
            table_name (str): Name of the table to delete.
        
        Returns:
            Dict[str, Any]: Deletion response.
        
        Raises:
            AWSResourceError: If table deletion fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If table doesn't exist.
        """
        try:
            response = self.client.delete_table(TableName=table_name)
            
            return {
                'table_name': table_name,
                'table_status': response['TableDescription']['TableStatus']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete table '{table_name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Table '{table_name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete table '{table_name}': {str(e)}") from e
    
    def put_item(self, table_name: str, item: Dict[str, Any],
                condition_expression: Optional[str] = None,
                expression_attribute_names: Optional[Dict[str, str]] = None,
                expression_attribute_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Put an item into a DynamoDB table.
        
        Args:
            table_name (str): Name of the table.
            item (Dict[str, Any]): Item to put into the table.
            condition_expression (str, optional): Conditional expression.
            expression_attribute_names (Dict[str, str], optional): Expression attribute names.
            expression_attribute_values (Dict[str, Any], optional): Expression attribute values.
        
        Returns:
            Dict[str, Any]: Put item response.
        
        Raises:
            AWSResourceError: If put operation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            table = self.resource.Table(table_name)
            
            params = {'Item': self._convert_to_dynamodb_format(item)}
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = self._convert_to_dynamodb_format(expression_attribute_values)
            
            response = table.put_item(**params)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to put item in table '{table_name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Table '{table_name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to put item in table '{table_name}': {str(e)}") from e
    
    def update_item(self, table_name: str, key: Dict[str, Any],
                   update_expression: str,
                   condition_expression: Optional[str] = None,
                   expression_attribute_names: Optional[Dict[str, str]] = None,
                   expression_attribute_values: Optional[Dict[str, Any]] = None,
                   return_values: str = 'NONE') -> Dict[str, Any]:
        """
        Update an item in a DynamoDB table.
        
        Args:
            table_name (str): Name of the table.
            key (Dict[str, Any]): Primary key of the item to update.
            update_expression (str): Update expression.
            condition_expression (str, optional): Conditional expression.
            expression_attribute_names (Dict[str, str], optional): Expression attribute names.
            expression_attribute_values (Dict[str, Any], optional): Expression attribute values.
            return_values (str): What to return ('NONE', 'ALL_OLD', 'UPDATED_OLD', 'ALL_NEW', 'UPDATED_NEW').
        
        Returns:
            Dict[str, Any]: Update item response.
        
        Raises:
            AWSResourceError: If update operation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            table = self.resource.Table(table_name)
            
            params = {
                'Key': self._convert_to_dynamodb_format(key),
                'UpdateExpression': update_expression,
                'ReturnValues': return_values
            }
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = self._convert_to_dynamodb_format(expression_attribute_values)
            
            response = table.update_item(**params)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to update item in table '{table_name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Table '{table_name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to update item in table '{table_name}': {str(e)}") from e
    
    def delete_item(self, table_name: str, key: Dict[str, Any],
                   condition_expression: Optional[str] = None,
                   expression_attribute_names: Optional[Dict[str, str]] = None,
                   expression_attribute_values: Optional[Dict[str, Any]] = None,
                   return_values: str = 'NONE') -> Dict[str, Any]:
        """
        Delete an item from a DynamoDB table.
        
        Args:
            table_name (str): Name of the table.
            key (Dict[str, Any]): Primary key of the item to delete.
            condition_expression (str, optional): Conditional expression.
            expression_attribute_names (Dict[str, str], optional): Expression attribute names.
            expression_attribute_values (Dict[str, Any], optional): Expression attribute values.
            return_values (str): What to return ('NONE', 'ALL_OLD').
        
        Returns:
            Dict[str, Any]: Delete item response.
        
        Raises:
            AWSResourceError: If delete operation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            table = self.resource.Table(table_name)
            
            params = {
                'Key': self._convert_to_dynamodb_format(key),
                'ReturnValues': return_values
            }
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = self._convert_to_dynamodb_format(expression_attribute_values)
            
            response = table.delete_item(**params)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete item from table '{table_name}': {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Table '{table_name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete item from table '{table_name}': {str(e)}") from e
    
    def batch_write_item(self, request_items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Perform batch write operations on multiple tables.
        
        Args:
            request_items (Dict[str, List[Dict[str, Any]]]): Batch write request items.
        
        Returns:
            Dict[str, Any]: Batch write response.
        
        Raises:
            AWSResourceError: If batch write operation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            # Convert request items to DynamoDB format
            converted_request_items = {}
            for table_name, items in request_items.items():
                converted_items = []
                for item in items:
                    if 'PutRequest' in item:
                        item['PutRequest']['Item'] = self._convert_to_dynamodb_format(item['PutRequest']['Item'])
                    elif 'DeleteRequest' in item:
                        item['DeleteRequest']['Key'] = self._convert_to_dynamodb_format(item['DeleteRequest']['Key'])
                    converted_items.append(item)
                converted_request_items[table_name] = converted_items
            
            response = self.client.batch_write_item(RequestItems=converted_request_items)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to perform batch write: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to perform batch write: {str(e)}") from e
    
    def update_table_throughput(self, table_name: str, 
                               provisioned_throughput: Dict[str, int],
                               global_secondary_index_updates: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Update the provisioned throughput for a table.
        
        Args:
            table_name (str): Name of the table.
            provisioned_throughput (Dict[str, int]): New provisioned throughput settings.
            global_secondary_index_updates (List[Dict[str, Any]], optional): GSI throughput updates.
        
        Returns:
            Dict[str, Any]: Update response.
        
        Raises:
            AWSResourceError: If update fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {
                'TableName': table_name,
                'ProvisionedThroughput': provisioned_throughput
            }
            
            if global_secondary_index_updates:
                params['GlobalSecondaryIndexUpdates'] = global_secondary_index_updates
            
            response = self.client.update_table(**params)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to update table throughput: {str(e)}") from e
            elif error_code == 'ResourceNotFoundException':
                raise ResourceNotFoundError(f"Table '{table_name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to update table throughput: {str(e)}") from e
    
    def tag_resource(self, resource_arn: str, tags: List[Dict[str, str]]) -> bool:
        """
        Add tags to a DynamoDB resource.
        
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
                ResourceArn=resource_arn,
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
        Remove tags from a DynamoDB resource.
        
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
                ResourceArn=resource_arn,
                TagKeys=tag_keys
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to untag resource: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to untag resource: {str(e)}") from e
    
    def _convert_to_dynamodb_format(self, item: Any) -> Any:
        """
        Convert Python types to DynamoDB format.
        
        Args:
            item: Item to convert.
        
        Returns:
            Converted item in DynamoDB format.
        """
        if isinstance(item, dict):
            return {k: self._convert_to_dynamodb_format(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._convert_to_dynamodb_format(v) for v in item]
        elif isinstance(item, float):
            return Decimal(str(item))
        else:
            return item
