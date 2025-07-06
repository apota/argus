"""
Elastic Beanstalk Writer for AWS resource management.

This module provides write operations for AWS Elastic Beanstalk resources
including creating applications, environments, application versions, and managing deployments.
"""

import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EBSWriter:
    """Writer class for AWS Elastic Beanstalk resources."""
    
    def __init__(self, client_manager):
        """
        Initialize EBS Writer.
        
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
    
    def create_application(self, application_name: str, description: str = None, 
                          resource_lifecycle_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new Elastic Beanstalk application.
        
        Args:
            application_name: Name of the application
            description: Optional description
            resource_lifecycle_config: Optional resource lifecycle configuration
            
        Returns:
            Application creation response
        """
        try:
            logger.info("Creating application: %s", application_name)
            params = {
                'ApplicationName': application_name
            }
            
            if description:
                params['Description'] = description
            if resource_lifecycle_config:
                params['ResourceLifecycleConfig'] = resource_lifecycle_config
            
            response = self.client.create_application(**params)
            logger.info("Successfully created application: %s", application_name)
            return response.get('Application', {})
        except ClientError as e:
            logger.error("Error creating application %s: %s", application_name, e)
            raise
    
    def delete_application(self, application_name: str, terminate_env_by_force: bool = False) -> None:
        """
        Delete an Elastic Beanstalk application.
        
        Args:
            application_name: Name of the application to delete
            terminate_env_by_force: Whether to terminate environments by force
        """
        try:
            logger.info("Deleting application: %s", application_name)
            self.client.delete_application(
                ApplicationName=application_name,
                TerminateEnvByForce=terminate_env_by_force
            )
            logger.info("Successfully deleted application: %s", application_name)
        except ClientError as e:
            logger.error("Error deleting application %s: %s", application_name, e)
            raise
    
    def create_application_version(self, application_name: str, version_label: str,
                                 source_bundle: Dict[str, str] = None,
                                 description: str = None) -> Dict[str, Any]:
        """
        Create a new application version.
        
        Args:
            application_name: Name of the application
            version_label: Version label
            source_bundle: Source bundle S3 location
            description: Optional description
            
        Returns:
            Application version creation response
        """
        try:
            logger.info("Creating application version: %s/%s", application_name, version_label)
            params = {
                'ApplicationName': application_name,
                'VersionLabel': version_label
            }
            
            if source_bundle:
                params['SourceBundle'] = source_bundle
            if description:
                params['Description'] = description
            
            response = self.client.create_application_version(**params)
            logger.info("Successfully created application version: %s/%s", application_name, version_label)
            return response.get('ApplicationVersion', {})
        except ClientError as e:
            logger.error("Error creating application version %s/%s: %s", application_name, version_label, e)
            raise
    
    def delete_application_version(self, application_name: str, version_label: str,
                                 delete_source_bundle: bool = False) -> None:
        """
        Delete an application version.
        
        Args:
            application_name: Name of the application
            version_label: Version label to delete
            delete_source_bundle: Whether to delete the source bundle from S3
        """
        try:
            logger.info("Deleting application version: %s/%s", application_name, version_label)
            self.client.delete_application_version(
                ApplicationName=application_name,
                VersionLabel=version_label,
                DeleteSourceBundle=delete_source_bundle
            )
            logger.info("Successfully deleted application version: %s/%s", application_name, version_label)
        except ClientError as e:
            logger.error("Error deleting application version %s/%s: %s", application_name, version_label, e)
            raise
    
    def create_environment(self, application_name: str, environment_name: str,
                          solution_stack_name: str = None, platform_arn: str = None,
                          version_label: str = None, template_name: str = None,
                          description: str = None, option_settings: List[Dict[str, Any]] = None,
                          tags: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new environment.
        
        Args:
            application_name: Name of the application
            environment_name: Name of the environment
            solution_stack_name: Solution stack name
            platform_arn: Platform ARN (alternative to solution_stack_name)
            version_label: Application version to deploy
            template_name: Configuration template name
            description: Optional description
            option_settings: Configuration option settings
            tags: Environment tags
            
        Returns:
            Environment creation response
        """
        try:
            logger.info("Creating environment: %s for application: %s", environment_name, application_name)
            params = {
                'ApplicationName': application_name,
                'EnvironmentName': environment_name
            }
            
            if solution_stack_name:
                params['SolutionStackName'] = solution_stack_name
            if platform_arn:
                params['PlatformArn'] = platform_arn
            if version_label:
                params['VersionLabel'] = version_label
            if template_name:
                params['TemplateName'] = template_name
            if description:
                params['Description'] = description
            if option_settings:
                params['OptionSettings'] = option_settings
            if tags:
                params['Tags'] = tags
            
            response = self.client.create_environment(**params)
            logger.info("Successfully created environment: %s", environment_name)
            return response
        except ClientError as e:
            logger.error("Error creating environment %s: %s", environment_name, e)
            raise
    
    def terminate_environment(self, environment_id: str = None, environment_name: str = None,
                            terminate_resources: bool = True, force_terminate: bool = False) -> Dict[str, Any]:
        """
        Terminate an environment.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
            terminate_resources: Whether to terminate AWS resources
            force_terminate: Whether to force termination
            
        Returns:
            Termination response
        """
        try:
            params = {
                'TerminateResources': terminate_resources,
                'ForceTerminate': force_terminate
            }
            
            if environment_id:
                params['EnvironmentId'] = environment_id
                logger.info("Terminating environment by ID: %s", environment_id)
            elif environment_name:
                params['EnvironmentName'] = environment_name
                logger.info("Terminating environment by name: %s", environment_name)
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            response = self.client.terminate_environment(**params)
            logger.info("Successfully initiated environment termination")
            return response
        except ClientError as e:
            logger.error("Error terminating environment: %s", e)
            raise
    
    def update_environment(self, environment_id: str = None, environment_name: str = None,
                          version_label: str = None, template_name: str = None,
                          solution_stack_name: str = None, platform_arn: str = None,
                          option_settings: List[Dict[str, Any]] = None,
                          options_to_remove: List[Dict[str, str]] = None,
                          description: str = None) -> Dict[str, Any]:
        """
        Update an environment.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
            version_label: New application version
            template_name: Configuration template
            solution_stack_name: New solution stack
            platform_arn: New platform ARN
            option_settings: Configuration options to update
            options_to_remove: Configuration options to remove
            description: New description
            
        Returns:
            Update response
        """
        try:
            params = {}
            
            if environment_id:
                params['EnvironmentId'] = environment_id
                logger.info("Updating environment by ID: %s", environment_id)
            elif environment_name:
                params['EnvironmentName'] = environment_name
                logger.info("Updating environment by name: %s", environment_name)
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            if version_label:
                params['VersionLabel'] = version_label
            if template_name:
                params['TemplateName'] = template_name
            if solution_stack_name:
                params['SolutionStackName'] = solution_stack_name
            if platform_arn:
                params['PlatformArn'] = platform_arn
            if option_settings:
                params['OptionSettings'] = option_settings
            if options_to_remove:
                params['OptionsToRemove'] = options_to_remove
            if description:
                params['Description'] = description
            
            response = self.client.update_environment(**params)
            logger.info("Successfully updated environment")
            return response
        except ClientError as e:
            logger.error("Error updating environment: %s", e)
            raise
    
    def swap_environment_cnames(self, source_environment_id: str = None, source_environment_name: str = None,
                               destination_environment_id: str = None, destination_environment_name: str = None) -> None:
        """
        Swap CNAMEs between two environments.
        
        Args:
            source_environment_id: Source environment ID
            source_environment_name: Source environment name
            destination_environment_id: Destination environment ID
            destination_environment_name: Destination environment name
        """
        try:
            params = {}
            
            if source_environment_id:
                params['SourceEnvironmentId'] = source_environment_id
            elif source_environment_name:
                params['SourceEnvironmentName'] = source_environment_name
            else:
                raise ValueError("Either source_environment_id or source_environment_name must be provided")
            
            if destination_environment_id:
                params['DestinationEnvironmentId'] = destination_environment_id
            elif destination_environment_name:
                params['DestinationEnvironmentName'] = destination_environment_name
            else:
                raise ValueError("Either destination_environment_id or destination_environment_name must be provided")
            
            logger.info("Swapping environment CNAMEs")
            self.client.swap_environment_cnames(**params)
            logger.info("Successfully swapped environment CNAMEs")
        except ClientError as e:
            logger.error("Error swapping environment CNAMEs: %s", e)
            raise
    
    def restart_app_server(self, environment_id: str = None, environment_name: str = None) -> None:
        """
        Restart the application server on all instances.
        
        Args:
            environment_id: Environment ID
            environment_name: Environment name
        """
        try:
            params = {}
            
            if environment_id:
                params['EnvironmentId'] = environment_id
                logger.info("Restarting app server for environment ID: %s", environment_id)
            elif environment_name:
                params['EnvironmentName'] = environment_name
                logger.info("Restarting app server for environment: %s", environment_name)
            else:
                raise ValueError("Either environment_id or environment_name must be provided")
            
            self.client.restart_app_server(**params)
            logger.info("Successfully initiated app server restart")
        except ClientError as e:
            logger.error("Error restarting app server: %s", e)
            raise
