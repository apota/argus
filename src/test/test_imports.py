#!/usr/bin/env python3
"""
Simple test script for Argus AWS Resource Explorer
"""

import sys
import os

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing Argus module imports...")
    
    try:
        # Test common modules
        from common.aws_client import AWSClientManager
        from common.exceptions import AWSResourceError, ResourceNotFoundError
        print("✅ Common modules imported successfully")
        
        # Test S3 modules
        from s3.read.s3_reader import S3Reader
        from s3.write.s3_writer import S3Writer
        print("✅ S3 modules imported successfully")
        
        # Test Lambda modules
        from awslambda.read.lambda_reader import LambdaReader
        from awslambda.write.lambda_writer import LambdaWriter
        print("✅ Lambda modules imported successfully")
        
        # Test ECS modules
        from ecs.read.ecs_reader import ECSReader
        from ecs.write.ecs_writer import ECSWriter
        print("✅ ECS modules imported successfully")
        
        # Test EC2 modules
        from ec2.read.ec2_reader import EC2Reader
        from ec2.write.ec2_writer import EC2Writer
        print("✅ EC2 modules imported successfully")
        
        # Test Step Functions modules
        from stepfunction.read.sf_reader import StepFunctionReader
        from stepfunction.write.sf_writer import StepFunctionWriter
        print("✅ Step Functions modules imported successfully")
        
        # Test DynamoDB modules
        from dynamodb.read.dynamodb_reader import DynamoDBReader
        from dynamodb.write.dynamodb_writer import DynamoDBWriter
        print("✅ DynamoDB modules imported successfully")
        
        # Test EventBridge modules
        from eventbridge.read.eb_reader import EventBridgeReader
        from eventbridge.write.eb_writer import EventBridgeWriter
        print("✅ EventBridge modules imported successfully")
        
        # Test Parameter Store modules
        from parameterstore.read.ps_reader import ParameterStoreReader
        from parameterstore.write.ps_writer import ParameterStoreWriter
        print("✅ Parameter Store modules imported successfully")
        
        # Test SQS modules
        from sqs.read.sqs_reader import SQSReader
        from sqs.write.sqs_writer import SQSWriter
        print("✅ SQS modules imported successfully")
        
        # Test EBS modules
        from ebs.read.ebs_reader import EBSReader
        from ebs.write.ebs_writer import EBSWriter
        print("✅ EBS modules imported successfully")
        
        # Test EKS modules
        from eks.read.eks_reader import EKSReader
        from eks.write.eks_writer import EKSWriter
        print("✅ EKS modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with mock/dry run."""
    print("\nTesting basic functionality...")
    
    try:
        from common.aws_client import AWSClientManager
        
        # Test AWS client manager initialization
        client_manager = AWSClientManager('default', 'us-east-1')
        print("✅ AWSClientManager initialized successfully")
        
        # Test that we can create a client (this won't make API calls)
        s3_client = client_manager.get_client('s3')
        print("✅ S3 client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Argus Library Test Suite")
    print("=" * 40)
    
    # Test imports
    import_success = test_imports()
    
    # Test basic functionality
    functionality_success = test_basic_functionality()
    
    # Summary
    print("\n📊 Test Results:")
    print(f"  Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"  Basic Functionality: {'✅ PASS' if functionality_success else '❌ FAIL'}")
    
    if import_success and functionality_success:
        print("\n🎉 All tests passed! The Argus library is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
