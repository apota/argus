"""
S3 Write operations module.
"""

from typing import Dict, Any, Optional, BinaryIO
from botocore.exceptions import ClientError
import logging
import json

from ..common.aws_client import AWSClientManager
from ..common.exceptions import AWSResourceException, AWSPermissionException

logger = logging.getLogger(__name__)


class S3Writer:
    """
    Class for writing and modifying S3 resources.
    """
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize S3 Writer.
        
        Args:
            client_manager (AWSClientManager): AWS client manager instance.
        """
        self.client_manager = client_manager
        self.s3_client = client_manager.get_client('s3')
    
    def create_bucket(self, bucket_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new S3 bucket.
        
        Args:
            bucket_name (str): Name of the bucket to create.
            region (str, optional): Region to create the bucket in.
        
        Returns:
            Dict: Result of bucket creation.
        
        Raises:
            AWSResourceException: If bucket creation fails.
        """
        try:
            create_config = {}
            if region and region != 'us-east-1':
                create_config['CreateBucketConfiguration'] = {'LocationConstraint': region}
            
            response = self.s3_client.create_bucket(
                Bucket=bucket_name,
                **create_config
            )
            
            logger.info(f"Successfully created bucket '{bucket_name}' in region '{region or 'us-east-1'}'")
            return {
                'bucket_name': bucket_name,
                'location': response.get('Location'),
                'region': region or 'us-east-1'
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                raise AWSResourceException('S3', 'create_bucket', f"Bucket '{bucket_name}' already exists")
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                raise AWSResourceException('S3', 'create_bucket', f"Bucket '{bucket_name}' already owned by you")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'create_bucket', str(e))
            raise AWSResourceException('S3', 'create_bucket', str(e))
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete an S3 bucket.
        
        Args:
            bucket_name (str): Name of the bucket to delete.
            force (bool): If True, delete all objects in bucket first.
        
        Returns:
            Dict: Result of bucket deletion.
        
        Raises:
            AWSResourceException: If bucket deletion fails.
        """
        try:
            if force:
                self._empty_bucket(bucket_name)
            
            self.s3_client.delete_bucket(Bucket=bucket_name)
            
            logger.info(f"Successfully deleted bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'status': 'deleted'
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'delete_bucket', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'BucketNotEmpty':
                raise AWSResourceException('S3', 'delete_bucket', f"Bucket '{bucket_name}' is not empty. Use force=True to delete all objects first")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'delete_bucket', str(e))
            raise AWSResourceException('S3', 'delete_bucket', str(e))
    
    def upload_object(self, bucket_name: str, object_key: str, content: Any, 
                     content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None,
                     tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload an object to S3.
        
        Args:
            bucket_name (str): Name of the bucket.
            object_key (str): Key for the object.
            content: Content to upload (string, bytes, or file-like object).
            content_type (str, optional): MIME type of the content.
            metadata (Dict, optional): Custom metadata for the object.
            tags (Dict, optional): Tags to apply to the object.
        
        Returns:
            Dict: Result of object upload.
        
        Raises:
            AWSResourceException: If object upload fails.
        """
        try:
            put_args = {
                'Bucket': bucket_name,
                'Key': object_key,
                'Body': content
            }
            
            if content_type:
                put_args['ContentType'] = content_type
            
            if metadata:
                put_args['Metadata'] = metadata
            
            if tags:
                tag_string = '&'.join([f"{k}={v}" for k, v in tags.items()])
                put_args['Tagging'] = tag_string
            
            response = self.s3_client.put_object(**put_args)
            
            logger.info(f"Successfully uploaded object '{object_key}' to bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'object_key': object_key,
                'etag': response.get('ETag', '').strip('"'),
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'upload_object', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'upload_object', str(e))
            raise AWSResourceException('S3', 'upload_object', str(e))
    
    def delete_object(self, bucket_name: str, object_key: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an object from S3.
        
        Args:
            bucket_name (str): Name of the bucket.
            object_key (str): Key of the object to delete.
            version_id (str, optional): Version ID for versioned buckets.
        
        Returns:
            Dict: Result of object deletion.
        
        Raises:
            AWSResourceException: If object deletion fails.
        """
        try:
            delete_args = {
                'Bucket': bucket_name,
                'Key': object_key
            }
            
            if version_id:
                delete_args['VersionId'] = version_id
            
            response = self.s3_client.delete_object(**delete_args)
            
            logger.info(f"Successfully deleted object '{object_key}' from bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'object_key': object_key,
                'version_id': response.get('VersionId'),
                'delete_marker': response.get('DeleteMarker', False)
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'delete_object', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'delete_object', str(e))
            raise AWSResourceException('S3', 'delete_object', str(e))
    
    def set_bucket_policy(self, bucket_name: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set bucket policy for an S3 bucket.
        
        Args:
            bucket_name (str): Name of the bucket.
            policy (Dict): Bucket policy as a dictionary.
        
        Returns:
            Dict: Result of policy setting.
        
        Raises:
            AWSResourceException: If setting bucket policy fails.
        """
        try:
            policy_json = json.dumps(policy)
            
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=policy_json
            )
            
            logger.info(f"Successfully set bucket policy for bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'policy_set': True
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'set_bucket_policy', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'set_bucket_policy', str(e))
            raise AWSResourceException('S3', 'set_bucket_policy', str(e))
    
    def enable_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """
        Enable versioning for an S3 bucket.
        
        Args:
            bucket_name (str): Name of the bucket.
        
        Returns:
            Dict: Result of versioning enablement.
        
        Raises:
            AWSResourceException: If enabling versioning fails.
        """
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            logger.info(f"Successfully enabled versioning for bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'versioning_enabled': True
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'enable_bucket_versioning', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'enable_bucket_versioning', str(e))
            raise AWSResourceException('S3', 'enable_bucket_versioning', str(e))
    
    def set_bucket_encryption(self, bucket_name: str, kms_key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Set server-side encryption for an S3 bucket.
        
        Args:
            bucket_name (str): Name of the bucket.
            kms_key_id (str, optional): KMS key ID for encryption. If None, uses AES256.
        
        Returns:
            Dict: Result of encryption setting.
        
        Raises:
            AWSResourceException: If setting encryption fails.
        """
        try:
            if kms_key_id:
                encryption_config = {
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'aws:kms',
                                'KMSMasterKeyID': kms_key_id
                            }
                        }
                    ]
                }
            else:
                encryption_config = {
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration=encryption_config
            )
            
            algorithm = 'aws:kms' if kms_key_id else 'AES256'
            logger.info(f"Successfully set {algorithm} encryption for bucket '{bucket_name}'")
            return {
                'bucket_name': bucket_name,
                'encryption_enabled': True,
                'algorithm': algorithm,
                'kms_key_id': kms_key_id
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'set_bucket_encryption', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'set_bucket_encryption', str(e))
            raise AWSResourceException('S3', 'set_bucket_encryption', str(e))
    
    def _empty_bucket(self, bucket_name: str) -> None:
        """Delete all objects in a bucket."""
        try:
            # List and delete all object versions
            paginator = self.s3_client.get_paginator('list_object_versions')
            for page in paginator.paginate(Bucket=bucket_name):
                objects_to_delete = []
                
                # Add versions
                for version in page.get('Versions', []):
                    objects_to_delete.append({
                        'Key': version['Key'],
                        'VersionId': version['VersionId']
                    })
                
                # Add delete markers
                for marker in page.get('DeleteMarkers', []):
                    objects_to_delete.append({
                        'Key': marker['Key'],
                        'VersionId': marker['VersionId']
                    })
                
                # Delete objects in batches
                if objects_to_delete:
                    self.s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
            
        except ClientError as e:
            # If versioning is not enabled, try regular delete
            if e.response['Error']['Code'] == 'NoSuchKey':
                paginator = self.s3_client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name):
                    objects_to_delete = [{'Key': obj['Key']} for obj in page.get('Contents', [])]
                    
                    if objects_to_delete:
                        self.s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': objects_to_delete}
                        )
