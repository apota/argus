"""
ECS Reader Module

This module provides functionality for reading and exploring AWS ECS resources.
"""

import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class ECSReader:
    """
    A class for reading AWS ECS resources.
    
    This class provides methods to list and retrieve information about
    ECS clusters, services, tasks, task definitions, and container instances.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the ECS reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.ecs_client = self.client_manager.get_client('ecs')
    
    def list_clusters(self, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all ECS clusters in the account.
        
        Args:
            max_results: Maximum number of clusters to return
            
        Returns:
            List of cluster ARNs and details
            
        Raises:
            AWSResourceError: If there's an error listing clusters
        """
        try:
            logger.info("Listing ECS clusters")
            
            kwargs = {}
            if max_results:
                kwargs['maxResults'] = max_results
            
            response = self.ecs_client.list_clusters(**kwargs)
            cluster_arns = response.get('clusterArns', [])
            
            if cluster_arns:
                # Get detailed information about clusters
                cluster_details = self.ecs_client.describe_clusters(clusters=cluster_arns)
                clusters = cluster_details.get('clusters', [])
            else:
                clusters = []
            
            logger.info("Found %d ECS clusters", len(clusters))
            return clusters
            
        except ClientError as e:
            error_message = f"Failed to list ECS clusters: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ECS cluster.
        
        Args:
            cluster_name: Name or ARN of the ECS cluster
            
        Returns:
            Cluster configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the cluster doesn't exist
            AWSResourceError: If there's an error retrieving the cluster
        """
        try:
            logger.info("Describing ECS cluster: %s", cluster_name)
            
            response = self.ecs_client.describe_clusters(clusters=[cluster_name])
            clusters = response.get('clusters', [])
            
            if not clusters:
                error_message = f"ECS cluster not found: {cluster_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message)
            
            cluster = clusters[0]
            logger.info("Retrieved cluster information for %s", cluster_name)
            return cluster
            
        except ClientError as e:
            error_message = f"Failed to describe ECS cluster {cluster_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_services(self, cluster_name: Optional[str] = None, 
                     max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List ECS services in a cluster.
        
        Args:
            cluster_name: Name of the cluster (uses default if not specified)
            max_results: Maximum number of services to return
            
        Returns:
            List of service configurations
            
        Raises:
            AWSResourceError: If there's an error listing services
        """
        try:
            logger.info("Listing ECS services in cluster: %s", cluster_name or 'default')
            
            kwargs = {}
            if cluster_name:
                kwargs['cluster'] = cluster_name
            if max_results:
                kwargs['maxResults'] = max_results
            
            response = self.ecs_client.list_services(**kwargs)
            service_arns = response.get('serviceArns', [])
            
            if service_arns:
                # Get detailed information about services
                describe_kwargs = {'services': service_arns}
                if cluster_name:
                    describe_kwargs['cluster'] = cluster_name
                
                service_details = self.ecs_client.describe_services(**describe_kwargs)
                services = service_details.get('services', [])
            else:
                services = []
            
            logger.info("Found %d ECS services", len(services))
            return services
            
        except ClientError as e:
            error_message = f"Failed to list ECS services: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_service(self, service_name: str, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific ECS service.
        
        Args:
            service_name: Name or ARN of the ECS service
            cluster_name: Name of the cluster (uses default if not specified)
            
        Returns:
            Service configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the service doesn't exist
            AWSResourceError: If there's an error retrieving the service
        """
        try:
            logger.info("Describing ECS service: %s", service_name)
            
            kwargs = {'services': [service_name]}
            if cluster_name:
                kwargs['cluster'] = cluster_name
            
            response = self.ecs_client.describe_services(**kwargs)
            services = response.get('services', [])
            
            if not services:
                error_message = f"ECS service not found: {service_name}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message)
            
            service = services[0]
            logger.info("Retrieved service information for %s", service_name)
            return service
            
        except ClientError as e:
            error_message = f"Failed to describe ECS service {service_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_tasks(self, cluster_name: Optional[str] = None, 
                  service_name: Optional[str] = None,
                  desired_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List ECS tasks in a cluster.
        
        Args:
            cluster_name: Name of the cluster (uses default if not specified)
            service_name: Optional service name to filter tasks
            desired_status: Optional desired status (RUNNING, PENDING, STOPPED)
            
        Returns:
            List of task configurations
            
        Raises:
            AWSResourceError: If there's an error listing tasks
        """
        try:
            logger.info("Listing ECS tasks in cluster: %s", cluster_name or 'default')
            
            kwargs = {}
            if cluster_name:
                kwargs['cluster'] = cluster_name
            if service_name:
                kwargs['serviceName'] = service_name
            if desired_status:
                kwargs['desiredStatus'] = desired_status
            
            response = self.ecs_client.list_tasks(**kwargs)
            task_arns = response.get('taskArns', [])
            
            if task_arns:
                # Get detailed information about tasks
                describe_kwargs = {'tasks': task_arns}
                if cluster_name:
                    describe_kwargs['cluster'] = cluster_name
                
                task_details = self.ecs_client.describe_tasks(**describe_kwargs)
                tasks = task_details.get('tasks', [])
            else:
                tasks = []
            
            logger.info("Found %d ECS tasks", len(tasks))
            return tasks
            
        except ClientError as e:
            error_message = f"Failed to list ECS tasks: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_task(self, task_arn: str, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific ECS task.
        
        Args:
            task_arn: ARN of the ECS task
            cluster_name: Name of the cluster (uses default if not specified)
            
        Returns:
            Task configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the task doesn't exist
            AWSResourceError: If there's an error retrieving the task
        """
        try:
            logger.info("Describing ECS task: %s", task_arn)
            
            kwargs = {'tasks': [task_arn]}
            if cluster_name:
                kwargs['cluster'] = cluster_name
            
            response = self.ecs_client.describe_tasks(**kwargs)
            tasks = response.get('tasks', [])
            
            if not tasks:
                error_message = f"ECS task not found: {task_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message)
            
            task = tasks[0]
            logger.info("Retrieved task information for %s", task_arn)
            return task
            
        except ClientError as e:
            error_message = f"Failed to describe ECS task {task_arn}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_task_definitions(self, family_prefix: Optional[str] = None,
                             status: str = 'ACTIVE') -> List[str]:
        """
        List ECS task definitions.
        
        Args:
            family_prefix: Optional family prefix to filter task definitions
            status: Status of task definitions to list (ACTIVE, INACTIVE, ALL)
            
        Returns:
            List of task definition ARNs
            
        Raises:
            AWSResourceError: If there's an error listing task definitions
        """
        try:
            logger.info("Listing ECS task definitions")
            
            kwargs = {'status': status}
            if family_prefix:
                kwargs['familyPrefix'] = family_prefix
            
            paginator = self.ecs_client.get_paginator('list_task_definitions')
            page_iterator = paginator.paginate(**kwargs)
            
            task_definitions = []
            for page in page_iterator:
                task_definitions.extend(page.get('taskDefinitionArns', []))
            
            logger.info("Found %d ECS task definitions", len(task_definitions))
            return task_definitions
            
        except ClientError as e:
            error_message = f"Failed to list ECS task definitions: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_task_definition(self, task_definition: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ECS task definition.
        
        Args:
            task_definition: Family and revision (family:revision) or full ARN
            
        Returns:
            Task definition configuration
            
        Raises:
            ResourceNotFoundError: If the task definition doesn't exist
            AWSResourceError: If there's an error retrieving the task definition
        """
        try:
            logger.info("Describing ECS task definition: %s", task_definition)
            
            response = self.ecs_client.describe_task_definition(taskDefinition=task_definition)
            
            logger.info("Retrieved task definition information for %s", task_definition)
            return response.get('taskDefinition', {})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ClientException':
                error_message = f"ECS task definition not found: {task_definition}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe ECS task definition {task_definition}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_container_instances(self, cluster_name: Optional[str] = None,
                                status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List ECS container instances in a cluster.
        
        Args:
            cluster_name: Name of the cluster (uses default if not specified)
            status: Optional status filter (ACTIVE, DRAINING, REGISTERING, etc.)
            
        Returns:
            List of container instance configurations
            
        Raises:
            AWSResourceError: If there's an error listing container instances
        """
        try:
            logger.info("Listing ECS container instances in cluster: %s", cluster_name or 'default')
            
            kwargs = {}
            if cluster_name:
                kwargs['cluster'] = cluster_name
            if status:
                kwargs['status'] = status
            
            response = self.ecs_client.list_container_instances(**kwargs)
            instance_arns = response.get('containerInstanceArns', [])
            
            if instance_arns:
                # Get detailed information about container instances
                describe_kwargs = {'containerInstances': instance_arns}
                if cluster_name:
                    describe_kwargs['cluster'] = cluster_name
                
                instance_details = self.ecs_client.describe_container_instances(**describe_kwargs)
                instances = instance_details.get('containerInstances', [])
            else:
                instances = []
            
            logger.info("Found %d ECS container instances", len(instances))
            return instances
            
        except ClientError as e:
            error_message = f"Failed to list ECS container instances: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def get_service_task_count(self, cluster_name: str, service_name: str) -> int:
        """
        Get the desired task count for a given ECS service.
        
        Args:
            cluster_name: Name of the ECS cluster
            service_name: Name of the ECS service
            
        Returns:
            The desired task count for the service
            
        Raises:
            AWSResourceError: If there's an error retrieving the service
        """
        try:
            response = self.ecs_client.describe_services(
                cluster=cluster_name,
                services=[service_name]
            )
            services = response.get('services', [])
            if not services:
                raise ResourceNotFoundError(f"Service {service_name} not found in cluster {cluster_name}")
            return services[0].get('desiredCount', 0)
        except ClientError as e:
            error_message = f"Failed to get task count for service {service_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e

    def get_running_task_count(self, cluster_name: str, service_name: str) -> int:
        """
        Get the running task count for a given ECS service.
        
        Args:
            cluster_name: Name of the ECS cluster
            service_name: Name of the ECS service
            
        Returns:
            The running task count for the service
            
        Raises:
            AWSResourceError: If there's an error retrieving the service
        """
        try:
            response = self.ecs_client.describe_services(
                cluster=cluster_name,
                services=[service_name]
            )
            services = response.get('services', [])
            if not services:
                raise ResourceNotFoundError(f"Service {service_name} not found in cluster {cluster_name}")
            return services[0].get('runningCount', 0)
        except ClientError as e:
            error_message = f"Failed to get running task count for service {service_name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
