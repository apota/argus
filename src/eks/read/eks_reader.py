"""
Elastic Kubernetes Service Reader for AWS resource exploration.

This module provides read-only operations for AWS EKS resources
including clusters, node groups, Fargate profiles, and add-ons.
"""

import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EKSReader:
    """Reader class for AWS EKS resources."""
    
    def __init__(self, client_manager):
        """
        Initialize EKS Reader.
        
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
    
    def list_clusters(self) -> List[str]:
        """
        List all EKS cluster names.
        
        Returns:
            List of cluster names
        """
        try:
            logger.info("Listing EKS clusters")
            response = self.client.list_clusters()
            clusters = response.get('clusters', [])
            logger.info("Found %d clusters", len(clusters))
            return clusters
        except ClientError as e:
            logger.error("Error listing clusters: %s", e)
            raise
    
    def describe_cluster(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            Cluster details or None if not found
        """
        try:
            logger.info("Describing cluster: %s", cluster_name)
            response = self.client.describe_cluster(name=cluster_name)
            return response.get('cluster')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Cluster not found: %s", cluster_name)
                return None
            logger.error("Error describing cluster %s: %s", cluster_name, e)
            raise
    
    def list_nodegroups(self, cluster_name: str) -> List[str]:
        """
        List node groups for a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of node group names
        """
        try:
            logger.info("Listing node groups for cluster: %s", cluster_name)
            response = self.client.list_nodegroups(clusterName=cluster_name)
            nodegroups = response.get('nodegroups', [])
            logger.info("Found %d node groups", len(nodegroups))
            return nodegroups
        except ClientError as e:
            logger.error("Error listing node groups for cluster %s: %s", cluster_name, e)
            raise
    
    def describe_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific node group.
        
        Args:
            cluster_name: Name of the cluster
            nodegroup_name: Name of the node group
            
        Returns:
            Node group details or None if not found
        """
        try:
            logger.info("Describing node group: %s/%s", cluster_name, nodegroup_name)
            response = self.client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            return response.get('nodegroup')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Node group not found: %s/%s", cluster_name, nodegroup_name)
                return None
            logger.error("Error describing node group %s/%s: %s", cluster_name, nodegroup_name, e)
            raise
    
    def list_fargate_profiles(self, cluster_name: str) -> List[str]:
        """
        List Fargate profiles for a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of Fargate profile names
        """
        try:
            logger.info("Listing Fargate profiles for cluster: %s", cluster_name)
            response = self.client.list_fargate_profiles(clusterName=cluster_name)
            profiles = response.get('fargateProfileNames', [])
            logger.info("Found %d Fargate profiles", len(profiles))
            return profiles
        except ClientError as e:
            logger.error("Error listing Fargate profiles for cluster %s: %s", cluster_name, e)
            raise
    
    def describe_fargate_profile(self, cluster_name: str, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific Fargate profile.
        
        Args:
            cluster_name: Name of the cluster
            profile_name: Name of the Fargate profile
            
        Returns:
            Fargate profile details or None if not found
        """
        try:
            logger.info("Describing Fargate profile: %s/%s", cluster_name, profile_name)
            response = self.client.describe_fargate_profile(
                clusterName=cluster_name,
                fargateProfileName=profile_name
            )
            return response.get('fargateProfile')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Fargate profile not found: %s/%s", cluster_name, profile_name)
                return None
            logger.error("Error describing Fargate profile %s/%s: %s", cluster_name, profile_name, e)
            raise
    
    def list_addons(self, cluster_name: str) -> List[str]:
        """
        List add-ons for a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of add-on names
        """
        try:
            logger.info("Listing add-ons for cluster: %s", cluster_name)
            response = self.client.list_addons(clusterName=cluster_name)
            addons = response.get('addons', [])
            logger.info("Found %d add-ons", len(addons))
            return addons
        except ClientError as e:
            logger.error("Error listing add-ons for cluster %s: %s", cluster_name, e)
            raise
    
    def describe_addon(self, cluster_name: str, addon_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific add-on.
        
        Args:
            cluster_name: Name of the cluster
            addon_name: Name of the add-on
            
        Returns:
            Add-on details or None if not found
        """
        try:
            logger.info("Describing add-on: %s/%s", cluster_name, addon_name)
            response = self.client.describe_addon(
                clusterName=cluster_name,
                addonName=addon_name
            )
            return response.get('addon')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Add-on not found: %s/%s", cluster_name, addon_name)
                return None
            logger.error("Error describing add-on %s/%s: %s", cluster_name, addon_name, e)
            raise
    
    def describe_addon_versions(self, addon_name: str, kubernetes_version: str = None) -> List[Dict[str, Any]]:
        """
        Get available versions for a specific add-on.
        
        Args:
            addon_name: Name of the add-on
            kubernetes_version: Optional Kubernetes version filter
            
        Returns:
            List of add-on version information
        """
        try:
            logger.info("Describing add-on versions for: %s", addon_name)
            params = {'addonName': addon_name}
            if kubernetes_version:
                params['kubernetesVersion'] = kubernetes_version
            
            response = self.client.describe_addon_versions(**params)
            versions = response.get('addons', [])
            logger.info("Found %d add-on versions", len(versions))
            return versions
        except ClientError as e:
            logger.error("Error describing add-on versions for %s: %s", addon_name, e)
            raise
    
    def list_identity_provider_configs(self, cluster_name: str) -> List[Dict[str, Any]]:
        """
        List identity provider configurations for a cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of identity provider configurations
        """
        try:
            logger.info("Listing identity provider configs for cluster: %s", cluster_name)
            response = self.client.list_identity_provider_configs(clusterName=cluster_name)
            configs = response.get('identityProviderConfigs', [])
            logger.info("Found %d identity provider configs", len(configs))
            return configs
        except ClientError as e:
            logger.error("Error listing identity provider configs for cluster %s: %s", cluster_name, e)
            raise
    
    def describe_identity_provider_config(self, cluster_name: str, config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific identity provider configuration.
        
        Args:
            cluster_name: Name of the cluster
            config: Identity provider config identifier (type and name)
            
        Returns:
            Identity provider config details or None if not found
        """
        try:
            logger.info("Describing identity provider config: %s", config)
            response = self.client.describe_identity_provider_config(
                clusterName=cluster_name,
                identityProviderConfig=config
            )
            return response.get('identityProviderConfig')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Identity provider config not found: %s", config)
                return None
            logger.error("Error describing identity provider config %s: %s", config, e)
            raise
    
    def get_cluster_oidc_issuer_url(self, cluster_name: str) -> Optional[str]:
        """
        Get the OIDC issuer URL for a cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            OIDC issuer URL or None if not available
        """
        try:
            cluster = self.describe_cluster(cluster_name)
            if cluster and 'identity' in cluster:
                oidc = cluster['identity'].get('oidc', {})
                return oidc.get('issuer')
            return None
        except Exception as e:
            logger.error("Error getting OIDC issuer URL for cluster %s: %s", cluster_name, e)
            return None
