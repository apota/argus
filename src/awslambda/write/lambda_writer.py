"""
Lambda Writer Module

This module provides functionality for creating and managing AWS Lambda resources.
"""

import logging
import json
import zipfile
import io
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class LambdaWriter:
    """
    A class for creating and managing AWS Lambda resources.
    
    This class provides methods to create, update, and delete Lambda functions,
    layers, aliases, and event source mappings.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the Lambda writer.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.lambda_client = self.client_manager.get_client('lambda')
    
    def create_function(self, function_name: str, runtime: str, role: str, 
                       handler: str, code: Dict[str, Any], 
                       description: Optional[str] = None,
                       timeout: int = 3, memory_size: int = 128,
                       environment: Optional[Dict[str, Any]] = None,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new Lambda function.
        
        Args:
            function_name: Name of the function
            runtime: Runtime environment (e.g., 'python3.9', 'nodejs18.x')
            role: ARN of the execution role
            handler: Entry point for the function
            code: Function code (ZipFile, S3Bucket/S3Key, or ImageUri)
            description: Optional description of the function
            timeout: Function timeout in seconds (1-900)
            memory_size: Memory allocated to function (128-10240 MB)
            environment: Environment variables
            tags: Resource tags
            
        Returns:
            Function configuration
            
        Raises:
            AWSResourceError: If there's an error creating the function
        """
        try:
            logger.info("Creating Lambda function: %s", function_name)
            
            kwargs = {
                'FunctionName': function_name,
                'Runtime': runtime,
                'Role': role,
                'Handler': handler,
                'Code': code,
                'Timeout': timeout,
                'MemorySize': memory_size
            }
            
            if description:
                kwargs['Description'] = description
            if environment:
                kwargs['Environment'] = environment
            if tags:
                kwargs['Tags'] = tags
            
            response = self.lambda_client.create_function(**kwargs)
            
            logger.info("Created Lambda function: %s", function_name)
            return response
            
        except ClientError as e:
            error_message = f"Failed to create Lambda function {function_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def update_function_code(self, function_name: str, 
                           zip_file: Optional[bytes] = None,
                           s3_bucket: Optional[str] = None,
                           s3_key: Optional[str] = None,
                           s3_object_version: Optional[str] = None,
                           image_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the code for a Lambda function.
        
        Args:
            function_name: Name of the function
            zip_file: ZIP file containing the function code
            s3_bucket: S3 bucket containing the code
            s3_key: S3 object key
            s3_object_version: S3 object version
            image_uri: Container image URI
            
        Returns:
            Updated function configuration
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error updating the function
        """
        try:
            logger.info("Updating function code: %s", function_name)
            
            kwargs = {'FunctionName': function_name}
            
            if zip_file:
                kwargs['ZipFile'] = zip_file
            elif s3_bucket and s3_key:
                kwargs['S3Bucket'] = s3_bucket
                kwargs['S3Key'] = s3_key
                if s3_object_version:
                    kwargs['S3ObjectVersion'] = s3_object_version
            elif image_uri:
                kwargs['ImageUri'] = image_uri
            else:
                raise ValueError("Must provide either zip_file, S3 location, or image_uri")
            
            response = self.lambda_client.update_function_code(**kwargs)
            
            logger.info("Updated function code: %s", function_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to update function code {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def update_function_configuration(self, function_name: str,
                                    role: Optional[str] = None,
                                    handler: Optional[str] = None,
                                    description: Optional[str] = None,
                                    timeout: Optional[int] = None,
                                    memory_size: Optional[int] = None,
                                    environment: Optional[Dict[str, Any]] = None,
                                    runtime: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the configuration of a Lambda function.
        
        Args:
            function_name: Name of the function
            role: ARN of the execution role
            handler: Entry point for the function
            description: Description of the function
            timeout: Function timeout in seconds
            memory_size: Memory allocated to function
            environment: Environment variables
            runtime: Runtime environment
            
        Returns:
            Updated function configuration
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error updating the function
        """
        try:
            logger.info("Updating function configuration: %s", function_name)
            
            kwargs = {'FunctionName': function_name}
            
            if role:
                kwargs['Role'] = role
            if handler:
                kwargs['Handler'] = handler
            if description:
                kwargs['Description'] = description
            if timeout:
                kwargs['Timeout'] = timeout
            if memory_size:
                kwargs['MemorySize'] = memory_size
            if environment:
                kwargs['Environment'] = environment
            if runtime:
                kwargs['Runtime'] = runtime
            
            response = self.lambda_client.update_function_configuration(**kwargs)
            
            logger.info("Updated function configuration: %s", function_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to update function configuration {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def delete_function(self, function_name: str, qualifier: Optional[str] = None) -> None:
        """
        Delete a Lambda function.
        
        Args:
            function_name: Name of the function
            qualifier: Version or alias to delete (optional)
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error deleting the function
        """
        try:
            logger.info("Deleting Lambda function: %s", function_name)
            
            kwargs = {'FunctionName': function_name}
            if qualifier:
                kwargs['Qualifier'] = qualifier
            
            self.lambda_client.delete_function(**kwargs)
            
            logger.info("Deleted Lambda function: %s", function_name)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete Lambda function {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def create_alias(self, function_name: str, alias_name: str, 
                    function_version: str, description: Optional[str] = None,
                    routing_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an alias for a Lambda function.
        
        Args:
            function_name: Name of the function
            alias_name: Name of the alias
            function_version: Version to point the alias to
            description: Optional description
            routing_config: Optional routing configuration for weighted aliases
            
        Returns:
            Alias configuration
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error creating the alias
        """
        try:
            logger.info("Creating alias %s for function: %s", alias_name, function_name)
            
            kwargs = {
                'FunctionName': function_name,
                'Name': alias_name,
                'FunctionVersion': function_version
            }
            
            if description:
                kwargs['Description'] = description
            if routing_config:
                kwargs['RoutingConfig'] = routing_config
            
            response = self.lambda_client.create_alias(**kwargs)
            
            logger.info("Created alias %s for function: %s", alias_name, function_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to create alias {alias_name} for {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def delete_alias(self, function_name: str, alias_name: str) -> None:
        """
        Delete an alias for a Lambda function.
        
        Args:
            function_name: Name of the function
            alias_name: Name of the alias to delete
            
        Raises:
            ResourceNotFoundError: If the function or alias doesn't exist
            AWSResourceError: If there's an error deleting the alias
        """
        try:
            logger.info("Deleting alias %s for function: %s", alias_name, function_name)
            
            self.lambda_client.delete_alias(
                FunctionName=function_name,
                Name=alias_name
            )
            
            logger.info("Deleted alias %s for function: %s", alias_name, function_name)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function or alias not found: {function_name}/{alias_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete alias {alias_name} for {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def publish_version(self, function_name: str, description: Optional[str] = None,
                       code_sha256: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish a new version of a Lambda function.
        
        Args:
            function_name: Name of the function
            description: Optional description for the version
            code_sha256: SHA256 of the function code (for validation)
            
        Returns:
            Version configuration
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error publishing the version
        """
        try:
            logger.info("Publishing version for function: %s", function_name)
            
            kwargs = {'FunctionName': function_name}
            
            if description:
                kwargs['Description'] = description
            if code_sha256:
                kwargs['CodeSha256'] = code_sha256
            
            response = self.lambda_client.publish_version(**kwargs)
            
            logger.info("Published version %s for function: %s", response['Version'], function_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to publish version for {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def create_event_source_mapping(self, event_source_arn: str, function_name: str,
                                   starting_position: Optional[str] = None,
                                   batch_size: Optional[int] = None,
                                   maximum_batching_window_in_seconds: Optional[int] = None,
                                   enabled: bool = True) -> Dict[str, Any]:
        """
        Create an event source mapping for a Lambda function.
        
        Args:
            event_source_arn: ARN of the event source
            function_name: Name of the function
            starting_position: Starting position for stream sources (TRIM_HORIZON, LATEST)
            batch_size: Maximum number of items to retrieve per batch
            maximum_batching_window_in_seconds: Maximum batching window
            enabled: Whether the mapping is enabled
            
        Returns:
            Event source mapping configuration
            
        Raises:
            AWSResourceError: If there's an error creating the mapping
        """
        try:
            logger.info("Creating event source mapping for function: %s", function_name)
            
            kwargs = {
                'EventSourceArn': event_source_arn,
                'FunctionName': function_name,
                'Enabled': enabled
            }
            
            if starting_position:
                kwargs['StartingPosition'] = starting_position
            if batch_size:
                kwargs['BatchSize'] = batch_size
            if maximum_batching_window_in_seconds:
                kwargs['MaximumBatchingWindowInSeconds'] = maximum_batching_window_in_seconds
            
            response = self.lambda_client.create_event_source_mapping(**kwargs)
            
            logger.info("Created event source mapping for function: %s", function_name)
            return response
            
        except ClientError as e:
            error_message = f"Failed to create event source mapping for {function_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def delete_event_source_mapping(self, uuid: str) -> Dict[str, Any]:
        """
        Delete an event source mapping.
        
        Args:
            uuid: UUID of the event source mapping
            
        Returns:
            Event source mapping configuration
            
        Raises:
            ResourceNotFoundError: If the mapping doesn't exist
            AWSResourceError: If there's an error deleting the mapping
        """
        try:
            logger.info("Deleting event source mapping: %s", uuid)
            
            response = self.lambda_client.delete_event_source_mapping(UUID=uuid)
            
            logger.info("Deleted event source mapping: %s", uuid)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Event source mapping not found: {uuid}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete event source mapping {uuid}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def add_permission(self, function_name: str, statement_id: str, 
                      action: str, principal: str,
                      source_arn: Optional[str] = None,
                      source_account: Optional[str] = None,
                      qualifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a permission to a Lambda function's resource policy.
        
        Args:
            function_name: Name of the function
            statement_id: Unique identifier for the statement
            action: Action that the principal can use on the function
            principal: Principal who is granted permission
            source_arn: Optional source ARN
            source_account: Optional source account
            qualifier: Optional qualifier (version or alias)
            
        Returns:
            Statement that was added
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error adding permission
        """
        try:
            logger.info("Adding permission to function: %s", function_name)
            
            kwargs = {
                'FunctionName': function_name,
                'StatementId': statement_id,
                'Action': action,
                'Principal': principal
            }
            
            if source_arn:
                kwargs['SourceArn'] = source_arn
            if source_account:
                kwargs['SourceAccount'] = source_account
            if qualifier:
                kwargs['Qualifier'] = qualifier
            
            response = self.lambda_client.add_permission(**kwargs)
            
            logger.info("Added permission to function: %s", function_name)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to add permission to {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    @staticmethod
    def create_deployment_package(source_code: str, handler_filename: str = 'lambda_function.py') -> bytes:
        """
        Create a deployment package (ZIP file) for Lambda function code.
        
        Args:
            source_code: Python source code for the function
            handler_filename: Name of the handler file
            
        Returns:
            ZIP file contents as bytes
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(handler_filename, source_code)
        
        return zip_buffer.getvalue()
