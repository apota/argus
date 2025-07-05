"""
EC2 Writer - Write operations for Amazon EC2 resources.

This module provides methods to create, modify, and delete EC2 instances,
security groups, key pairs, and other EC2 resources.
"""

import logging
from typing import List, Dict, Any, Optional
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class EC2Writer:
    """EC2 write operations using boto3."""
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize EC2Writer.
        
        Args:
            client_manager: AWSClientManager instance for AWS service clients
        """
        self.client_manager = client_manager
        self.ec2_client = client_manager.get_client('ec2')
        logger.info("EC2Writer initialized successfully")
    
    def create_instance(self, image_id: str, instance_type: str = 't2.micro', 
                       key_name: Optional[str] = None, security_group_ids: Optional[List[str]] = None,
                       subnet_id: Optional[str] = None, user_data: Optional[str] = None,
                       min_count: int = 1, max_count: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Launch new EC2 instances.
        
        Args:
            image_id: AMI ID to launch
            instance_type: EC2 instance type (default: t2.micro)
            key_name: Key pair name for SSH access
            security_group_ids: List of security group IDs
            subnet_id: Subnet ID for VPC launch
            user_data: User data script for instance initialization
            min_count: Minimum number of instances to launch
            max_count: Maximum number of instances to launch
            **kwargs: Additional parameters for run_instances
            
        Returns:
            Dictionary containing instance launch details
            
        Raises:
            AWSResourceError: If there's an error launching instances
        """
        try:
            logger.info(f"Launching {min_count}-{max_count} EC2 instances")
            
            launch_params = {
                'ImageId': image_id,
                'MinCount': min_count,
                'MaxCount': max_count,
                'InstanceType': instance_type
            }
            
            if key_name:
                launch_params['KeyName'] = key_name
            if security_group_ids:
                launch_params['SecurityGroupIds'] = security_group_ids
            if subnet_id:
                launch_params['SubnetId'] = subnet_id
            if user_data:
                launch_params['UserData'] = user_data
            
            # Add any additional parameters
            launch_params.update(kwargs)
            
            response = self.ec2_client.run_instances(**launch_params)
            
            instance_ids = [instance['InstanceId'] for instance in response['Instances']]
            logger.info(f"Successfully launched instances: {instance_ids}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error launching EC2 instances: {e}")
            raise AWSResourceError(f"Failed to launch EC2 instances: {e}")
    
    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Terminate a specific EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID to terminate
            
        Returns:
            Dictionary containing termination details
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error terminating the instance
        """
        try:
            logger.info(f"Terminating EC2 instance: {instance_id}")
            
            response = self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            
            logger.info(f"Successfully initiated termination for instance: {instance_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            logger.error(f"Error terminating EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to terminate EC2 instance {instance_id}: {e}")
        except Exception as e:
            logger.error(f"Error terminating EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to terminate EC2 instance {instance_id}: {e}")
    
    def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Start a stopped EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID to start
            
        Returns:
            Dictionary containing start operation details
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error starting the instance
        """
        try:
            logger.info(f"Starting EC2 instance: {instance_id}")
            
            response = self.ec2_client.start_instances(InstanceIds=[instance_id])
            
            logger.info(f"Successfully initiated start for instance: {instance_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            logger.error(f"Error starting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to start EC2 instance {instance_id}: {e}")
        except Exception as e:
            logger.error(f"Error starting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to start EC2 instance {instance_id}: {e}")
    
    def stop_instance(self, instance_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Stop a running EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID to stop
            force: Whether to force stop the instance
            
        Returns:
            Dictionary containing stop operation details
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error stopping the instance
        """
        try:
            logger.info(f"Stopping EC2 instance: {instance_id}")
            
            response = self.ec2_client.stop_instances(
                InstanceIds=[instance_id],
                Force=force
            )
            
            logger.info(f"Successfully initiated stop for instance: {instance_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            logger.error(f"Error stopping EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to stop EC2 instance {instance_id}: {e}")
        except Exception as e:
            logger.error(f"Error stopping EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to stop EC2 instance {instance_id}: {e}")
    
    def reboot_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Reboot an EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID to reboot
            
        Returns:
            Dictionary containing reboot operation details
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error rebooting the instance
        """
        try:
            logger.info(f"Rebooting EC2 instance: {instance_id}")
            
            response = self.ec2_client.reboot_instances(InstanceIds=[instance_id])
            
            logger.info(f"Successfully initiated reboot for instance: {instance_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            logger.error(f"Error rebooting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to reboot EC2 instance {instance_id}: {e}")
        except Exception as e:
            logger.error(f"Error rebooting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to reboot EC2 instance {instance_id}: {e}")
    
    def create_security_group(self, group_name: str, description: str, 
                             vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new security group.
        
        Args:
            group_name: Name for the security group
            description: Description for the security group
            vpc_id: VPC ID (required for VPC security groups)
            
        Returns:
            Dictionary containing security group creation details
            
        Raises:
            AWSResourceError: If there's an error creating the security group
        """
        try:
            logger.info(f"Creating security group: {group_name}")
            
            params = {
                'GroupName': group_name,
                'Description': description
            }
            
            if vpc_id:
                params['VpcId'] = vpc_id
            
            response = self.ec2_client.create_security_group(**params)
            
            logger.info(f"Successfully created security group: {response['GroupId']}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating security group {group_name}: {e}")
            raise AWSResourceError(f"Failed to create security group {group_name}: {e}")
    
    def delete_security_group(self, group_id: str) -> Dict[str, Any]:
        """
        Delete a security group.
        
        Args:
            group_id: The security group ID to delete
            
        Returns:
            Dictionary containing deletion details
            
        Raises:
            ResourceNotFoundError: If the security group is not found
            AWSResourceError: If there's an error deleting the security group
        """
        try:
            logger.info(f"Deleting security group: {group_id}")
            
            response = self.ec2_client.delete_security_group(GroupId=group_id)
            
            logger.info(f"Successfully deleted security group: {group_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroupId.NotFound':
                raise ResourceNotFoundError(f"Security group not found: {group_id}")
            logger.error(f"Error deleting security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to delete security group {group_id}: {e}")
        except Exception as e:
            logger.error(f"Error deleting security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to delete security group {group_id}: {e}")
    
    def authorize_security_group_ingress(self, group_id: str, ip_permissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add inbound rules to a security group.
        
        Args:
            group_id: The security group ID
            ip_permissions: List of inbound rule specifications
            
        Returns:
            Dictionary containing authorization details
            
        Raises:
            ResourceNotFoundError: If the security group is not found
            AWSResourceError: If there's an error adding the rules
        """
        try:
            logger.info(f"Adding inbound rules to security group: {group_id}")
            
            response = self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )
            
            logger.info(f"Successfully added inbound rules to security group: {group_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroupId.NotFound':
                raise ResourceNotFoundError(f"Security group not found: {group_id}")
            logger.error(f"Error adding inbound rules to security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to add inbound rules to security group {group_id}: {e}")
        except Exception as e:
            logger.error(f"Error adding inbound rules to security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to add inbound rules to security group {group_id}: {e}")
    
    def revoke_security_group_ingress(self, group_id: str, ip_permissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Remove inbound rules from a security group.
        
        Args:
            group_id: The security group ID
            ip_permissions: List of inbound rule specifications to remove
            
        Returns:
            Dictionary containing revocation details
            
        Raises:
            ResourceNotFoundError: If the security group is not found
            AWSResourceError: If there's an error removing the rules
        """
        try:
            logger.info(f"Removing inbound rules from security group: {group_id}")
            
            response = self.ec2_client.revoke_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )
            
            logger.info(f"Successfully removed inbound rules from security group: {group_id}")
            return response
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroupId.NotFound':
                raise ResourceNotFoundError(f"Security group not found: {group_id}")
            logger.error(f"Error removing inbound rules from security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to remove inbound rules from security group {group_id}: {e}")
        except Exception as e:
            logger.error(f"Error removing inbound rules from security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to remove inbound rules from security group {group_id}: {e}")
    
    def create_key_pair(self, key_name: str) -> Dict[str, Any]:
        """
        Create a new EC2 key pair.
        
        Args:
            key_name: Name for the key pair
            
        Returns:
            Dictionary containing key pair creation details (including private key material)
            
        Raises:
            AWSResourceError: If there's an error creating the key pair
        """
        try:
            logger.info(f"Creating key pair: {key_name}")
            
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            
            logger.info(f"Successfully created key pair: {key_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating key pair {key_name}: {e}")
            raise AWSResourceError(f"Failed to create key pair {key_name}: {e}")
    
    def delete_key_pair(self, key_name: str) -> Dict[str, Any]:
        """
        Delete an EC2 key pair.
        
        Args:
            key_name: Name of the key pair to delete
            
        Returns:
            Dictionary containing deletion details
            
        Raises:
            AWSResourceError: If there's an error deleting the key pair
        """
        try:
            logger.info(f"Deleting key pair: {key_name}")
            
            response = self.ec2_client.delete_key_pair(KeyName=key_name)
            
            logger.info(f"Successfully deleted key pair: {key_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error deleting key pair {key_name}: {e}")
            raise AWSResourceError(f"Failed to delete key pair {key_name}: {e}")
    
    def create_tags(self, resource_ids: List[str], tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create or overwrite tags for EC2 resources.
        
        Args:
            resource_ids: List of resource IDs to tag
            tags: List of tag dictionaries with 'Key' and 'Value' keys
            
        Returns:
            Dictionary containing tagging operation details
            
        Raises:
            AWSResourceError: If there's an error creating tags
        """
        try:
            logger.info(f"Creating tags for resources: {resource_ids}")
            
            response = self.ec2_client.create_tags(
                Resources=resource_ids,
                Tags=tags
            )
            
            logger.info(f"Successfully created tags for resources: {resource_ids}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating tags for resources {resource_ids}: {e}")
            raise AWSResourceError(f"Failed to create tags for resources {resource_ids}: {e}")
    
    def delete_tags(self, resource_ids: List[str], tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Delete tags from EC2 resources.
        
        Args:
            resource_ids: List of resource IDs to remove tags from
            tags: List of tag dictionaries with 'Key' and optionally 'Value' keys
            
        Returns:
            Dictionary containing tag deletion details
            
        Raises:
            AWSResourceError: If there's an error deleting tags
        """
        try:
            logger.info(f"Deleting tags from resources: {resource_ids}")
            
            response = self.ec2_client.delete_tags(
                Resources=resource_ids,
                Tags=tags
            )
            
            logger.info(f"Successfully deleted tags from resources: {resource_ids}")
            return response
            
        except Exception as e:
            logger.error(f"Error deleting tags from resources {resource_ids}: {e}")
            raise AWSResourceError(f"Failed to delete tags from resources {resource_ids}: {e}")
