"""
AWS Client Manager for handling Boto3 clients and sessions.
"""

import boto3
from botocore.exceptions import ClientError, BotoCoreError, ProfileNotFound
from typing import Optional, Dict, Any
import logging

from .exceptions import AWSConnectionException, AWSPermissionException

logger = logging.getLogger(__name__)


class AWSClientManager:
    """
    Manages AWS clients and sessions using Boto3.
    Handles profile management and client creation for different AWS services.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: Optional[str] = None):
        """
        Initialize the AWS Client Manager.
        
        Args:
            profile_name (str): AWS profile name from credentials file. Defaults to 'default'.
            region_name (str, optional): AWS region name. If None, uses profile's default region.
        
        Raises:
            AWSConnectionException: If the profile is not found or session creation fails.
        """
        self.profile_name = profile_name
        self.region_name = region_name
        self._session = None
        self._clients: Dict[str, Any] = {}
        
        try:
            self._initialize_session()
        except (ProfileNotFound, BotoCoreError) as e:
            raise AWSConnectionException(f"Failed to initialize AWS session: {str(e)}")
    
    def _initialize_session(self) -> None:
        """Initialize the AWS session with the specified profile."""
        try:
            self._session = boto3.Session(
                profile_name=self.profile_name,
                region_name=self.region_name
            )
            # Test the session by getting caller identity
            sts_client = self._session.client('sts')
            identity = sts_client.get_caller_identity()
            logger.info(f"Successfully connected to AWS. Account: {identity.get('Account')}, "
                       f"User: {identity.get('Arn')}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('STS', 'get_caller_identity', str(e))
            raise AWSConnectionException(f"Failed to connect to AWS: {str(e)}")
    
    def get_client(self, service_name: str, region_name: Optional[str] = None) -> Any:
        """
        Get or create a Boto3 client for the specified service.
        
        Args:
            service_name (str): AWS service name (e.g., 's3', 'ec2', 'lambda').
            region_name (str, optional): Override region for this client.
        
        Returns:
            boto3.client: The AWS service client.
        
        Raises:
            AWSConnectionException: If client creation fails.
        """
        region = region_name or self.region_name
        client_key = f"{service_name}_{region}"
        
        if client_key not in self._clients:
            try:
                self._clients[client_key] = self._session.client(
                    service_name,
                    region_name=region
                )
                logger.debug(f"Created {service_name} client for region {region}")
            except (ClientError, BotoCoreError) as e:
                raise AWSConnectionException(f"Failed to create {service_name} client: {str(e)}")
        
        return self._clients[client_key]
    
    def get_resource(self, service_name: str, region_name: Optional[str] = None) -> Any:
        """
        Get a Boto3 resource for the specified service.
        
        Args:
            service_name (str): AWS service name (e.g., 's3', 'dynamodb').
            region_name (str, optional): Override region for this resource.
        
        Returns:
            boto3.resource: The AWS service resource.
        
        Raises:
            AWSConnectionException: If resource creation fails.
        """
        region = region_name or self.region_name
        
        try:
            return self._session.resource(
                service_name,
                region_name=region
            )
        except (ClientError, BotoCoreError) as e:
            raise AWSConnectionException(f"Failed to create {service_name} resource: {str(e)}")
    
    def list_profiles(self) -> list:
        """
        List available AWS profiles from the credentials file.
        
        Returns:
            list: List of available profile names.
        """
        try:
            return boto3.Session().available_profiles
        except Exception as e:
            logger.warning(f"Could not list profiles: {str(e)}")
            return []
    
    def get_current_region(self) -> Optional[str]:
        """
        Get the current region being used by the session.
        
        Returns:
            str: The current AWS region name.
        """
        return self._session.region_name if self._session else None
    
    def get_account_id(self) -> Optional[str]:
        """
        Get the current AWS account ID.
        
        Returns:
            str: The AWS account ID.
        
        Raises:
            AWSConnectionException: If unable to get account information.
        """
        try:
            sts_client = self.get_client('sts')
            identity = sts_client.get_caller_identity()
            return identity.get('Account')
        except ClientError as e:
            raise AWSConnectionException(f"Failed to get account ID: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the AWS connection and return connection information.
        
        Returns:
            dict: Connection information including account ID, user ARN, and region.
        
        Raises:
            AWSConnectionException: If connection test fails.
        """
        try:
            sts_client = self.get_client('sts')
            identity = sts_client.get_caller_identity()
            
            return {
                'account_id': identity.get('Account'),
                'user_arn': identity.get('Arn'),
                'user_id': identity.get('UserId'),
                'region': self.get_current_region(),
                'profile': self.profile_name
            }
        except ClientError as e:
            raise AWSConnectionException(f"Connection test failed: {str(e)}")
