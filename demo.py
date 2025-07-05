#!/usr/bin/env python3
"""
Argus AWS Resource Explorer - Example Usage Script

This script demonstrates how to use the Argus library to explore AWS resources.
Run this script to see examples of reading various AWS resources.
"""

import logging
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demonstrate_s3():
    """Demonstrate S3 operations."""
    try:
        from src.s3 import S3Reader
        
        print("🪣 S3 Operations Demo")
        print("=" * 50)
        
        # Initialize S3 reader with default profile
        s3_reader = S3Reader()
        
        # List buckets
        print("📋 Listing S3 buckets...")
        buckets = s3_reader.list_buckets()
        print(f"Found {len(buckets)} S3 buckets:")
        for bucket in buckets[:5]:  # Show first 5 buckets
            print(f"  • {bucket['Name']} (Created: {bucket['CreationDate']})")
        
        # If we have buckets, demonstrate more operations
        if buckets:
            bucket_name = buckets[0]['Name']
            print(f"\n🔍 Getting information for bucket: {bucket_name}")
            
            try:
                bucket_info = s3_reader.get_bucket_info(bucket_name)
                location = bucket_info.get('LocationConstraint') or 'us-east-1'
                print(f"  Location: {location}")
                
                # List some objects
                print(f"\n📁 Listing objects in {bucket_name} (max 5)...")
                objects = s3_reader.list_objects(bucket_name, max_keys=5)
                if objects:
                    for obj in objects:
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f"  • {obj['Key']} ({size_mb:.2f} MB)")
                else:
                    print("  No objects found in bucket")
                    
            except Exception as e:
                print(f"  Could not access bucket details: {e}")
        
        print("✅ S3 operations completed successfully\n")
        
    except ImportError:
        print("❌ Could not import S3 modules. Check your installation.\n")
    except Exception as e:
        print(f"❌ Error in S3 operations: {e}\n")


def demonstrate_lambda():
    """Demonstrate Lambda operations."""
    try:
        from src.awslambda.read.lambda_reader import LambdaReader
        
        print("⚡ Lambda Operations Demo")
        print("=" * 50)
        
        # Initialize Lambda reader with default profile
        lambda_reader = LambdaReader()
        
        # List functions
        print("📋 Listing Lambda functions...")
        functions = lambda_reader.list_functions(max_items=10)
        print(f"Found {len(functions)} Lambda functions:")
        for func in functions[:5]:  # Show first 5 functions
            print(f"  • {func['FunctionName']} ({func['Runtime']}) - {func.get('Description', 'No description')[:50]}")
        
        # If we have functions, demonstrate more operations
        if functions:
            function_name = functions[0]['FunctionName']
            print(f"\n🔍 Getting details for function: {function_name}")
            
            try:
                function_config = lambda_reader.get_function_configuration(function_name)
                print(f"  Memory: {function_config['MemorySize']} MB")
                print(f"  Timeout: {function_config['Timeout']} seconds")
                print(f"  Last Modified: {function_config['LastModified']}")
                
                # List aliases
                aliases = lambda_reader.list_aliases(function_name)
                if aliases:
                    print(f"  Aliases: {', '.join([alias['Name'] for alias in aliases])}")
                else:
                    print("  No aliases found")
                    
            except Exception as e:
                print(f"  Could not access function details: {e}")
        
        # List layers
        print(f"\n📚 Listing Lambda layers...")
        layers = lambda_reader.list_layers()
        print(f"Found {len(layers)} Lambda layers:")
        for layer in layers[:3]:  # Show first 3 layers
            print(f"  • {layer['LayerName']}")
        
        print("✅ Lambda operations completed successfully\n")
        
    except ImportError:
        print("❌ Could not import Lambda modules. Check your installation.\n")
    except Exception as e:
        print(f"❌ Error in Lambda operations: {e}\n")


def demonstrate_ecs():
    """Demonstrate ECS operations."""
    try:
        from src.ecs import ECSReader
        
        print("🐳 ECS Operations Demo")
        print("=" * 50)
        
        # Initialize ECS reader with default profile
        ecs_reader = ECSReader()
        
        # List clusters
        print("📋 Listing ECS clusters...")
        clusters = ecs_reader.list_clusters()
        print(f"Found {len(clusters)} ECS clusters:")
        for cluster in clusters:
            print(f"  • {cluster['clusterName']} ({cluster['status']}) - {cluster['runningTasksCount']} running tasks")
        
        # If we have clusters, demonstrate more operations
        if clusters:
            cluster_name = clusters[0]['clusterName']
            print(f"\n🔍 Getting services in cluster: {cluster_name}")
            
            try:
                services = ecs_reader.list_services(cluster_name)
                print(f"Found {len(services)} services:")
                for service in services[:3]:  # Show first 3 services
                    print(f"  • {service['serviceName']} (Desired: {service['desiredCount']}, Running: {service['runningCount']})")
                    
            except Exception as e:
                print(f"  Could not access cluster services: {e}")
        
        # List task definitions
        print(f"\n📋 Listing task definitions...")
        task_definitions = ecs_reader.list_task_definitions()[:5]  # First 5
        print(f"Found task definitions (showing first 5):")
        for td in task_definitions:
            family_revision = td.split('/')[-1] if '/' in td else td
            print(f"  • {family_revision}")
        
        print("✅ ECS operations completed successfully\n")
        
    except ImportError:
        print("❌ Could not import ECS modules. Check your installation.\n")
    except Exception as e:
        print(f"❌ Error in ECS operations: {e}\n")


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ProfileNotFound
        
        # Try to create a session and get caller identity
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ AWS Credentials Configuration")
        print("=" * 50)
        print(f"Account ID: {identity.get('Account')}")
        print(f"User ARN: {identity.get('Arn')}")
        print(f"Region: {session.region_name or 'Not specified'}")
        print("")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("Please configure your AWS credentials using one of these methods:")
        print("  1. aws configure")
        print("  2. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("  3. Use IAM roles (if running on EC2)")
        print("")
        return False
    except ProfileNotFound as e:
        print(f"❌ AWS profile not found: {e}")
        print("Check your AWS profile configuration.")
        print("")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS credentials: {e}")
        print("")
        return False


def main():
    """Main demonstration function."""
    print("🚀 Argus AWS Resource Explorer - Demo Script")
    print("=" * 60)
    print("This script demonstrates the Argus library capabilities.")
    print("Make sure your AWS credentials are configured before running.\n")
    
    # Check AWS credentials first
    if not check_aws_credentials():
        print("⚠️  Please configure your AWS credentials and try again.")
        return 1
    
    # Run demonstrations
    print("🔍 Starting AWS resource exploration...\n")
    
    demonstrate_s3()
    demonstrate_lambda()
    demonstrate_ecs()
    
    print("🎉 Demo completed!")
    print("Check the Argus documentation for more advanced usage examples.")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in demo: {e}")
        sys.exit(1)
