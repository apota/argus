"""
S3 Write operations module.
"""

from typing import Dict, Any, Optional, BinaryIO
from botocore.exceptions import ClientError
import logging
import json
from datetime import datetime, timezone

from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceException, AWSPermissionException

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
    
    def touch_object(self, bucket_name: str, object_key: str, 
                    preserve_metadata: bool = True, custom_metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Touch an S3 object to update its timestamp by copying it with new metadata.
        
        This operation updates the LastModified timestamp of an S3 object by performing
        a copy operation on itself with updated metadata. This is useful for cache
        invalidation, triggering events, or updating object timestamps.
        
        Args:
            bucket_name (str): Name of the bucket containing the object.
            object_key (str): Key of the object to touch.
            preserve_metadata (bool): Whether to preserve existing metadata. Default is True.
            custom_metadata (Dict, optional): Additional metadata to add/update.
        
        Returns:
            Dict: Result of touch operation including new timestamp and metadata.
        
        Raises:
            AWSResourceException: If the touch operation fails.
        """
        try:
            from datetime import datetime, timezone
            
            # First, get the current object metadata and properties
            head_response = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            
            # Prepare copy arguments
            copy_args = {
                'Bucket': bucket_name,
                'Key': object_key,
                'CopySource': {'Bucket': bucket_name, 'Key': object_key},
                'MetadataDirective': 'REPLACE'
            }
            
            # Handle metadata
            metadata = {}
            if preserve_metadata and 'Metadata' in head_response:
                metadata.update(head_response['Metadata'])
            
            # Add custom metadata if provided
            if custom_metadata:
                metadata.update(custom_metadata)
            
            # Add/update touch timestamp
            metadata['touched-at'] = datetime.now(timezone.utc).isoformat()
            
            copy_args['Metadata'] = metadata
            
            # Preserve content type if it exists
            if 'ContentType' in head_response:
                copy_args['ContentType'] = head_response['ContentType']
            
            # Preserve content encoding if it exists
            if 'ContentEncoding' in head_response:
                copy_args['ContentEncoding'] = head_response['ContentEncoding']
            
            # Preserve cache control if it exists
            if 'CacheControl' in head_response:
                copy_args['CacheControl'] = head_response['CacheControl']
            
            # Perform the copy operation (which updates the timestamp)
            copy_response = self.s3_client.copy_object(**copy_args)
            
            # Get updated object info
            updated_head = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            
            logger.info(f"Successfully touched object '{object_key}' in bucket '{bucket_name}'")
            
            return {
                'bucket_name': bucket_name,
                'object_key': object_key,
                'previous_last_modified': head_response.get('LastModified'),
                'new_last_modified': updated_head.get('LastModified'),
                'etag': copy_response.get('CopyObjectResult', {}).get('ETag', '').strip('"'),
                'version_id': copy_response.get('VersionId'),
                'metadata': metadata,
                'touched_at': metadata.get('touched-at'),
                'operation': 'touch_successful'
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                raise AWSResourceException('S3', 'touch_object', f"Bucket '{bucket_name}' does not exist")
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise AWSResourceException('S3', 'touch_object', f"Object '{object_key}' does not exist in bucket '{bucket_name}'")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AWSPermissionException('S3', 'touch_object', str(e))
            raise AWSResourceException('S3', 'touch_object', str(e))
    
    def batch_touch_objects(self, bucket_name: str, object_keys: list, 
                           preserve_metadata: bool = True, custom_metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Touch multiple S3 objects to update their timestamps.
        
        Args:
            bucket_name (str): Name of the bucket containing the objects.
            object_keys (list): List of object keys to touch.
            preserve_metadata (bool): Whether to preserve existing metadata. Default is True.
            custom_metadata (Dict, optional): Additional metadata to add/update for all objects.
        
        Returns:
            Dict: Results of batch touch operation with success/failure counts.
        
        Raises:
            AWSResourceException: If the batch operation fails completely.
        """
        try:
            results = {
                'bucket_name': bucket_name,
                'total_objects': len(object_keys),
                'successful_touches': 0,
                'failed_touches': 0,
                'touched_objects': [],
                'failed_objects': []
            }
            
            for object_key in object_keys:
                try:
                    touch_result = self.touch_object(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        preserve_metadata=preserve_metadata,
                        custom_metadata=custom_metadata
                    )
                    results['successful_touches'] += 1
                    results['touched_objects'].append({
                        'object_key': object_key,
                        'new_last_modified': touch_result['new_last_modified'],
                        'touched_at': touch_result['touched_at']
                    })
                    
                except Exception as e:
                    results['failed_touches'] += 1
                    results['failed_objects'].append({
                        'object_key': object_key,
                        'error': str(e)
                    })
                    logger.error(f"Failed to touch object '{object_key}': {str(e)}")
            
            logger.info(f"Batch touch completed: {results['successful_touches']}/{results['total_objects']} objects touched successfully")
            return results
            
        except Exception as e:
            raise AWSResourceException('S3', 'batch_touch_objects', f"Batch touch operation failed: {str(e)}")

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
