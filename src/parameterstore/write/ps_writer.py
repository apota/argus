"""
Parameter Store Writer Module
Provides functionality to create, update, and manage AWS Systems Manager Parameter Store parameters.
"""

from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, AWSPermissionException, ResourceNotFoundError


class ParameterStoreWriter:
    """
    Handles write operations for AWS Systems Manager Parameter Store.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize the Parameter Store writer.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.client = client_manager.get_client('ssm')
    
    def put_parameter(self, name: str, value: str, parameter_type: str = 'String',
                     description: Optional[str] = None, key_id: Optional[str] = None,
                     overwrite: bool = False, allowed_pattern: Optional[str] = None,
                     tags: Optional[List[Dict[str, str]]] = None,
                     tier: str = 'Standard', policies: Optional[str] = None,
                     data_type: str = 'text') -> Dict[str, Any]:
        """
        Create or update a parameter in Parameter Store.
        
        Args:
            name (str): Name of the parameter.
            value (str): Value of the parameter.
            parameter_type (str): Type of parameter ('String', 'StringList', 'SecureString').
            description (str, optional): Description of the parameter.
            key_id (str, optional): KMS key ID for SecureString parameters.
            overwrite (bool): Whether to overwrite existing parameter.
            allowed_pattern (str, optional): Regular expression pattern for validation.
            tags (List[Dict[str, str]], optional): Tags for the parameter.
            tier (str): Parameter tier ('Standard' or 'Advanced').
            policies (str, optional): Parameter policies in JSON format.
            data_type (str): Data type of the parameter.
        
        Returns:
            Dict[str, Any]: Parameter creation response.
        
        Raises:
            AWSResourceError: If parameter creation fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            params = {
                'Name': name,
                'Value': value,
                'Type': parameter_type,
                'Overwrite': overwrite,
                'Tier': tier,
                'DataType': data_type
            }
            
            if description:
                params['Description'] = description
            
            if key_id and parameter_type == 'SecureString':
                params['KeyId'] = key_id
            
            if allowed_pattern:
                params['AllowedPattern'] = allowed_pattern
            
            if tags:
                params['Tags'] = tags
            
            if policies:
                params['Policies'] = policies
            
            response = self.client.put_parameter(**params)
            
            return {
                'version': response['Version'],
                'tier': response['Tier'],
                'name': name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to put parameter '{name}': {str(e)}") from e
            elif error_code == 'ParameterAlreadyExists':
                raise AWSResourceError(f"Parameter '{name}' already exists and overwrite is False") from e
            else:
                raise AWSResourceError(f"Failed to put parameter '{name}': {str(e)}") from e
    
    def delete_parameter(self, name: str) -> bool:
        """
        Delete a parameter from Parameter Store.
        
        Args:
            name (str): Name of the parameter to delete.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            AWSResourceError: If parameter deletion fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If parameter doesn't exist.
        """
        try:
            self.client.delete_parameter(Name=name)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete parameter '{name}': {str(e)}") from e
            elif error_code == 'ParameterNotFound':
                raise ResourceNotFoundError(f"Parameter '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to delete parameter '{name}': {str(e)}") from e
    
    def delete_parameters(self, names: List[str]) -> Dict[str, Any]:
        """
        Delete multiple parameters from Parameter Store.
        
        Args:
            names (List[str]): List of parameter names to delete.
        
        Returns:
            Dict[str, Any]: Deletion response with deleted and invalid parameters.
        
        Raises:
            AWSResourceError: If parameter deletion fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.delete_parameters(Names=names)
            
            return {
                'deleted_parameters': response.get('DeletedParameters', []),
                'invalid_parameters': response.get('InvalidParameters', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to delete parameters: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to delete parameters: {str(e)}") from e
    
    def label_parameter_version(self, name: str, parameter_version: int,
                               labels: List[str]) -> Dict[str, Any]:
        """
        Label a specific version of a parameter.
        
        Args:
            name (str): Name of the parameter.
            parameter_version (int): Version number to label.
            labels (List[str]): Labels to apply to the version.
        
        Returns:
            Dict[str, Any]: Label response.
        
        Raises:
            AWSResourceError: If labeling fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If parameter doesn't exist.
        """
        try:
            response = self.client.label_parameter_version(
                Name=name,
                ParameterVersion=parameter_version,
                Labels=labels
            )
            
            return {
                'invalid_labels': response.get('InvalidLabels', []),
                'parameter_version': response.get('ParameterVersion')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to label parameter version: {str(e)}") from e
            elif error_code == 'ParameterNotFound':
                raise ResourceNotFoundError(f"Parameter '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to label parameter version: {str(e)}") from e
    
    def unlabel_parameter_version(self, name: str, parameter_version: int,
                                 labels: List[str]) -> Dict[str, Any]:
        """
        Remove labels from a specific version of a parameter.
        
        Args:
            name (str): Name of the parameter.
            parameter_version (int): Version number to unlabel.
            labels (List[str]): Labels to remove from the version.
        
        Returns:
            Dict[str, Any]: Unlabel response.
        
        Raises:
            AWSResourceError: If unlabeling fails.
            AWSPermissionException: If insufficient permissions.
            ResourceNotFoundError: If parameter doesn't exist.
        """
        try:
            response = self.client.unlabel_parameter_version(
                Name=name,
                ParameterVersion=parameter_version,
                Labels=labels
            )
            
            return {
                'removed_labels': response.get('RemovedLabels', []),
                'invalid_labels': response.get('InvalidLabels', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to unlabel parameter version: {str(e)}") from e
            elif error_code == 'ParameterNotFound':
                raise ResourceNotFoundError(f"Parameter '{name}' not found") from e
            else:
                raise AWSResourceError(f"Failed to unlabel parameter version: {str(e)}") from e
    
    def add_tags_to_resource(self, resource_type: str, resource_id: str,
                           tags: List[Dict[str, str]]) -> bool:
        """
        Add tags to a Parameter Store resource.
        
        Args:
            resource_type (str): Type of resource (e.g., 'Parameter').
            resource_id (str): ID of the resource to tag.
            tags (List[Dict[str, str]]): List of tags to add.
        
        Returns:
            bool: True if tagging was successful.
        
        Raises:
            AWSResourceError: If tagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.add_tags_to_resource(
                ResourceType=resource_type,
                ResourceId=resource_id,
                Tags=tags
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to tag resource: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to tag resource: {str(e)}") from e
    
    def remove_tags_from_resource(self, resource_type: str, resource_id: str,
                                tag_keys: List[str]) -> bool:
        """
        Remove tags from a Parameter Store resource.
        
        Args:
            resource_type (str): Type of resource (e.g., 'Parameter').
            resource_id (str): ID of the resource to untag.
            tag_keys (List[str]): List of tag keys to remove.
        
        Returns:
            bool: True if untagging was successful.
        
        Raises:
            AWSResourceError: If untagging fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            self.client.remove_tags_from_resource(
                ResourceType=resource_type,
                ResourceId=resource_id,
                TagKeys=tag_keys
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to untag resource: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to untag resource: {str(e)}") from e
    
    def reset_service_setting(self, setting_id: str, setting_value: str) -> Dict[str, Any]:
        """
        Reset a service setting to its default value.
        
        Args:
            setting_id (str): ID of the service setting.
            setting_value (str): New value for the service setting.
        
        Returns:
            Dict[str, Any]: Reset response.
        
        Raises:
            AWSResourceError: If reset fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.reset_service_setting(
                SettingId=setting_id,
                SettingValue=setting_value
            )
            
            return {
                'service_setting': response.get('ServiceSetting', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to reset service setting: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to reset service setting: {str(e)}") from e
    
    def update_service_setting(self, setting_id: str, setting_value: str) -> Dict[str, Any]:
        """
        Update a service setting.
        
        Args:
            setting_id (str): ID of the service setting.
            setting_value (str): New value for the service setting.
        
        Returns:
            Dict[str, Any]: Update response.
        
        Raises:
            AWSResourceError: If update fails.
            AWSPermissionException: If insufficient permissions.
        """
        try:
            response = self.client.update_service_setting(
                SettingId=setting_id,
                SettingValue=setting_value
            )
            
            return {
                'service_setting': response.get('ServiceSetting', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                raise AWSPermissionException(f"Failed to update service setting: {str(e)}") from e
            else:
                raise AWSResourceError(f"Failed to update service setting: {str(e)}") from e
