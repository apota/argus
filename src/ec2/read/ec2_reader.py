"""
EC2 Reader - Read operations for Amazon EC2 resources.

This module provides methods to read and query EC2 instances, security groups,
key pairs, AMIs, and other EC2 resources.
"""

import logging
from typing import List, Dict, Any, Optional
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class EC2Reader:
    """EC2 read operations using boto3."""
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize EC2Reader.
        
        Args:
            client_manager: AWSClientManager instance for AWS service clients
        """
        self.client_manager = client_manager
        self.ec2_client = client_manager.get_client('ec2')
        logger.info("EC2Reader initialized successfully")
    
    def list_instances(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        List all EC2 instances with optional filters.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of EC2 instance dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing instances
        """
        try:
            logger.info("Listing EC2 instances")
            
            kwargs = {}
            if filters:
                kwargs['Filters'] = filters
            
            response = self.ec2_client.describe_instances(**kwargs)
            
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append(instance)
            
            logger.info(f"Found {len(instances)} EC2 instances")
            return instances
            
        except Exception as e:
            logger.error(f"Error listing EC2 instances: {e}")
            raise AWSResourceError(f"Failed to list EC2 instances: {e}")
    
    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Get details for a specific EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID
            
        Returns:
            Instance details dictionary
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error getting the instance
        """
        try:
            logger.info(f"Getting EC2 instance: {instance_id}")
            
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            
            if not response.get('Reservations'):
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            
            instance = response['Reservations'][0]['Instances'][0]
            logger.info(f"Successfully retrieved instance: {instance_id}")
            return instance
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise ResourceNotFoundError(f"EC2 instance not found: {instance_id}")
            logger.error(f"Error getting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to get EC2 instance {instance_id}: {e}")
        except Exception as e:
            logger.error(f"Error getting EC2 instance {instance_id}: {e}")
            raise AWSResourceError(f"Failed to get EC2 instance {instance_id}: {e}")
    
    def list_security_groups(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        List all security groups with optional filters.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of security group dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing security groups
        """
        try:
            logger.info("Listing security groups")
            
            kwargs = {}
            if filters:
                kwargs['Filters'] = filters
            
            response = self.ec2_client.describe_security_groups(**kwargs)
            security_groups = response.get('SecurityGroups', [])
            
            logger.info(f"Found {len(security_groups)} security groups")
            return security_groups
            
        except Exception as e:
            logger.error(f"Error listing security groups: {e}")
            raise AWSResourceError(f"Failed to list security groups: {e}")
    
    def get_security_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get details for a specific security group.
        
        Args:
            group_id: The security group ID
            
        Returns:
            Security group details dictionary
            
        Raises:
            ResourceNotFoundError: If the security group is not found
            AWSResourceError: If there's an error getting the security group
        """
        try:
            logger.info(f"Getting security group: {group_id}")
            
            response = self.ec2_client.describe_security_groups(GroupIds=[group_id])
            
            if not response.get('SecurityGroups'):
                raise ResourceNotFoundError(f"Security group not found: {group_id}")
            
            security_group = response['SecurityGroups'][0]
            logger.info(f"Successfully retrieved security group: {group_id}")
            return security_group
            
        except self.ec2_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroupId.NotFound':
                raise ResourceNotFoundError(f"Security group not found: {group_id}")
            logger.error(f"Error getting security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to get security group {group_id}: {e}")
        except Exception as e:
            logger.error(f"Error getting security group {group_id}: {e}")
            raise AWSResourceError(f"Failed to get security group {group_id}: {e}")
    
    def list_key_pairs(self) -> List[Dict[str, Any]]:
        """
        List all EC2 key pairs.
        
        Returns:
            List of key pair dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing key pairs
        """
        try:
            logger.info("Listing EC2 key pairs")
            
            response = self.ec2_client.describe_key_pairs()
            key_pairs = response.get('KeyPairs', [])
            
            logger.info(f"Found {len(key_pairs)} key pairs")
            return key_pairs
            
        except Exception as e:
            logger.error(f"Error listing key pairs: {e}")
            raise AWSResourceError(f"Failed to list key pairs: {e}")
    
    def list_vpcs(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        List all VPCs with optional filters.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of VPC dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing VPCs
        """
        try:
            logger.info("Listing VPCs")
            
            kwargs = {}
            if filters:
                kwargs['Filters'] = filters
            
            response = self.ec2_client.describe_vpcs(**kwargs)
            vpcs = response.get('Vpcs', [])
            
            logger.info(f"Found {len(vpcs)} VPCs")
            return vpcs
            
        except Exception as e:
            logger.error(f"Error listing VPCs: {e}")
            raise AWSResourceError(f"Failed to list VPCs: {e}")
    
    def list_subnets(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all subnets, optionally filtered by VPC.
        
        Args:
            vpc_id: Optional VPC ID to filter subnets
            
        Returns:
            List of subnet dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing subnets
        """
        try:
            logger.info(f"Listing subnets{f' for VPC {vpc_id}' if vpc_id else ''}")
            
            kwargs = {}
            if vpc_id:
                kwargs['Filters'] = [{'Name': 'vpc-id', 'Values': [vpc_id]}]
            
            response = self.ec2_client.describe_subnets(**kwargs)
            subnets = response.get('Subnets', [])
            
            logger.info(f"Found {len(subnets)} subnets")
            return subnets
            
        except Exception as e:
            logger.error(f"Error listing subnets: {e}")
            raise AWSResourceError(f"Failed to list subnets: {e}")
    
    def list_amis(self, owners: Optional[List[str]] = None, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        List AMIs with optional filters.
        
        Args:
            owners: Optional list of owner IDs to filter AMIs
            filters: Optional filters to apply to the query
            
        Returns:
            List of AMI dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing AMIs
        """
        try:
            logger.info("Listing AMIs")
            
            kwargs = {}
            if owners:
                kwargs['Owners'] = owners
            if filters:
                kwargs['Filters'] = filters
            
            response = self.ec2_client.describe_images(**kwargs)
            amis = response.get('Images', [])
            
            logger.info(f"Found {len(amis)} AMIs")
            return amis
            
        except Exception as e:
            logger.error(f"Error listing AMIs: {e}")
            raise AWSResourceError(f"Failed to list AMIs: {e}")
    
    def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific EC2 instance.
        
        Args:
            instance_id: The EC2 instance ID
            
        Returns:
            Instance status dictionary
            
        Raises:
            ResourceNotFoundError: If the instance is not found
            AWSResourceError: If there's an error getting the instance status
        """
        try:
            logger.info(f"Getting status for EC2 instance: {instance_id}")
            
            response = self.ec2_client.describe_instance_status(InstanceIds=[instance_id])
            
            if not response.get('InstanceStatuses'):
                # Instance might exist but not have status data yet
                instance = self.get_instance(instance_id)
                return {
                    'InstanceId': instance_id,
                    'InstanceState': instance.get('State', {}),
                    'SystemStatus': {'Status': 'unknown'},
                    'InstanceStatus': {'Status': 'unknown'}
                }
            
            status = response['InstanceStatuses'][0]
            logger.info(f"Successfully retrieved status for instance: {instance_id}")
            return status
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting instance status {instance_id}: {e}")
            raise AWSResourceError(f"Failed to get instance status {instance_id}: {e}")
