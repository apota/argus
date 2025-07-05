#!/usr/bin/env python3
"""
Unit tests for common AWS client functionality
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestAWSClientManager(unittest.TestCase):
    """Test cases for AWSClientManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.profile_name = 'test-profile'
        self.region_name = 'us-east-1'
    
    @patch('common.aws_client.boto3.Session')
    def test_client_manager_initialization(self, mock_session):
        """Test AWSClientManager initialization."""
        # Mock the session and STS client
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        mock_sts_client = Mock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_sts_client.get_caller_identity.return_value = {
            'Account': '123456789012',
            'Arn': 'arn:aws:iam::123456789012:user/test-user'
        }
        
        from common.aws_client import AWSClientManager
        
        # Test initialization
        client_manager = AWSClientManager(self.profile_name, self.region_name)
        
        # Verify session was created with correct parameters
        mock_session.assert_called_once_with(
            profile_name=self.profile_name,
            region_name=self.region_name
        )
        
        # Verify STS client was called to test connection
        mock_session_instance.client.assert_called_with('sts')
        mock_sts_client.get_caller_identity.assert_called_once()
        
        # Verify client manager properties
        self.assertEqual(client_manager.profile_name, self.profile_name)
        self.assertEqual(client_manager.region_name, self.region_name)
    
    @patch('common.aws_client.boto3.Session')
    def test_get_client(self, mock_session):
        """Test get_client method."""
        # Mock the session
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        mock_sts_client = Mock()
        mock_s3_client = Mock()
        
        def client_side_effect(service_name, region_name=None):
            if service_name == 'sts':
                return mock_sts_client
            elif service_name == 's3':
                return mock_s3_client
            return Mock()
        
        mock_session_instance.client.side_effect = client_side_effect
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
        
        from common.aws_client import AWSClientManager
        
        client_manager = AWSClientManager(self.profile_name, self.region_name)
        
        # Test getting S3 client
        s3_client = client_manager.get_client('s3')
        
        # Verify the correct client was returned
        self.assertEqual(s3_client, mock_s3_client)
        
        # Test getting the same client again (should be cached)
        s3_client_2 = client_manager.get_client('s3')
        self.assertEqual(s3_client, s3_client_2)
    
    @patch('common.aws_client.boto3.Session')
    def test_get_resource(self, mock_session):
        """Test get_resource method."""
        # Mock the session
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        mock_sts_client = Mock()
        mock_dynamodb_resource = Mock()
        
        mock_session_instance.client.return_value = mock_sts_client
        mock_session_instance.resource.return_value = mock_dynamodb_resource
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
        
        from common.aws_client import AWSClientManager
        
        client_manager = AWSClientManager(self.profile_name, self.region_name)
        
        # Test getting DynamoDB resource
        dynamodb_resource = client_manager.get_resource('dynamodb')
        
        # Verify the correct resource was returned
        self.assertEqual(dynamodb_resource, mock_dynamodb_resource)
        mock_session_instance.resource.assert_called_with(
            'dynamodb',
            region_name=self.region_name
        )

class TestAWSExceptions(unittest.TestCase):
    """Test cases for custom AWS exceptions."""
    
    def test_aws_resource_error(self):
        """Test AWSResourceError exception."""
        from common.exceptions import AWSResourceError
        
        message = "Test error message"
        error = AWSResourceError(message)
        
        self.assertEqual(str(error), message)
        self.assertEqual(error.message, message)
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError exception."""
        from common.exceptions import ResourceNotFoundError
        
        message = "Resource not found"
        error = ResourceNotFoundError(message)
        
        self.assertEqual(str(error), message)
        self.assertEqual(error.message, message)
        
        # Verify it's a subclass of AWSResourceError
        from common.exceptions import AWSResourceError
        self.assertIsInstance(error, AWSResourceError)

if __name__ == '__main__':
    unittest.main()
