#!/usr/bin/env python3
"""
Example script demonstrating S3 object touch functionality.

This script shows how to use the touch_object method to update
the LastModified timestamp of S3 objects.
"""

import sys
import os

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from common.aws_client import AWSClientManager
from s3.write.s3_writer import S3Writer
from s3.read.s3_reader import S3Reader


def demonstrate_s3_touch():
    """Demonstrate S3 object touch functionality."""
    try:
        # Initialize AWS client manager
        client_manager = AWSClientManager('default', 'us-east-1')
        
        # Initialize S3 reader and writer
        s3_reader = S3Reader(client_manager)
        s3_writer = S3Writer(client_manager)
        
        # Example configuration
        bucket_name = 'my-test-bucket'
        object_key = 'test-file.txt'
        
        print("🔍 S3 Object Touch Demonstration")
        print("=" * 50)
        
        # Check if object exists first
        print(f"\n1. Checking if object exists: {object_key}")
        try:
            object_info = s3_reader.get_object_metadata(bucket_name, object_key)
            print(f"   ✅ Object found!")
            print(f"   📅 Current LastModified: {object_info.get('LastModified')}")
            
            if 'Metadata' in object_info and 'touched-at' in object_info['Metadata']:
                print(f"   🏷️  Previous touch timestamp: {object_info['Metadata']['touched-at']}")
            
        except Exception as e:
            print(f"   ❌ Object not found or error: {e}")
            print("   💡 Please ensure the object exists before running this demo")
            return
        
        # Touch the object
        print(f"\n2. Touching object: {object_key}")
        touch_result = s3_writer.touch_object(
            bucket_name=bucket_name,
            object_key=object_key,
            preserve_metadata=True,
            custom_metadata={
                'demo-run': 'true',
                'script-version': '1.0'
            }
        )
        
        print(f"   ✅ Touch operation successful!")
        print(f"   📅 Previous LastModified: {touch_result['previous_last_modified']}")
        print(f"   📅 New LastModified: {touch_result['new_last_modified']}")
        print(f"   🏷️  Touch timestamp: {touch_result['touched_at']}")
        print(f"   🆔 New ETag: {touch_result['etag']}")
        
        # Demonstrate batch touch
        print(f"\n3. Demonstrating batch touch (if multiple objects exist)")
        batch_objects = ['test-file.txt', 'another-file.txt', 'third-file.txt']
        
        batch_result = s3_writer.batch_touch_objects(
            bucket_name=bucket_name,
            object_keys=batch_objects,
            preserve_metadata=True,
            custom_metadata={'batch-touch': 'demo'}
        )
        
        print(f"   📊 Batch touch results:")
        print(f"   • Total objects: {batch_result['total_objects']}")
        print(f"   • Successful: {batch_result['successful_touches']}")
        print(f"   • Failed: {batch_result['failed_touches']}")
        
        if batch_result['touched_objects']:
            print(f"   ✅ Successfully touched objects:")
            for obj in batch_result['touched_objects']:
                print(f"      - {obj['object_key']} (touched at: {obj['touched_at']})")
        
        if batch_result['failed_objects']:
            print(f"   ❌ Failed objects:")
            for obj in batch_result['failed_objects']:
                print(f"      - {obj['object_key']}: {obj['error']}")
        
        print(f"\n🎉 Touch demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return 1


def show_usage():
    """Show usage examples for touch functionality."""
    print("""
🔧 S3 Touch Functionality Usage Examples:

1. Basic touch operation:
   ```python
   result = s3_writer.touch_object('my-bucket', 'my-file.txt')
   ```

2. Touch with custom metadata:
   ```python
   result = s3_writer.touch_object(
       bucket_name='my-bucket',
       object_key='my-file.txt',
       preserve_metadata=True,
       custom_metadata={'cache-invalidated': 'true'}
   )
   ```

3. Batch touch multiple objects:
   ```python
   result = s3_writer.batch_touch_objects(
       bucket_name='my-bucket',
       object_keys=['file1.txt', 'file2.txt', 'file3.txt'],
       custom_metadata={'batch-update': 'v2.0'}
   )
   ```

💡 Use Cases:
• Cache invalidation by updating object timestamps
• Triggering S3 event notifications without changing content
• Updating metadata without re-uploading large files
• Batch operations for multiple files
• Workflow automation based on object modification times
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--usage':
        show_usage()
    else:
        print("Note: This demo requires AWS credentials and an existing S3 bucket with test objects.")
        print("Run with --usage to see usage examples without running the demo.")
        print()
        result = demonstrate_s3_touch()
        sys.exit(result or 0)
