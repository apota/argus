"""
S3 Read operations module.
"""

from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
import logging

from ..common.aws_client import AWSClientManager
from ..common.exceptions import AWSResourceException, AWSPermissionException

logger = logging.getLogger(__name__)


class S3Reader:
    """
    Class for reading S3 resources and metadata.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize S3 Reader.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.s3_client = client_manager.get_client('s3')
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all S3 buckets in the account.
        
        Returns:
            List[Dict]: List of bucket information dictionaries.
        
        Raises:
            AWSResourceException: If listing buckets fails.
        """
        try:
            response = self.s3_client.list_buckets()
            buckets = []
            
            for bucket in response.get('Buckets', []):
                bucket_info = {
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'],
                    'region': self._get_bucket_region(bucket['Name'])
                }
                buckets.append(bucket_info)
            
            logger.info(f"Found {len(buckets)} S3 buckets")
            return buckets
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'list_buckets', str(e))
            raise AWSResourceException('S3', 'list_buckets', str(e))
    
    def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific bucket.
        
        Args:
            bucket_name (str): Name of the S3 bucket.
        
        Returns:
            Dict: Bucket information including versioning, encryption, etc.
        
        Raises:
            AWSResourceException: If getting bucket info fails.
        """
        try:
            bucket_info = {
                'name': bucket_name,
                'region': self._get_bucket_region(bucket_name),
                'versioning': self._get_bucket_versioning(bucket_name),
                'encryption': self._get_bucket_encryption(bucket_name),
                'public_access_block': self._get_public_access_block(bucket_name),
                'object_count': self._get_object_count(bucket_name),
                'size': self._get_bucket_size(bucket_name)
            }
            
            return bucket_info
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'get_bucket_info', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'get_bucket_info', str(e))
            raise AWSResourceException('S3', 'get_bucket_info', str(e))
    
    def list_objects(self, bucket_name: str, prefix: str = '', max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List objects in an S3 bucket.
        
        Args:
            bucket_name (str): Name of the S3 bucket.
            prefix (str): Prefix to filter objects.
            max_keys (int): Maximum number of objects to return.
        
        Returns:
            List[Dict]: List of object information dictionaries.
        
        Raises:
            AWSResourceException: If listing objects fails.
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=bucket_name,
                Prefix=prefix,
                PaginationConfig={'MaxItems': max_keys}
            )
            
            objects = []
            for page in page_iterator:
                for obj in page.get('Contents', []):
                    object_info = {
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag'].strip('"'),
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    }
                    objects.append(object_info)
            
            logger.info(f"Found {len(objects)} objects in bucket '{bucket_name}' with prefix '{prefix}'")
            return objects
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'list_objects', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'list_objects', str(e))
            raise AWSResourceException('S3', 'list_objects', str(e))
    
    def get_object_metadata(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """
        Get metadata for a specific S3 object.
        
        Args:
            bucket_name (str): Name of the S3 bucket.
            object_key (str): Key of the S3 object.
        
        Returns:
            Dict: Object metadata.
        
        Raises:
            AWSResourceException: If getting object metadata fails.
        """
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            
            metadata = {
                'key': object_key,
                'size': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
                'content_type': response.get('ContentType'),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'metadata': response.get('Metadata', {}),
                'tags': self._get_object_tags(bucket_name, object_key)
            }
            
            return metadata
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise AWSResourceException('S3', 'get_object_metadata', f"Object '{object_key}' does not exist in bucket '{bucket_name}'")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'get_object_metadata', str(e))
            raise AWSResourceException('S3', 'get_object_metadata', str(e))
    
    def _get_bucket_region(self, bucket_name: str) -> Optional[str]:
        """Get the region of a bucket."""
        try:
            response = self.s3_client.get_bucket_location(Bucket=bucket_name)
            location = response.get('LocationConstraint')
            return location if location else 'us-east-1'
        except ClientError:
            return None
    
    def _get_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket versioning configuration."""
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            return {
                'status': response.get('Status', 'Disabled'),
                'mfa_delete': response.get('MfaDelete', 'Disabled')
            }
        except ClientError:
            return {'status': 'Disabled', 'mfa_delete': 'Disabled'}
    
    def _get_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket encryption configuration."""
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
            rules = response.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
            if rules:
                rule = rules[0]
                return {
                    'enabled': True,
                    'sse_algorithm': rule.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm'),
                    'kms_master_key_id': rule.get('ApplyServerSideEncryptionByDefault', {}).get('KMSMasterKeyID')
                }
            return {'enabled': False}
        except ClientError:
            return {'enabled': False}
    
    def _get_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket public access block configuration."""
        try:
            response = self.s3_client.get_public_access_block(Bucket=bucket_name)
            config = response.get('PublicAccessBlockConfiguration', {})
            return {
                'block_public_acls': config.get('BlockPublicAcls', False),
                'ignore_public_acls': config.get('IgnorePublicAcls', False),
                'block_public_policy': config.get('BlockPublicPolicy', False),
                'restrict_public_buckets': config.get('RestrictPublicBuckets', False)
            }
        except ClientError:
            return {
                'block_public_acls': False,
                'ignore_public_acls': False,
                'block_public_policy': False,
                'restrict_public_buckets': False
            }
    
    def _get_object_count(self, bucket_name: str) -> int:
        """Get approximate object count in bucket."""
        try:
            cloudwatch = self.client_manager.get_client('cloudwatch')
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='NumberOfObjects',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                ],
                StartTime='2023-01-01',
                EndTime='2024-01-01',
                Period=86400,
                Statistics=['Average']
            )
            if response.get('Datapoints'):
                return int(response['Datapoints'][-1]['Average'])
            return 0
        except ClientError:
            return 0
    
    def _get_bucket_size(self, bucket_name: str) -> int:
        """Get approximate bucket size in bytes."""
        try:
            cloudwatch = self.client_manager.get_client('cloudwatch')
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime='2023-01-01',
                EndTime='2024-01-01',
                Period=86400,
                Statistics=['Average']
            )
            if response.get('Datapoints'):
                return int(response['Datapoints'][-1]['Average'])
            return 0
        except ClientError:
            return 0
    
    def _get_object_tags(self, bucket_name: str, object_key: str) -> Dict[str, str]:
        """Get tags for an S3 object."""
        try:
            response = self.s3_client.get_object_tagging(Bucket=bucket_name, Key=object_key)
            tags = {}
            for tag in response.get('TagSet', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}
