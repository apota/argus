#!/usr/bin/env python3
"""
Quick test script for Argus library
"""

import sys
import os

# Add the parent src directory to the Python path
src_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, src_dir)

def main():
    print("🧪 Testing Argus Library")
    print("=" * 40)
    
    try:
        # Test basic imports
        from common.aws_client import AWSClientManager
        print("✅ AWSClientManager imported")
        
        from s3.read.s3_reader import S3Reader  
        print("✅ S3Reader imported")
        
        from awslambda.read.lambda_reader import LambdaReader
        print("✅ LambdaReader imported")
        
        from ecs.read.ecs_reader import ECSReader
        print("✅ ECSReader imported")
        
        from stepfunction.read.sf_reader import StepFunctionReader
        print("✅ StepFunctionReader imported")
        
        from dynamodb.read.dynamodb_reader import DynamoDBReader
        print("✅ DynamoDBReader imported")
        
        from eventbridge.read.eb_reader import EventBridgeReader
        print("✅ EventBridgeReader imported")
        
        from parameterstore.read.ps_reader import ParameterStoreReader
        print("✅ ParameterStoreReader imported")
        
        from sqs.read.sqs_reader import SQSReader
        print("✅ SQSReader imported")
        
        # Test write modules
        from s3.write.s3_writer import S3Writer
        print("✅ S3Writer imported")
        
        from awslambda.write.lambda_writer import LambdaWriter
        print("✅ LambdaWriter imported")
        
        from ecs.write.ecs_writer import ECSWriter
        print("✅ ECSWriter imported")
        
        from stepfunction.write.sf_writer import StepFunctionWriter
        print("✅ StepFunctionWriter imported")
        
        from dynamodb.write.dynamodb_writer import DynamoDBWriter
        print("✅ DynamoDBWriter imported")
        
        from eventbridge.write.eb_writer import EventBridgeWriter
        print("✅ EventBridgeWriter imported")
        
        from parameterstore.write.ps_writer import ParameterStoreWriter
        print("✅ ParameterStoreWriter imported")
        
        from sqs.write.sqs_writer import SQSWriter
        print("✅ SQSWriter imported")
        
        print("\n🎉 All modules imported successfully!")
        
        # Test basic client creation (no AWS calls)
        try:
            client_manager = AWSClientManager('default', 'us-east-1')
            print("✅ AWSClientManager instance created")
        except Exception as e:
            print(f"ℹ️  AWS connection test failed (expected if no credentials): {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
