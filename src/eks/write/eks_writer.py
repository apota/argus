"""
Elastic Kubernetes Service Writer for AWS resource management.

This module provides write operations for AWS EKS resources
including creating clusters, node groups, Fargate profiles, and managing add-ons.
"""

import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EKSWriter:
    """Writer class for AWS EKS resources."""
    
    def __init__(self, client_manager):
        """
        Initialize EKS Writer.
        
        Args:
            client_manager: AWS client manager instance
        """
        self.client_manager = client_manager
        self._client = None
    
    @property
    def client(self):
        """Get or create the EKS client."""
        if self._client is None:
            self._client = self.client_manager.get_client('eks')
        return self._client
    
    def create_cluster(self, name: str, version: str, role_arn: str, 
                      resources_vpc_config: Dict[str, Any],
                      kubernetes_network_config: Dict[str, Any] = None,
                      logging: Dict[str, Any] = None,
                      client_request_token: str = None,
                      tags: Dict[str, str] = None,
                      encryption_config: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new EKS cluster.
        
        Args:
            name: Cluster name
            version: Kubernetes version
            role_arn: Service role ARN
            resources_vpc_config: VPC configuration
            kubernetes_network_config: Optional network configuration
            logging: Optional logging configuration
            client_request_token: Optional idempotency token
            tags: Optional tags
            encryption_config: Optional encryption configuration
            
        Returns:
            Cluster creation response
        """
        try:
            logger.info("Creating EKS cluster: %s", name)
            params = {
                'name': name,
                'version': version,
                'roleArn': role_arn,
                'resourcesVpcConfig': resources_vpc_config
            }
            
            if kubernetes_network_config:
                params['kubernetesNetworkConfig'] = kubernetes_network_config
            if logging:
                params['logging'] = logging
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            if tags:
                params['tags'] = tags
            if encryption_config:
                params['encryptionConfig'] = encryption_config
            
            response = self.client.create_cluster(**params)
            logger.info("Successfully initiated cluster creation: %s", name)
            return response.get('cluster', {})
        except ClientError as e:
            logger.error("Error creating cluster %s: %s", name, e)
            raise
    
    def delete_cluster(self, name: str) -> Dict[str, Any]:
        """
        Delete an EKS cluster.
        
        Args:
            name: Cluster name
            
        Returns:
            Cluster deletion response
        """
        try:
            logger.info("Deleting EKS cluster: %s", name)
            response = self.client.delete_cluster(name=name)
            logger.info("Successfully initiated cluster deletion: %s", name)
            return response.get('cluster', {})
        except ClientError as e:
            logger.error("Error deleting cluster %s: %s", name, e)
            raise
    
    def update_cluster_version(self, name: str, version: str, 
                              client_request_token: str = None) -> Dict[str, Any]:
        """
        Update the Kubernetes version of a cluster.
        
        Args:
            name: Cluster name
            version: New Kubernetes version
            client_request_token: Optional idempotency token
            
        Returns:
            Update response
        """
        try:
            logger.info("Updating cluster version: %s to %s", name, version)
            params = {
                'name': name,
                'version': version
            }
            
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            
            response = self.client.update_cluster_version(**params)
            logger.info("Successfully initiated cluster version update: %s", name)
            return response.get('update', {})
        except ClientError as e:
            logger.error("Error updating cluster version %s: %s", name, e)
            raise
    
    def update_cluster_config(self, name: str, resources_vpc_config: Dict[str, Any] = None,
                             logging: Dict[str, Any] = None,
                             client_request_token: str = None) -> Dict[str, Any]:
        """
        Update cluster configuration.
        
        Args:
            name: Cluster name
            resources_vpc_config: Optional VPC configuration update
            logging: Optional logging configuration update
            client_request_token: Optional idempotency token
            
        Returns:
            Update response
        """
        try:
            logger.info("Updating cluster config: %s", name)
            params = {'name': name}
            
            if resources_vpc_config:
                params['resourcesVpcConfig'] = resources_vpc_config
            if logging:
                params['logging'] = logging
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            
            response = self.client.update_cluster_config(**params)
            logger.info("Successfully initiated cluster config update: %s", name)
            return response.get('update', {})
        except ClientError as e:
            logger.error("Error updating cluster config %s: %s", name, e)
            raise
    
    def create_nodegroup(self, cluster_name: str, nodegroup_name: str, 
                        subnets: List[str], node_role: str,
                        scaling_config: Dict[str, int] = None,
                        disk_size: int = None, instance_types: List[str] = None,
                        ami_type: str = None, remote_access: Dict[str, Any] = None,
                        labels: Dict[str, str] = None, taints: List[Dict[str, Any]] = None,
                        tags: Dict[str, str] = None, client_request_token: str = None,
                        launch_template: Dict[str, Any] = None,
                        update_config: Dict[str, Any] = None,
                        capacity_type: str = None, version: str = None,
                        release_version: str = None) -> Dict[str, Any]:
        """
        Create a managed node group.
        
        Args:
            cluster_name: Cluster name
            nodegroup_name: Node group name
            subnets: List of subnet IDs
            node_role: Node instance role ARN
            scaling_config: Optional scaling configuration
            disk_size: Optional disk size in GiB
            instance_types: Optional list of instance types
            ami_type: Optional AMI type
            remote_access: Optional remote access configuration
            labels: Optional Kubernetes labels
            taints: Optional Kubernetes taints
            tags: Optional AWS tags
            client_request_token: Optional idempotency token
            launch_template: Optional launch template
            update_config: Optional update configuration
            capacity_type: Optional capacity type (ON_DEMAND or SPOT)
            version: Optional Kubernetes version
            release_version: Optional AMI release version
            
        Returns:
            Node group creation response
        """
        try:
            logger.info("Creating node group: %s/%s", cluster_name, nodegroup_name)
            params = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name,
                'subnets': subnets,
                'nodeRole': node_role
            }
            
            if scaling_config:
                params['scalingConfig'] = scaling_config
            if disk_size:
                params['diskSize'] = disk_size
            if instance_types:
                params['instanceTypes'] = instance_types
            if ami_type:
                params['amiType'] = ami_type
            if remote_access:
                params['remoteAccess'] = remote_access
            if labels:
                params['labels'] = labels
            if taints:
                params['taints'] = taints
            if tags:
                params['tags'] = tags
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            if launch_template:
                params['launchTemplate'] = launch_template
            if update_config:
                params['updateConfig'] = update_config
            if capacity_type:
                params['capacityType'] = capacity_type
            if version:
                params['version'] = version
            if release_version:
                params['releaseVersion'] = release_version
            
            response = self.client.create_nodegroup(**params)
            logger.info("Successfully initiated node group creation: %s/%s", cluster_name, nodegroup_name)
            return response.get('nodegroup', {})
        except ClientError as e:
            logger.error("Error creating node group %s/%s: %s", cluster_name, nodegroup_name, e)
            raise
    
    def delete_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Dict[str, Any]:
        """
        Delete a managed node group.
        
        Args:
            cluster_name: Cluster name
            nodegroup_name: Node group name
            
        Returns:
            Node group deletion response
        """
        try:
            logger.info("Deleting node group: %s/%s", cluster_name, nodegroup_name)
            response = self.client.delete_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            logger.info("Successfully initiated node group deletion: %s/%s", cluster_name, nodegroup_name)
            return response.get('nodegroup', {})
        except ClientError as e:
            logger.error("Error deleting node group %s/%s: %s", cluster_name, nodegroup_name, e)
            raise
    
    def update_nodegroup_config(self, cluster_name: str, nodegroup_name: str,
                               labels: Dict[str, str] = None, taints: List[Dict[str, Any]] = None,
                               scaling_config: Dict[str, int] = None,
                               update_config: Dict[str, Any] = None,
                               client_request_token: str = None) -> Dict[str, Any]:
        """
        Update node group configuration.
        
        Args:
            cluster_name: Cluster name
            nodegroup_name: Node group name
            labels: Optional Kubernetes labels update
            taints: Optional Kubernetes taints update
            scaling_config: Optional scaling configuration update
            update_config: Optional update configuration
            client_request_token: Optional idempotency token
            
        Returns:
            Update response
        """
        try:
            logger.info("Updating node group config: %s/%s", cluster_name, nodegroup_name)
            params = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name
            }
            
            if labels:
                params['labels'] = labels
            if taints:
                params['taints'] = taints
            if scaling_config:
                params['scalingConfig'] = scaling_config
            if update_config:
                params['updateConfig'] = update_config
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            
            response = self.client.update_nodegroup_config(**params)
            logger.info("Successfully initiated node group config update: %s/%s", cluster_name, nodegroup_name)
            return response.get('update', {})
        except ClientError as e:
            logger.error("Error updating node group config %s/%s: %s", cluster_name, nodegroup_name, e)
            raise
    
    def create_fargate_profile(self, fargate_profile_name: str, cluster_name: str,
                              pod_execution_role_arn: str, subnets: List[str] = None,
                              selectors: List[Dict[str, Any]] = None,
                              client_request_token: str = None,
                              tags: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a Fargate profile.
        
        Args:
            fargate_profile_name: Fargate profile name
            cluster_name: Cluster name
            pod_execution_role_arn: Pod execution role ARN
            subnets: Optional list of subnet IDs
            selectors: Optional pod selectors
            client_request_token: Optional idempotency token
            tags: Optional tags
            
        Returns:
            Fargate profile creation response
        """
        try:
            logger.info("Creating Fargate profile: %s/%s", cluster_name, fargate_profile_name)
            params = {
                'fargateProfileName': fargate_profile_name,
                'clusterName': cluster_name,
                'podExecutionRoleArn': pod_execution_role_arn
            }
            
            if subnets:
                params['subnets'] = subnets
            if selectors:
                params['selectors'] = selectors
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            if tags:
                params['tags'] = tags
            
            response = self.client.create_fargate_profile(**params)
            logger.info("Successfully initiated Fargate profile creation: %s/%s", cluster_name, fargate_profile_name)
            return response.get('fargateProfile', {})
        except ClientError as e:
            logger.error("Error creating Fargate profile %s/%s: %s", cluster_name, fargate_profile_name, e)
            raise
    
    def delete_fargate_profile(self, cluster_name: str, fargate_profile_name: str) -> Dict[str, Any]:
        """
        Delete a Fargate profile.
        
        Args:
            cluster_name: Cluster name
            fargate_profile_name: Fargate profile name
            
        Returns:
            Fargate profile deletion response
        """
        try:
            logger.info("Deleting Fargate profile: %s/%s", cluster_name, fargate_profile_name)
            response = self.client.delete_fargate_profile(
                clusterName=cluster_name,
                fargateProfileName=fargate_profile_name
            )
            logger.info("Successfully initiated Fargate profile deletion: %s/%s", cluster_name, fargate_profile_name)
            return response.get('fargateProfile', {})
        except ClientError as e:
            logger.error("Error deleting Fargate profile %s/%s: %s", cluster_name, fargate_profile_name, e)
            raise
    
    def create_addon(self, cluster_name: str, addon_name: str, addon_version: str = None,
                    service_account_role_arn: str = None, resolve_conflicts: str = None,
                    client_request_token: str = None, tags: Dict[str, str] = None,
                    configuration_values: str = None) -> Dict[str, Any]:
        """
        Create an add-on.
        
        Args:
            cluster_name: Cluster name
            addon_name: Add-on name
            addon_version: Optional add-on version
            service_account_role_arn: Optional service account role ARN
            resolve_conflicts: Optional conflict resolution strategy
            client_request_token: Optional idempotency token
            tags: Optional tags
            configuration_values: Optional JSON configuration values
            
        Returns:
            Add-on creation response
        """
        try:
            logger.info("Creating add-on: %s/%s", cluster_name, addon_name)
            params = {
                'clusterName': cluster_name,
                'addonName': addon_name
            }
            
            if addon_version:
                params['addonVersion'] = addon_version
            if service_account_role_arn:
                params['serviceAccountRoleArn'] = service_account_role_arn
            if resolve_conflicts:
                params['resolveConflicts'] = resolve_conflicts
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            if tags:
                params['tags'] = tags
            if configuration_values:
                params['configurationValues'] = configuration_values
            
            response = self.client.create_addon(**params)
            logger.info("Successfully initiated add-on creation: %s/%s", cluster_name, addon_name)
            return response.get('addon', {})
        except ClientError as e:
            logger.error("Error creating add-on %s/%s: %s", cluster_name, addon_name, e)
            raise
    
    def update_addon(self, cluster_name: str, addon_name: str, addon_version: str = None,
                    service_account_role_arn: str = None, resolve_conflicts: str = None,
                    client_request_token: str = None, configuration_values: str = None) -> Dict[str, Any]:
        """
        Update an add-on.
        
        Args:
            cluster_name: Cluster name
            addon_name: Add-on name
            addon_version: Optional new add-on version
            service_account_role_arn: Optional service account role ARN
            resolve_conflicts: Optional conflict resolution strategy
            client_request_token: Optional idempotency token
            configuration_values: Optional JSON configuration values
            
        Returns:
            Add-on update response
        """
        try:
            logger.info("Updating add-on: %s/%s", cluster_name, addon_name)
            params = {
                'clusterName': cluster_name,
                'addonName': addon_name
            }
            
            if addon_version:
                params['addonVersion'] = addon_version
            if service_account_role_arn:
                params['serviceAccountRoleArn'] = service_account_role_arn
            if resolve_conflicts:
                params['resolveConflicts'] = resolve_conflicts
            if client_request_token:
                params['clientRequestToken'] = client_request_token
            if configuration_values:
                params['configurationValues'] = configuration_values
            
            response = self.client.update_addon(**params)
            logger.info("Successfully initiated add-on update: %s/%s", cluster_name, addon_name)
            return response.get('update', {})
        except ClientError as e:
            logger.error("Error updating add-on %s/%s: %s", cluster_name, addon_name, e)
            raise
    
    def delete_addon(self, cluster_name: str, addon_name: str, preserve: bool = False) -> Dict[str, Any]:
        """
        Delete an add-on.
        
        Args:
            cluster_name: Cluster name
            addon_name: Add-on name
            preserve: Whether to preserve add-on resources in the cluster
            
        Returns:
            Add-on deletion response
        """
        try:
            logger.info("Deleting add-on: %s/%s", cluster_name, addon_name)
            params = {
                'clusterName': cluster_name,
                'addonName': addon_name,
                'preserve': preserve
            }
            
            response = self.client.delete_addon(**params)
            logger.info("Successfully initiated add-on deletion: %s/%s", cluster_name, addon_name)
            return response.get('addon', {})
        except ClientError as e:
            logger.error("Error deleting add-on %s/%s: %s", cluster_name, addon_name, e)
            raise
