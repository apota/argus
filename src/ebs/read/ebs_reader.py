"""
Elastic Beanstalk Reader for AWS resource exploration.

This module provides read-only operations for AWS Elastic Beanstalk resources
including applications, environments, application versions, and configurations.
"""

import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EBSReader:
    """Reader class for AWS Elastic Beanstalk resources."""
    
    def __init__(self, client_manager):
        """
        Initialize EBS Reader.
        
        Args:
            client_manager: AWS client manager instance
        """
        self.client_manager = client_manager
        self._client = None
    
    @property
    def client(self):
        """Get or create the Elastic Beanstalk client."""
        if self._client is None:
            self._client = self.client_manager.get_client('elasticbeanstalk')
        return self._client
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """
        List all Elastic Beanstalk applications.
        
        Returns:
            List of application dictionaries
        """
        try:
            logger.info("Listing Elastic Beanstalk applications")
            response = self.client.describe_applications()
            applications = response.get('Applications', [])
            logger.info(f"Found {len(applications)} applications")
            return applications
        except ClientError as e:
            logger.error(f"Error listing applications: {e}")
            raise
    
    def get_application(self, application_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific application.
        
        Args:
            application_name: Name of the application
            
        Returns:
            Application details or None if not found
        """
        try:
            logger.info(f"Getting application details: {application_name}")
            response = self.client.describe_applications(
                ApplicationNames=[application_name]
            )
            applications = response.get('Applications', [])
            if applications:
                return applications[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting application {application_name}: {e}")
            raise
    
    def list_environments(self, application_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List environments, optionally filtered by application.
        
        Args:
            application_name: Optional application name to filter by
            
        Returns:
            List of environment dictionaries
        """
        try:
            logger.info(f"Listing environments for application: {application_name or 'all'}")
            params = {}
            if application_name:
                params['ApplicationName'] = application_name
            
            response = self.client.describe_environments(**params)
            environments = response.get('Environments', [])
            logger.info(f"Found {len(environments)} environments")
            return environments
        except ClientError as e:
            logger.error(f"Error listing environments: {e}")
            raise
    
    def get_environment(self, environment_id: str = None, environment_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific environment.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
            
        Returns:
            Environment details or None if not found
        """
        try:
            params = {}
            if environment_id:
                params['EnvironmentIds'] = [environment_id]
                logger.info(f"Getting environment details by ID: {environment_id}")
            elif environment_name:
                params['EnvironmentNames'] = [environment_name]
                logger.info(f"Getting environment details by name: {environment_name}")
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            response = self.client.describe_environments(**params)
            environments = response.get('Environments', [])
            if environments:
                return environments[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting environment: {e}")
            raise
    
    def list_application_versions(self, application_name: str) -> List[Dict[str, Any]]:
        """
        List application versions for a specific application.
        
        Args:
            application_name: Name of the application
            
        Returns:
            List of application version dictionaries
        """
        try:
            logger.info(f"Listing application versions for: {application_name}")
            response = self.client.describe_application_versions(
                ApplicationName=application_name
            )
            versions = response.get('ApplicationVersions', [])
            logger.info(f"Found {len(versions)} application versions")
            return versions
        except ClientError as e:
            logger.error(f"Error listing application versions: {e}")
            raise
    
    def get_application_version(self, application_name: str, version_label: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific application version.
        
        Args:
            application_name: Name of the application
            version_label: Version label
            
        Returns:
            Application version details or None if not found
        """
        try:
            logger.info(f"Getting application version: {application_name}/{version_label}")
            response = self.client.describe_application_versions(
                ApplicationName=application_name,
                VersionLabels=[version_label]
            )
            versions = response.get('ApplicationVersions', [])
            if versions:
                return versions[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting application version: {e}")
            raise
    
    def get_environment_health(self, environment_id: str = None, environment_name: str = None) -> Dict[str, Any]:
        """
        Get health information for an environment.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
            
        Returns:
            Environment health information
        """
        try:
            if environment_id:
                logger.info(f"Getting environment health by ID: {environment_id}")
            elif environment_name:
                logger.info(f"Getting environment health by name: {environment_name}")
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            params = {}
            if environment_id:
                params['EnvironmentId'] = environment_id
            elif environment_name:
                params['EnvironmentName'] = environment_name
            
            response = self.client.describe_environment_health(**params)
            return response
        except ClientError as e:
            logger.error(f"Error getting environment health: {e}")
            raise
    
    def list_configuration_templates(self, application_name: str) -> List[Dict[str, Any]]:
        """
        List configuration templates for an application.
        
        Args:
            application_name: Name of the application
            
        Returns:
            List of configuration template dictionaries
        """
        try:
            logger.info(f"Listing configuration templates for: {application_name}")
            response = self.client.describe_configuration_settings(
                ApplicationName=application_name
            )
            templates = response.get('ConfigurationSettings', [])
            logger.info(f"Found {len(templates)} configuration templates")
            return templates
        except ClientError as e:
            logger.error(f"Error listing configuration templates: {e}")
            raise
    
    def get_environment_resources(self, environment_id: str = None, environment_name: str = None) -> Dict[str, Any]:
        """
        Get AWS resources used by an environment.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
            
        Returns:
            Environment resources information
        """
        try:
            params = {}
            if environment_id:
                params['EnvironmentId'] = environment_id
                logger.info(f"Getting environment resources by ID: {environment_id}")
            elif environment_name:
                params['EnvironmentName'] = environment_name
                logger.info(f"Getting environment resources by name: {environment_name}")
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            response = self.client.describe_environment_resources(**params)
            return response.get('EnvironmentResources', {})
        except ClientError as e:
            logger.error(f"Error getting environment resources: {e}")
            raise
    
    def list_platform_versions(self) -> List[Dict[str, Any]]:
        """
        List available platform versions.
        
        Returns:
            List of platform version dictionaries
        """
        try:
            logger.info("Listing platform versions")
            response = self.client.list_platform_versions()
            platforms = response.get('PlatformSummaryList', [])
            logger.info(f"Found {len(platforms)} platform versions")
            return platforms
        except ClientError as e:
            logger.error(f"Error listing platform versions: {e}")
            raise
