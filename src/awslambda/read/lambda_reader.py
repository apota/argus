"""
Lambda Reader Module

This module provides functionality for reading and exploring AWS Lambda resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from ...common.aws_client import AWSClientManager
from ...common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class LambdaReader:
    """
    A class for reading AWS Lambda resources.
    
    This class provides methods to list and retrieve information about
    Lambda functions, layers, event source mappings, and aliases.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the Lambda reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.lambda_client = self.client_manager.get_client('lambda')
    
    def list_functions(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all Lambda functions in the account.
        
        Args:
            max_items: Maximum number of functions to return
            
        Returns:
            List of function configurations
            
        Raises:
            AWSResourceError: If there's an error listing functions
        """
        try:
            logger.info("Listing Lambda functions")
            
            paginator = self.lambda_client.get_paginator('list_functions')
            page_iterator = paginator.paginate(
                PaginationConfig={'MaxItems': max_items} if max_items else {}
            )
            
            functions = []
            for page in page_iterator:
                functions.extend(page.get('Functions', []))
            
            logger.info(f"Found {len(functions)} Lambda functions")
            return functions
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = f"Failed to list Lambda functions: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_function(self, function_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Lambda function.
        
        Args:
            function_name: Name or ARN of the Lambda function
            
        Returns:
            Function configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error retrieving the function
        """
        try:
            logger.info(f"Getting Lambda function: {function_name}")
            
            response = self.lambda_client.get_function(FunctionName=function_name)
            
            logger.info(f"Retrieved function configuration for {function_name}")
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get Lambda function {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_function_configuration(self, function_name: str) -> Dict[str, Any]:
        """
        Get configuration information for a Lambda function.
        
        Args:
            function_name: Name or ARN of the Lambda function
            
        Returns:
            Function configuration
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error retrieving the configuration
        """
        try:
            logger.info(f"Getting Lambda function configuration: {function_name}")
            
            response = self.lambda_client.get_function_configuration(FunctionName=function_name)
            
            logger.info(f"Retrieved configuration for {function_name}")
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get function configuration {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_aliases(self, function_name: str) -> List[Dict[str, Any]]:
        """
        List aliases for a Lambda function.
        
        Args:
            function_name: Name or ARN of the Lambda function
            
        Returns:
            List of aliases
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error listing aliases
        """
        try:
            logger.info(f"Listing aliases for function: {function_name}")
            
            paginator = self.lambda_client.get_paginator('list_aliases')
            page_iterator = paginator.paginate(FunctionName=function_name)
            
            aliases = []
            for page in page_iterator:
                aliases.extend(page.get('Aliases', []))
            
            logger.info(f"Found {len(aliases)} aliases for {function_name}")
            return aliases
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list aliases for {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_versions(self, function_name: str) -> List[Dict[str, Any]]:
        """
        List versions for a Lambda function.
        
        Args:
            function_name: Name or ARN of the Lambda function
            
        Returns:
            List of function versions
            
        Raises:
            ResourceNotFoundError: If the function doesn't exist
            AWSResourceError: If there's an error listing versions
        """
        try:
            logger.info(f"Listing versions for function: {function_name}")
            
            paginator = self.lambda_client.get_paginator('list_versions_by_function')
            page_iterator = paginator.paginate(FunctionName=function_name)
            
            versions = []
            for page in page_iterator:
                versions.extend(page.get('Versions', []))
            
            logger.info(f"Found {len(versions)} versions for {function_name}")
            return versions
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Lambda function not found: {function_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list versions for {function_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_event_source_mappings(self, function_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List event source mappings for Lambda functions.
        
        Args:
            function_name: Optional function name to filter mappings
            
        Returns:
            List of event source mappings
            
        Raises:
            AWSResourceError: If there's an error listing mappings
        """
        try:
            logger.info(f"Listing event source mappings for function: {function_name or 'all functions'}")
            
            kwargs = {}
            if function_name:
                kwargs['FunctionName'] = function_name
            
            paginator = self.lambda_client.get_paginator('list_event_source_mappings')
            page_iterator = paginator.paginate(**kwargs)
            
            mappings = []
            for page in page_iterator:
                mappings.extend(page.get('EventSourceMappings', []))
            
            logger.info(f"Found {len(mappings)} event source mappings")
            return mappings
            
        except ClientError as e:
            error_message = f"Failed to list event source mappings: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_layers(self) -> List[Dict[str, Any]]:
        """
        List Lambda layers.
        
        Returns:
            List of layers
            
        Raises:
            AWSResourceError: If there's an error listing layers
        """
        try:
            logger.info("Listing Lambda layers")
            
            paginator = self.lambda_client.get_paginator('list_layers')
            page_iterator = paginator.paginate()
            
            layers = []
            for page in page_iterator:
                layers.extend(page.get('Layers', []))
            
            logger.info(f"Found {len(layers)} Lambda layers")
            return layers
            
        except ClientError as e:
            error_message = f"Failed to list Lambda layers: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_layer_version(self, layer_name: str, version_number: int) -> Dict[str, Any]:
        """
        Get information about a specific layer version.
        
        Args:
            layer_name: Name or ARN of the layer
            version_number: Version number of the layer
            
        Returns:
            Layer version information
            
        Raises:
            ResourceNotFoundError: If the layer version doesn't exist
            AWSResourceError: If there's an error retrieving the layer version
        """
        try:
            logger.info(f"Getting layer version: {layer_name}:{version_number}")
            
            response = self.lambda_client.get_layer_version(
                LayerName=layer_name,
                VersionNumber=version_number
            )
            
            logger.info(f"Retrieved layer version {layer_name}:{version_number}")
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                error_message = f"Layer version not found: {layer_name}:{version_number}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get layer version {layer_name}:{version_number}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
