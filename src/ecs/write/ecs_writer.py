"""
ECS Writer Module

This module provides functionality for creating and managing AWS ECS resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class ECSWriter:
    """
    A class for creating and managing AWS ECS resources.
    
    This class provides methods to create, update, and delete ECS clusters,
    services, tasks, and task definitions.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the ECS writer.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.ecs_client = self.client_manager.get_client('ecs')
    
    def create_cluster(self, cluster_name: str, 
                      capacity_providers: Optional[List[str]] = None,
                      default_capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
                      tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new ECS cluster.
        
        Args:
            cluster_name: Name of the cluster
            capacity_providers: List of capacity providers
            default_capacity_provider_strategy: Default capacity provider strategy
            tags: Resource tags
            
        Returns:
            Cluster configuration
            
        Raises:
            AWSResourceError: If there's an error creating the cluster
        """
        try:
            logger.info("Creating ECS cluster: %s", cluster_name)
            
            kwargs = {'clusterName': cluster_name}
            
            if capacity_providers:
                kwargs['capacityProviders'] = capacity_providers
            if default_capacity_provider_strategy:
                kwargs['defaultCapacityProviderStrategy'] = default_capacity_provider_strategy
            if tags:
                kwargs['tags'] = tags
            
            response = self.ecs_client.create_cluster(**kwargs)
            
            logger.info("Created ECS cluster: %s", cluster_name)
            return response.get('cluster', {})
            
        except ClientError as e:
            error_message = f"Failed to create ECS cluster {cluster_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def delete_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """
        Delete an ECS cluster.
        
        Args:
            cluster_name: Name or ARN of the cluster
            
        Returns:
            Cluster configuration
            
        Raises:
            ResourceNotFoundError: If the cluster doesn't exist
            AWSResourceError: If there's an error deleting the cluster
        """
        try:
            logger.info("Deleting ECS cluster: %s", cluster_name)
            
            response = self.ecs_client.delete_cluster(cluster=cluster_name)
            
            logger.info("Deleted ECS cluster: %s", cluster_name)
            return response.get('cluster', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ClusterNotFoundException':
                error_message = f"ECS cluster not found: {cluster_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete ECS cluster {cluster_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def create_service(self, service_name: str, task_definition: str,
                      cluster: Optional[str] = None, desired_count: int = 1,
                      launch_type: Optional[str] = None,
                      capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
                      load_balancers: Optional[List[Dict[str, Any]]] = None,
                      service_registries: Optional[List[Dict[str, Any]]] = None,
                      network_configuration: Optional[Dict[str, Any]] = None,
                      tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new ECS service.
        
        Args:
            service_name: Name of the service
            task_definition: Task definition to use
            cluster: Cluster to run the service in
            desired_count: Desired number of tasks
            launch_type: Launch type (EC2, FARGATE)
            capacity_provider_strategy: Capacity provider strategy
            load_balancers: Load balancer configuration
            service_registries: Service registry configuration
            network_configuration: Network configuration for Fargate
            tags: Resource tags
            
        Returns:
            Service configuration
            
        Raises:
            AWSResourceError: If there's an error creating the service
        """
        try:
            logger.info("Creating ECS service: %s", service_name)
            
            kwargs = {
                'serviceName': service_name,
                'taskDefinition': task_definition,
                'desiredCount': desired_count
            }
            
            if cluster:
                kwargs['cluster'] = cluster
            if launch_type:
                kwargs['launchType'] = launch_type
            if capacity_provider_strategy:
                kwargs['capacityProviderStrategy'] = capacity_provider_strategy
            if load_balancers:
                kwargs['loadBalancers'] = load_balancers
            if service_registries:
                kwargs['serviceRegistries'] = service_registries
            if network_configuration:
                kwargs['networkConfiguration'] = network_configuration
            if tags:
                kwargs['tags'] = tags
            
            response = self.ecs_client.create_service(**kwargs)
            
            logger.info("Created ECS service: %s", service_name)
            return response.get('service', {})
            
        except ClientError as e:
            error_message = f"Failed to create ECS service {service_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def update_service(self, service_name: str, cluster: Optional[str] = None,
                      task_definition: Optional[str] = None,
                      desired_count: Optional[int] = None,
                      capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
                      network_configuration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update an existing ECS service.
        
        Args:
            service_name: Name of the service
            cluster: Cluster the service is running in
            task_definition: New task definition
            desired_count: New desired count
            capacity_provider_strategy: New capacity provider strategy
            network_configuration: New network configuration
            
        Returns:
            Updated service configuration
            
        Raises:
            ResourceNotFoundError: If the service doesn't exist
            AWSResourceError: If there's an error updating the service
        """
        try:
            logger.info("Updating ECS service: %s", service_name)
            
            kwargs = {'service': service_name}
            
            if cluster:
                kwargs['cluster'] = cluster
            if task_definition:
                kwargs['taskDefinition'] = task_definition
            if desired_count is not None:
                kwargs['desiredCount'] = desired_count
            if capacity_provider_strategy:
                kwargs['capacityProviderStrategy'] = capacity_provider_strategy
            if network_configuration:
                kwargs['networkConfiguration'] = network_configuration
            
            response = self.ecs_client.update_service(**kwargs)
            
            logger.info("Updated ECS service: %s", service_name)
            return response.get('service', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ServiceNotFoundException':
                error_message = f"ECS service not found: {service_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to update ECS service {service_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def delete_service(self, service_name: str, cluster: Optional[str] = None,
                      force: bool = False) -> Dict[str, Any]:
        """
        Delete an ECS service.
        
        Args:
            service_name: Name of the service
            cluster: Cluster the service is running in
            force: Force deletion even if service has running tasks
            
        Returns:
            Service configuration
            
        Raises:
            ResourceNotFoundError: If the service doesn't exist
            AWSResourceError: If there's an error deleting the service
        """
        try:
            logger.info("Deleting ECS service: %s", service_name)
            
            kwargs = {'service': service_name}
            
            if cluster:
                kwargs['cluster'] = cluster
            if force:
                kwargs['force'] = force
            
            response = self.ecs_client.delete_service(**kwargs)
            
            logger.info("Deleted ECS service: %s", service_name)
            return response.get('service', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ServiceNotFoundException':
                error_message = f"ECS service not found: {service_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete ECS service {service_name}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def register_task_definition(self, family: str, container_definitions: List[Dict[str, Any]],
                                requires_compatibilities: Optional[List[str]] = None,
                                network_mode: Optional[str] = None,
                                cpu: Optional[str] = None, memory: Optional[str] = None,
                                execution_role_arn: Optional[str] = None,
                                task_role_arn: Optional[str] = None,
                                tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Register a new ECS task definition.
        
        Args:
            family: Family name for the task definition
            container_definitions: List of container definitions
            requires_compatibilities: Required launch types (EC2, FARGATE)
            network_mode: Network mode (bridge, host, awsvpc, none)
            cpu: CPU units for Fargate tasks
            memory: Memory for Fargate tasks
            execution_role_arn: Task execution role ARN
            task_role_arn: Task role ARN
            tags: Resource tags
            
        Returns:
            Task definition configuration
            
        Raises:
            AWSResourceError: If there's an error registering the task definition
        """
        try:
            logger.info("Registering ECS task definition: %s", family)
            
            kwargs = {
                'family': family,
                'containerDefinitions': container_definitions
            }
            
            if requires_compatibilities:
                kwargs['requiresCompatibilities'] = requires_compatibilities
            if network_mode:
                kwargs['networkMode'] = network_mode
            if cpu:
                kwargs['cpu'] = cpu
            if memory:
                kwargs['memory'] = memory
            if execution_role_arn:
                kwargs['executionRoleArn'] = execution_role_arn
            if task_role_arn:
                kwargs['taskRoleArn'] = task_role_arn
            if tags:
                kwargs['tags'] = tags
            
            response = self.ecs_client.register_task_definition(**kwargs)
            
            logger.info("Registered ECS task definition: %s", family)
            return response.get('taskDefinition', {})
            
        except ClientError as e:
            error_message = f"Failed to register ECS task definition {family}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def deregister_task_definition(self, task_definition: str) -> Dict[str, Any]:
        """
        Deregister an ECS task definition.
        
        Args:
            task_definition: Task definition ARN or family:revision
            
        Returns:
            Task definition configuration
            
        Raises:
            ResourceNotFoundError: If the task definition doesn't exist
            AWSResourceError: If there's an error deregistering the task definition
        """
        try:
            logger.info("Deregistering ECS task definition: %s", task_definition)
            
            response = self.ecs_client.deregister_task_definition(taskDefinition=task_definition)
            
            logger.info("Deregistered ECS task definition: %s", task_definition)
            return response.get('taskDefinition', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ClientException':
                error_message = f"ECS task definition not found: {task_definition}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to deregister ECS task definition {task_definition}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def run_task(self, task_definition: str, cluster: Optional[str] = None,
                count: int = 1, launch_type: Optional[str] = None,
                capacity_provider_strategy: Optional[List[Dict[str, Any]]] = None,
                network_configuration: Optional[Dict[str, Any]] = None,
                overrides: Optional[Dict[str, Any]] = None,
                tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Run a task using an ECS task definition.
        
        Args:
            task_definition: Task definition to run
            cluster: Cluster to run the task in
            count: Number of tasks to run
            launch_type: Launch type (EC2, FARGATE)
            capacity_provider_strategy: Capacity provider strategy
            network_configuration: Network configuration for Fargate
            overrides: Container overrides
            tags: Resource tags
            
        Returns:
            Task run response
            
        Raises:
            AWSResourceError: If there's an error running the task
        """
        try:
            logger.info("Running ECS task: %s", task_definition)
            
            kwargs = {
                'taskDefinition': task_definition,
                'count': count
            }
            
            if cluster:
                kwargs['cluster'] = cluster
            if launch_type:
                kwargs['launchType'] = launch_type
            if capacity_provider_strategy:
                kwargs['capacityProviderStrategy'] = capacity_provider_strategy
            if network_configuration:
                kwargs['networkConfiguration'] = network_configuration
            if overrides:
                kwargs['overrides'] = overrides
            if tags:
                kwargs['tags'] = tags
            
            response = self.ecs_client.run_task(**kwargs)
            
            logger.info("Started ECS task: %s", task_definition)
            return response
            
        except ClientError as e:
            error_message = f"Failed to run ECS task {task_definition}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def stop_task(self, task_arn: str, cluster: Optional[str] = None,
                 reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a running ECS task.
        
        Args:
            task_arn: ARN of the task to stop
            cluster: Cluster the task is running in
            reason: Reason for stopping the task
            
        Returns:
            Task configuration
            
        Raises:
            ResourceNotFoundError: If the task doesn't exist
            AWSResourceError: If there's an error stopping the task
        """
        try:
            logger.info("Stopping ECS task: %s", task_arn)
            
            kwargs = {'task': task_arn}
            
            if cluster:
                kwargs['cluster'] = cluster
            if reason:
                kwargs['reason'] = reason
            
            response = self.ecs_client.stop_task(**kwargs)
            
            logger.info("Stopped ECS task: %s", task_arn)
            return response.get('task', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'TaskNotFoundException':
                error_message = f"ECS task not found: {task_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to stop ECS task {task_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
