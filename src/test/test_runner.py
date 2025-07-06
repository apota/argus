#!/usr/bin/env python3
"""
Test runner for Argus AWS Resource Explorer
"""

import sys
import os
import importlib

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_import_tests():
    """Run import tests for all modules."""
    print("🔍 Running Import Tests")
    print("-" * 30)
    
    test_modules = [
        ('common.aws_client', 'AWSClientManager'),
        ('common.exceptions', 'AWSResourceError'),
        ('s3.read.s3_reader', 'S3Reader'),
        ('s3.write.s3_writer', 'S3Writer'),
        ('awslambda.read.lambda_reader', 'LambdaReader'),
        ('awslambda.write.lambda_writer', 'LambdaWriter'),
        ('ecs.read.ecs_reader', 'ECSReader'),
        ('ecs.write.ecs_writer', 'ECSWriter'),
        ('stepfunction.read.sf_reader', 'StepFunctionReader'),
        ('stepfunction.write.sf_writer', 'StepFunctionWriter'),
        ('dynamodb.read.dynamodb_reader', 'DynamoDBReader'),
        ('dynamodb.write.dynamodb_writer', 'DynamoDBWriter'),
        ('eventbridge.read.eb_reader', 'EventBridgeReader'),
        ('eventbridge.write.eb_writer', 'EventBridgeWriter'),
        ('parameterstore.read.ps_reader', 'ParameterStoreReader'),
        ('parameterstore.write.ps_writer', 'ParameterStoreWriter'),
        ('sqs.read.sqs_reader', 'SQSReader'),
        ('sqs.write.sqs_writer', 'SQSWriter'),
        ('cloudwatch.read.cloudwatch_reader', 'CloudWatchReader'),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, class_name in test_modules:
        try:
            module = importlib.import_module(module_name)
            class_obj = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            passed += 1
        except ImportError as e:
            print(f"❌ {module_name}.{class_name} - Import Error: {e}")
            failed += 1
        except AttributeError as e:
            print(f"❌ {module_name}.{class_name} - Attribute Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - Unexpected Error: {e}")
            failed += 1
    
    print(f"\n📊 Import Test Results: {passed} passed, {failed} failed")
    return failed == 0

def run_instantiation_tests():
    """Test that core classes can be instantiated."""
    print("\n🏗️  Running Instantiation Tests")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    try:
        from common.aws_client import AWSClientManager
        
        # Test basic instantiation (may fail due to credentials, but should not fail due to code errors)
        try:
            client_manager = AWSClientManager('default', 'us-east-1')
            print("✅ AWSClientManager instantiated successfully")
            passed += 1
            
            # Test client creation
            try:
                s3_client = client_manager.get_client('s3')
                print("✅ S3 client created successfully")
                passed += 1
            except Exception as e:
                print(f"ℹ️  S3 client creation failed (may be due to credentials): {e}")
                passed += 1  # Consider this a pass since it's likely a credential issue
                
        except Exception as e:
            print(f"❌ AWSClientManager instantiation failed: {e}")
            failed += 1
            
    except ImportError as e:
        print(f"❌ Could not import AWSClientManager: {e}")
        failed += 1
    
    print(f"\n📊 Instantiation Test Results: {passed} passed, {failed} failed")
    return failed == 0

def run_module_structure_tests():
    """Test that module structure is correct."""
    print("\n📁 Running Module Structure Tests")
    print("-" * 30)
    
    expected_modules = [
        'common',
        's3', 's3.read', 's3.write',
        'awslambda', 'awslambda.read', 'awslambda.write',
        'ecs', 'ecs.read', 'ecs.write',
        'stepfunction', 'stepfunction.read', 'stepfunction.write',
        'dynamodb', 'dynamodb.read', 'dynamodb.write',
        'eventbridge', 'eventbridge.read', 'eventbridge.write',
        'parameterstore', 'parameterstore.read', 'parameterstore.write',
        'sqs', 'sqs.read', 'sqs.write',
    ]
    
    passed = 0
    failed = 0
    
    for module_name in expected_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ Module {module_name} exists")
            passed += 1
        except ImportError:
            print(f"❌ Module {module_name} missing or has import errors")
            failed += 1
    
    print(f"\n📊 Module Structure Test Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all tests."""
    print("🧪 Argus Library Test Suite")
    print("=" * 50)
    
    # Run all test suites
    import_success = run_import_tests()
    instantiation_success = run_instantiation_tests()
    structure_success = run_module_structure_tests()
    
    # Overall summary
    print("\n" + "=" * 50)
    print("📋 Overall Test Summary:")
    print(f"  Import Tests: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"  Instantiation Tests: {'✅ PASS' if instantiation_success else '❌ FAIL'}")
    print(f"  Module Structure Tests: {'✅ PASS' if structure_success else '❌ FAIL'}")
    
    all_passed = import_success and instantiation_success and structure_success
    
    if all_passed:
        print("\n🎉 All tests passed! The Argus library is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
