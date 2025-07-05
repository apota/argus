# Argus - AWS Resource Explorer Library

Argus is a Python library for exploring and managing AWS resources using Boto3. It provides a modular, organized approach to interact with various AWS services through a consistent interface.

**This is perfect for people who don't like clicking around the AWS console (especially when you are managing several artifacts across multiple accounts), all that pointing and clicking slows you down.**

> 🚀 **Latest Update**: All major AWS services are now fully implemented! The library includes complete support for S3, Lambda, ECS (with scaling), Step Functions, DynamoDB, EventBridge, Parameter Store, SQS, and CloudWatch (with log querying). Each service has comprehensive read/write operations, examples, and test coverage.

## Features

- **Modular Structure**: Separate read and write modules for each AWS service
- **Consistent Interface**: Unified approach across all AWS services
- **Profile Support**: Uses AWS credential profiles for authentication
- **Comprehensive Coverage**: Supports major AWS services including S3, Lambda, ECS, Step Functions, DynamoDB, EventBridge, Parameter Store, SQS, and CloudWatch
- **Error Handling**: Custom exception handling for better error management
- **Logging**: Built-in logging for debugging and monitoring

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd argus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Verify installation by running tests:
```bash
cd src/test
python test_runner.py
```

## Testing and Examples

Argus includes a comprehensive test suite and example scripts:

### Test Suite
- **`src/test/test_runner.py`**: Comprehensive test runner with import and module structure validation
- **`src/test/test_imports.py`**: Simple import verification for all modules
- **`src/test/test_quick.py`**: Quick functionality tests without AWS calls
- **`src/test/test_common.py`**: Unit tests with mocking

### Example Scripts
- **`demo.py`**: Interactive demo showcasing all AWS services
- **`ecs_example.py`**: ECS-specific examples with scaling operations
- **`cloudwatch_example.py`**: CloudWatch log querying and metrics examples

Run the demo to explore all services:
```bash
python demo.py
```

## Prerequisites

- Python 3.7 or higher
- AWS CLI configured with appropriate credentials
- Boto3 and related dependencies (see requirements.txt)

## Directory Structure

```
argus/
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── common/
    │   ├── __init__.py
    │   ├── aws_client.py          # AWS client management
    │   └── exceptions.py          # Custom exception classes
    ├── test/
    │   ├── __init__.py
    │   ├── README.md              # Test documentation
    │   ├── test_runner.py         # Comprehensive test runner
    │   ├── test_imports.py        # Import validation tests
    │   ├── test_quick.py          # Quick functionality tests
    │   └── test_common.py         # Unit tests with mocking
    ├── s3/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── s3_reader.py       # S3 read operations
    │   └── write/
    │       └── s3_writer.py       # S3 write operations
    ├── awslambda/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── lambda_reader.py   # Lambda read operations
    │   └── write/
    │       └── lambda_writer.py   # Lambda write operations
    ├── ecs/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── ecs_reader.py      # ECS read operations
    │   └── write/
    │       └── ecs_writer.py      # ECS write operations
    ├── stepfunction/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── sf_reader.py       # Step Functions read operations
    │   └── write/
    │       └── sf_writer.py       # Step Functions write operations
    ├── dynamodb/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── dynamodb_reader.py # DynamoDB read operations
    │   └── write/
    │       └── dynamodb_writer.py # DynamoDB write operations
    ├── eventbridge/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── eb_reader.py       # EventBridge read operations
    │   └── write/
    │       └── eb_writer.py       # EventBridge write operations
    ├── parameterstore/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── ps_reader.py       # Parameter Store read operations
    │   └── write/
    │       └── ps_writer.py       # Parameter Store write operations
    └── sqs/
        ├── __init__.py
        ├── read/
        │   └── sqs_reader.py      # SQS read operations
        └── write/
            └── sqs_writer.py      # SQS write operations
    └── cloudwatch/
        ├── __init__.py
        ├── read/
        │   └── cloudwatch_reader.py  # CloudWatch read operations
        └── write/
            └── cloudwatch_writer.py  # CloudWatch write operations
```

## AWS Credentials Configuration

Argus uses AWS profiles for authentication. Configure your AWS credentials using one of these methods:

### Method 1: AWS CLI Configuration
```bash
aws configure --profile your-profile-name
```

### Method 2: Credentials File
Edit `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1

[production]
aws_access_key_id = PROD_ACCESS_KEY
aws_secret_access_key = PROD_SECRET_KEY
region = us-west-2
```

### Method 3: Environment Variables
```bash
export AWS_PROFILE=your-profile-name
export AWS_DEFAULT_REGION=us-east-1
```

## Installation

### Option 1: Install from source (Recommended for development)
```bash
git clone https://github.com/your-org/argus.git
cd argus
pip install -e .
```

### Option 2: Install from PyPI (when available)
```bash
pip install argus-aws
```

## Usage Examples

### S3 Operations

#### Reading S3 Resources
```python
from common.aws_client import AWSClientManager
from s3.read.s3_reader import S3Reader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize S3 reader
s3_reader = S3Reader(client_manager)

# List all buckets
buckets = s3_reader.list_buckets()
print(f"Found {len(buckets)} buckets")

# Get bucket information
bucket_info = s3_reader.get_bucket_info('my-bucket')
print(f"Bucket location: {bucket_info.get('LocationConstraint')}")

# List objects in a bucket
objects = s3_reader.list_objects('my-bucket', prefix='logs/')
for obj in objects:
    print(f"Object: {obj['Key']}, Size: {obj['Size']}")

# Get object metadata
metadata = s3_reader.get_object_metadata('my-bucket', 'important-file.txt')
print(f"Last modified: {metadata['LastModified']}")
```

#### Writing S3 Resources
```python
from common.aws_client import AWSClientManager
from s3.write.s3_writer import S3Writer

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize S3 writer
s3_writer = S3Writer(client_manager)

# Initialize S3 writer
s3_writer = S3Writer(profile_name='default')

# Create a new bucket
bucket_config = s3_writer.create_bucket(
    bucket_name='my-new-bucket',
    region='us-west-2'
)

# Upload a file
s3_writer.upload_file(
    bucket_name='my-new-bucket',
    object_key='data/sample.txt',
    file_path='/local/path/to/file.txt'
)

# Upload string content
s3_writer.upload_object(
    bucket_name='my-new-bucket',
    object_key='config/settings.json',
    content='{"environment": "production"}',
    content_type='application/json'
)

# Set bucket policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-new-bucket/*"
        }
    ]
}
s3_writer.set_bucket_policy('my-new-bucket', policy)
```

### Lambda Operations

#### Reading Lambda Resources
```python
from common.aws_client import AWSClientManager
from awslambda.read.lambda_reader import LambdaReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Lambda reader
lambda_reader = LambdaReader(client_manager)

# Initialize Lambda reader
lambda_reader = LambdaReader(profile_name='default')

# List all functions
functions = lambda_reader.list_functions()
for func in functions:
    print(f"Function: {func['FunctionName']}, Runtime: {func['Runtime']}")

# Get function details
function_info = lambda_reader.get_function('my-function')
print(f"Function ARN: {function_info['Configuration']['FunctionArn']}")

# List function aliases
aliases = lambda_reader.list_aliases('my-function')
for alias in aliases:
    print(f"Alias: {alias['Name']}, Version: {alias['FunctionVersion']}")

# List layers
layers = lambda_reader.list_layers()
for layer in layers:
    print(f"Layer: {layer['LayerName']}")
```

#### Writing Lambda Resources
```python
from common.aws_client import AWSClientManager
from awslambda.write.lambda_writer import LambdaWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Lambda writer
lambda_writer = LambdaWriter(client_manager)

# Initialize Lambda writer
lambda_writer = LambdaWriter(profile_name='default')

# Create simple Python function code
code = '''
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
'''

# Create deployment package
zip_content = LambdaWriter.create_deployment_package(code)

# Create function
function_config = lambda_writer.create_function(
    function_name='my-new-function',
    runtime='python3.9',
    role='arn:aws:iam::123456789012:role/lambda-execution-role',
    handler='lambda_function.lambda_handler',
    code={'ZipFile': zip_content},
    description='My new Lambda function',
    timeout=30,
    memory_size=256
)

# Create an alias
alias = lambda_writer.create_alias(
    function_name='my-new-function',
    alias_name='production',
    function_version='1'
)

# Update function code
updated_code = '''
def lambda_handler(event, context):
    print(f"Event: {event}")
    return {
        'statusCode': 200,
        'body': 'Updated Lambda function!'
    }
'''
new_zip = LambdaWriter.create_deployment_package(updated_code)
lambda_writer.update_function_code('my-new-function', zip_file=new_zip)
```

### ECS Operations

#### Reading ECS Resources
```python
from common.aws_client import AWSClientManager
from ecs.read.ecs_reader import ECSReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize ECS reader
ecs_reader = ECSReader(client_manager)

# Initialize ECS reader
ecs_reader = ECSReader(profile_name='default')

# List clusters
clusters = ecs_reader.list_clusters()
for cluster in clusters:
    print(f"Cluster: {cluster['clusterName']}, Status: {cluster['status']}")

# List services in a cluster
services = ecs_reader.list_services('my-cluster')
for service in services:
    print(f"Service: {service['serviceName']}, Desired: {service['desiredCount']}")

# List task definitions
task_defs = ecs_reader.list_task_definitions(family_prefix='my-app')
for td in task_defs:
    print(f"Task Definition: {td}")

# Get task definition details
task_def = ecs_reader.describe_task_definition('my-app:1')
print(f"CPU: {task_def.get('cpu')}, Memory: {task_def.get('memory')}")
```

#### Writing ECS Resources
```python
from common.aws_client import AWSClientManager
from ecs.write.ecs_writer import ECSWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize ECS writer
ecs_writer = ECSWriter(client_manager)

# Initialize ECS writer
ecs_writer = ECSWriter(profile_name='default')

# Create a cluster
cluster = ecs_writer.create_cluster(
    cluster_name='my-new-cluster',
    capacity_providers=['FARGATE', 'FARGATE_SPOT']
)

# Register task definition
container_def = {
    'name': 'my-container',
    'image': 'nginx:latest',
    'portMappings': [
        {
            'containerPort': 80,
            'protocol': 'tcp'
        }
    ],
    'memory': 512,
    'essential': True
}

task_def = ecs_writer.register_task_definition(
    family='my-web-app',
    container_definitions=[container_def],
    requires_compatibilities=['FARGATE'],
    network_mode='awsvpc',
    cpu='256',
    memory='512'
)

# Create a service
service = ecs_writer.create_service(
    service_name='my-web-service',
    task_definition='my-web-app:1',
    cluster='my-new-cluster',
    desired_count=2,
    launch_type='FARGATE'
)

# Scale service up/down
ecs_writer.scale_service('my-web-service', 'my-new-cluster', 5)
ecs_writer.scale_up('my-web-service', 'my-new-cluster', 2)  # Increment by 2
ecs_writer.scale_down('my-web-service', 'my-new-cluster', 1)  # Decrement by 1
```

### CloudWatch Operations

#### Reading CloudWatch Logs and Metrics
```python
from common.aws_client import AWSClientManager
from cloudwatch import CloudWatchReader, CloudWatchWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize CloudWatch reader
cw_reader = CloudWatchReader(client_manager)

# List log groups
log_groups = cw_reader.list_log_groups(prefix='/aws/lambda/', limit=10)
for lg in log_groups:
    print(f"Log Group: {lg['logGroupName']}, Size: {lg.get('storedBytes', 0)} bytes")

# List log streams in a group
log_streams = cw_reader.list_log_streams('/aws/lambda/my-function')
for stream in log_streams[:3]:
    print(f"Stream: {stream['logStreamName']}")

# Search for specific log events
error_logs = cw_reader.search_log_events(
    log_group_name='/aws/lambda/my-function',
    search_term='ERROR',
    hours_back=24
)
for event in error_logs[:5]:
    print(f"Error: {event['message']}")

# Get recent logs
recent_logs = cw_reader.get_recent_logs(
    log_group_name='/aws/lambda/my-function',
    minutes_back=60
)

# Filter logs with pattern
filtered_logs = cw_reader.filter_log_events(
    log_group_name='/aws/lambda/my-function',
    filter_pattern='[timestamp, request_id, level="ERROR", message]',
    limit=50
)

# Get metrics
cpu_metrics = cw_reader.get_metric_statistics(
    namespace='AWS/EC2',
    metric_name='CPUUtilization',
    dimensions=[{'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}],
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow(),
    period=300,
    statistics=['Average', 'Maximum']
)
```

#### Writing CloudWatch Resources
```python
# Initialize CloudWatch writer
cw_writer = CloudWatchWriter(client_manager)

# Create log group
cw_writer.create_log_group('my-application-logs', retention_days=30)

# Create log stream
cw_writer.create_log_stream('my-application-logs', 'stream-1')

# Put log messages
cw_writer.put_log_message(
    log_group_name='my-application-logs',
    log_stream_name='stream-1',
    message='Application started successfully'
)

# Put multiple log events
log_events = [
    {
        'timestamp': int(datetime.utcnow().timestamp() * 1000),
        'message': 'Processing request 1'
    },
    {
        'timestamp': int(datetime.utcnow().timestamp() * 1000) + 1000,
        'message': 'Request 1 completed'
    }
]
cw_writer.put_log_events('my-application-logs', 'stream-1', log_events)

# Publish custom metrics
cw_writer.put_metric(
    namespace='MyApplication',
    metric_name='RequestCount',
    value=42,
    unit='Count',
    dimensions=[
        {'Name': 'Environment', 'Value': 'Production'},
        {'Name': 'Service', 'Value': 'API'}
    ]
)

# Create CloudWatch alarm
cw_writer.create_alarm(
    alarm_name='HighErrorRate',
    alarm_description='Alert when error rate is high',
    metric_name='ErrorRate',
    namespace='MyApplication',
    statistic='Average',
    dimensions=[{'Name': 'Service', 'Value': 'API'}],
    period=300,
    evaluation_periods=2,
    threshold=5.0,
    comparison_operator='GreaterThanThreshold',
    alarm_actions=['arn:aws:sns:us-east-1:123456789012:alerts']
)

# Export logs to S3
task_id = cw_reader.export_logs_to_s3(
    log_group_name='my-application-logs',
    destination_bucket='my-log-archive-bucket',
    destination_prefix='logs/2024/01/',
    start_time=datetime.utcnow() - timedelta(days=1),
    end_time=datetime.utcnow(),
    task_name='daily-export'
)
```
```

## Error Handling

Argus provides custom exception classes for better error handling:

```python
from common.exceptions import AWSResourceError, ResourceNotFoundError
from common.aws_client import AWSClientManager
from s3.read.s3_reader import S3Reader

client_manager = AWSClientManager('default', 'us-east-1')
s3_reader = S3Reader(client_manager)

try:
    bucket_info = s3_reader.get_bucket_info('non-existent-bucket')
except ResourceNotFoundError as e:
    print(f"Bucket not found: {e}")
except AWSResourceError as e:
    print(f"AWS error occurred: {e}")
```

## Logging

Enable logging to see detailed operation information:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all Argus operations will log their activities
from common.aws_client import AWSClientManager
from s3.read.s3_reader import S3Reader

client_manager = AWSClientManager('default', 'us-east-1')
s3_reader = S3Reader(client_manager)
buckets = s3_reader.list_buckets()  # This will log the operation
```

## Advanced Configuration

### Custom Client Configuration

You can customize the underlying Boto3 client configuration:

```python
from common.aws_client import AWSClientManager

# Initialize with custom configuration
client_manager = AWSClientManager(
    profile_name='production',
    region_name='eu-west-1'
)

# Get a client with custom configuration
s3_client = client_manager.get_client('s3')
```

### Working with Multiple Regions

```python
from common.aws_client import AWSClientManager
from s3.read.s3_reader import S3Reader

# Read from multiple regions
regions = ['us-east-1', 'us-west-2', 'eu-west-1']
all_buckets = []

for region in regions:
    client_manager = AWSClientManager('default', region)
    s3_reader = S3Reader(client_manager)

for region in regions:
    s3_reader = S3Reader(region_name=region)
    buckets = s3_reader.list_buckets()
    all_buckets.extend(buckets)

print(f"Total buckets across all regions: {len(all_buckets)}")
```

## Available Services

### Currently Implemented ✅

All major AWS services are now fully implemented with comprehensive read and write operations:

- **S3**: Complete read/write operations for buckets and objects
- **Lambda**: Complete read/write operations for functions, layers, and aliases  
- **ECS**: Complete read/write operations for clusters, services, and task definitions with scaling capabilities
- **Step Functions**: Complete state machine management, execution control, and activity operations
- **DynamoDB**: Complete table and item operations with advanced querying capabilities
- **EventBridge**: Complete event bus and rule management with archive support
- **Parameter Store**: Complete parameter management with hierarchical organization
- **SQS**: Complete queue and message operations with dead letter queue support
- **CloudWatch**: Complete log querying, metrics management, and alarm operations

### Key Features by Service

#### ECS (Enhanced Implementation)
- **Scaling Operations**: Built-in methods for scaling services up/down
- **Task Management**: Complete task lifecycle management
- **Service Health**: Monitor service status and task counts
- **Cluster Operations**: Full cluster management capabilities

#### CloudWatch (New Implementation)
- **Log Operations**: Query, filter, and search CloudWatch logs
- **Log Management**: Create/delete log groups and streams
- **Metrics**: Publish custom metrics and retrieve statistics
- **Alarms**: Create and manage CloudWatch alarms
- **Export**: Export logs to S3 for archival

#### Step Functions (Fully Implemented)
- **State Machine Management**: Create, update, and delete state machines
- **Execution Control**: Start, stop, and monitor executions
- **Activity Support**: Manage Step Function activities
- **History Tracking**: Access detailed execution history

#### Parameter Store (Comprehensive Implementation)
- **Parameter Operations**: Full CRUD operations for parameters
- **Hierarchical Access**: Get parameters by path with filtering
- **Version Management**: Access parameter history and versions
- **Tagging Support**: Complete tag management for parameters

#### EventBridge (Complete Implementation)
- **Event Bus Management**: Create and manage custom event buses
- **Rule Operations**: Complete rule lifecycle management
- **Target Management**: Add/remove targets for rules
- **Archive Support**: Create and manage event archives

#### DynamoDB (Full Implementation)
- **Table Operations**: Complete table lifecycle management
- **Item Operations**: Advanced CRUD with conditional operations
- **Query & Scan**: Optimized querying with pagination support
- **Index Management**: Global and local secondary index operations

#### SQS (Complete Implementation)
- **Queue Management**: Full queue lifecycle operations
- **Message Operations**: Send, receive, and delete messages
- **Dead Letter Queues**: Complete DLQ configuration and management
- **Visibility Timeout**: Advanced message handling

## Best Practices

1. **Use Specific Profiles**: Always specify the AWS profile for different environments
2. **Handle Exceptions**: Use try-catch blocks with specific exception types
3. **Enable Logging**: Use logging to monitor operations and debug issues
4. **Least Privilege**: Ensure your AWS credentials have only necessary permissions
5. **Resource Cleanup**: Always clean up resources you create during testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the existing GitHub issues
2. Create a new issue with detailed information
3. Include relevant error messages and configurations

## Troubleshooting

### Common Issues

#### Import Errors
If you encounter import errors, ensure you're running Python from the correct directory and the package is properly installed:
```bash
cd argus
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -c "from s3.read.s3_reader import S3Reader; print('Import successful')"
```

#### AWS Credential Issues
Verify your AWS credentials are properly configured:
```bash
aws sts get-caller-identity --profile your-profile-name
```

#### Permission Denied
Ensure your AWS user/role has the necessary permissions for the operations you're trying to perform.

### Debug Mode
Enable debug logging to see detailed AWS API calls:
```python
import logging
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)
```
