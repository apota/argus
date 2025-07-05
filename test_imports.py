#!/usr/bin/env python3
"""
Simple test script for Argus AWS Resource Explorer
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing Argus module imports...")
    
    try:
        # Test common modules
        from src.common.aws_client import AWSClientManager
        from src.common.exceptions import AWSResourceError, ResourceNotFoundError
        print("✅ Common modules imported successfully")
        
        # Test S3 modules
        from src.s3.read.s3_reader import S3Reader
        from src.s3.write.s3_writer import S3Writer
        print("✅ S3 modules imported successfully")
        
        # Test Lambda modules
        from src.awslambda.read.lambda_reader import LambdaReader
        from src.awslambda.write.lambda_writer import LambdaWriter
        print("✅ Lambda modules imported successfully")
        
        # Test ECS modules
        from src.ecs.read.ecs_reader import ECSReader
        from src.ecs.write.ecs_writer import ECSWriter
        print("✅ ECS modules imported successfully")
        
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
        from src.common.aws_client import AWSClientManager
        
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
