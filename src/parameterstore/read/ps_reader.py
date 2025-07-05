"""
Parameter Store Reader Module

This module provides functionality for reading and exploring AWS Systems Manager Parameter Store resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from ...common.aws_client import AWSClientManager
from ...common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class ParameterStoreReader:
    """
    A class for reading AWS Systems Manager Parameter Store resources.
    
    This class provides methods to list and retrieve information about
    parameters, parameter history, and parameter hierarchies.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the Parameter Store reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.ssm_client = self.client_manager.get_client('ssm')
    
    def describe_parameters(self, filters: Optional[List[Dict[str, Any]]] = None,
                          parameter_filters: Optional[List[Dict[str, Any]]] = None,
                          max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all parameters in the account.
        
        Args:
            filters: Optional filters for parameter metadata
            parameter_filters: Optional filters for parameter names and values
            max_results: Maximum number of parameters to return
            
        Returns:
            List of parameter metadata
            
        Raises:
            AWSResourceError: If there's an error listing parameters
        """
        try:
            logger.info("Listing Parameter Store parameters")
            
            kwargs = {}
            if filters:
                kwargs['Filters'] = filters
            if parameter_filters:
                kwargs['ParameterFilters'] = parameter_filters
            if max_results:
                kwargs['MaxResults'] = max_results
            
            paginator = self.ssm_client.get_paginator('describe_parameters')
            page_iterator = paginator.paginate(**kwargs)
            
            parameters = []
            for page in page_iterator:
                parameters.extend(page.get('Parameters', []))
            
            logger.info("Found %d Parameter Store parameters", len(parameters))
            return parameters
            
        except ClientError as e:
            error_message = f"Failed to list Parameter Store parameters: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_parameter(self, name: str, with_decryption: bool = False) -> Dict[str, Any]:
        """
        Get a specific parameter from Parameter Store.
        
        Args:
            name: Name of the parameter
            with_decryption: Whether to decrypt SecureString parameters
            
        Returns:
            Parameter configuration and value
            
        Raises:
            ResourceNotFoundError: If the parameter doesn't exist
            AWSResourceError: If there's an error retrieving the parameter
        """
        try:
            logger.info("Getting Parameter Store parameter: %s", name)
            
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=with_decryption
            )
            
            logger.info("Retrieved parameter: %s", name)
            return response.get('Parameter', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ParameterNotFound':
                error_message = f"Parameter Store parameter not found: {name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get Parameter Store parameter {name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_parameters(self, names: List[str], with_decryption: bool = False) -> Dict[str, Any]:
        """
        Get multiple parameters from Parameter Store.
        
        Args:
            names: List of parameter names
            with_decryption: Whether to decrypt SecureString parameters
            
        Returns:
            Dictionary containing valid parameters and invalid parameter names
            
        Raises:
            AWSResourceError: If there's an error retrieving the parameters
        """
        try:
            logger.info("Getting %d Parameter Store parameters", len(names))
            
            response = self.ssm_client.get_parameters(
                Names=names,
                WithDecryption=with_decryption
            )
            
            valid_params = response.get('Parameters', [])
            invalid_params = response.get('InvalidParameters', [])
            
            logger.info("Retrieved %d valid parameters, %d invalid", len(valid_params), len(invalid_params))
            return {
                'Parameters': valid_params,
                'InvalidParameters': invalid_params
            }
            
        except ClientError as e:
            error_message = f"Failed to get Parameter Store parameters: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_parameters_by_path(self, path: str, recursive: bool = False,
                              parameter_filters: Optional[List[Dict[str, Any]]] = None,
                              with_decryption: bool = False,
                              max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get parameters by path hierarchy.
        
        Args:
            path: Parameter path prefix
            recursive: Whether to retrieve parameters recursively
            parameter_filters: Optional filters for parameter names and values
            with_decryption: Whether to decrypt SecureString parameters
            max_results: Maximum number of parameters to return
            
        Returns:
            List of parameters under the specified path
            
        Raises:
            AWSResourceError: If there's an error retrieving the parameters
        """
        try:
            logger.info("Getting Parameter Store parameters by path: %s", path)
            
            kwargs = {
                'Path': path,
                'Recursive': recursive,
                'WithDecryption': with_decryption
            }
            
            if parameter_filters:
                kwargs['ParameterFilters'] = parameter_filters
            if max_results:
                kwargs['MaxResults'] = max_results
            
            paginator = self.ssm_client.get_paginator('get_parameters_by_path')
            page_iterator = paginator.paginate(**kwargs)
            
            parameters = []
            for page in page_iterator:
                parameters.extend(page.get('Parameters', []))
            
            logger.info("Found %d parameters under path %s", len(parameters), path)
            return parameters
            
        except ClientError as e:
            error_message = f"Failed to get Parameter Store parameters by path {path}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_parameter_history(self, name: str, with_decryption: bool = False,
                            max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the history of a parameter.
        
        Args:
            name: Name of the parameter
            with_decryption: Whether to decrypt SecureString parameter values
            max_results: Maximum number of history items to return
            
        Returns:
            List of parameter history items
            
        Raises:
            ResourceNotFoundError: If the parameter doesn't exist
            AWSResourceError: If there's an error retrieving the parameter history
        """
        try:
            logger.info("Getting Parameter Store parameter history: %s", name)
            
            kwargs = {
                'Name': name,
                'WithDecryption': with_decryption
            }
            
            if max_results:
                kwargs['MaxResults'] = max_results
            
            paginator = self.ssm_client.get_paginator('get_parameter_history')
            page_iterator = paginator.paginate(**kwargs)
            
            history = []
            for page in page_iterator:
                history.extend(page.get('Parameters', []))
            
            logger.info("Found %d history items for parameter %s", len(history), name)
            return history
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ParameterNotFound':
                error_message = f"Parameter Store parameter not found: {name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get Parameter Store parameter history {name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def describe_ops_items(self, ops_item_filters: Optional[List[Dict[str, Any]]] = None,
                          max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List OpsItems (operational items) in Systems Manager.
        
        Args:
            ops_item_filters: Optional filters for OpsItems
            max_results: Maximum number of OpsItems to return
            
        Returns:
            List of OpsItem summaries
            
        Raises:
            AWSResourceError: If there's an error listing OpsItems
        """
        try:
            logger.info("Listing Systems Manager OpsItems")
            
            kwargs = {}
            if ops_item_filters:
                kwargs['OpsItemFilters'] = ops_item_filters
            if max_results:
                kwargs['MaxResults'] = max_results
            
            paginator = self.ssm_client.get_paginator('describe_ops_items')
            page_iterator = paginator.paginate(**kwargs)
            
            ops_items = []
            for page in page_iterator:
                ops_items.extend(page.get('OpsItemSummaries', []))
            
            logger.info("Found %d Systems Manager OpsItems", len(ops_items))
            return ops_items
            
        except ClientError as e:
            error_message = f"Failed to list Systems Manager OpsItems: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_ops_item(self, ops_item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific OpsItem.
        
        Args:
            ops_item_id: ID of the OpsItem
            
        Returns:
            OpsItem configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the OpsItem doesn't exist
            AWSResourceError: If there's an error retrieving the OpsItem
        """
        try:
            logger.info("Getting Systems Manager OpsItem: %s", ops_item_id)
            
            response = self.ssm_client.get_ops_item(OpsItemId=ops_item_id)
            
            logger.info("Retrieved OpsItem: %s", ops_item_id)
            return response.get('OpsItem', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'OpsItemNotFoundException':
                error_message = f"Systems Manager OpsItem not found: {ops_item_id}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get Systems Manager OpsItem {ops_item_id}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def describe_maintenance_windows(self, filters: Optional[List[Dict[str, Any]]] = None,
                                   max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List maintenance windows in Systems Manager.
        
        Args:
            filters: Optional filters for maintenance windows
            max_results: Maximum number of maintenance windows to return
            
        Returns:
            List of maintenance window information
            
        Raises:
            AWSResourceError: If there's an error listing maintenance windows
        """
        try:
            logger.info("Listing Systems Manager maintenance windows")
            
            kwargs = {}
            if filters:
                kwargs['Filters'] = filters
            if max_results:
                kwargs['MaxResults'] = max_results
            
            paginator = self.ssm_client.get_paginator('describe_maintenance_windows')
            page_iterator = paginator.paginate(**kwargs)
            
            windows = []
            for page in page_iterator:
                windows.extend(page.get('WindowIdentities', []))
            
            logger.info("Found %d Systems Manager maintenance windows", len(windows))
            return windows
            
        except ClientError as e:
            error_message = f"Failed to list Systems Manager maintenance windows: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_maintenance_window(self, window_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific maintenance window.
        
        Args:
            window_id: ID of the maintenance window
            
        Returns:
            Maintenance window configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the maintenance window doesn't exist
            AWSResourceError: If there's an error retrieving the maintenance window
        """
        try:
            logger.info("Getting Systems Manager maintenance window: %s", window_id)
            
            response = self.ssm_client.get_maintenance_window(WindowId=window_id)
            
            logger.info("Retrieved maintenance window: %s", window_id)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DoesNotExistException':
                error_message = f"Systems Manager maintenance window not found: {window_id}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get Systems Manager maintenance window {window_id}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
