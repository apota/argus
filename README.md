# Argus - AWS Resource Explorer Library

Argus is a Python library for exploring and managing AWS resources using Boto3. It provides a modular, organized approach to interact with various AWS services through a consistent interface.

## Features

- **Modular Structure**: Separate read and write modules for each AWS service
- **Consistent Interface**: Unified approach across all AWS services
- **Profile Support**: Uses AWS credential profiles for authentication
- **Comprehensive Coverage**: Supports major AWS services including S3, Lambda, ECS, Step Functions, DynamoDB, EventBridge, Parameter Store, and SQS
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

## Usage Examples

### S3 Operations

#### Reading S3 Resources
```python
from src.s3 import S3Reader

# Initialize with default profile
s3_reader = S3Reader()

# Initialize with specific profile and region
s3_reader = S3Reader(profile_name='production', region_name='us-west-2')

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
from src.s3 import S3Writer

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
from src.lambda import LambdaReader

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
from src.lambda import LambdaWriter

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
from src.ecs import ECSReader

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
from src.ecs import ECSWriter

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
```

## Error Handling

Argus provides custom exception classes for better error handling:

```python
from src.common.exceptions import AWSResourceError, ResourceNotFoundError
from src.s3 import S3Reader

s3_reader = S3Reader()

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
from src.s3 import S3Reader
s3_reader = S3Reader()
buckets = s3_reader.list_buckets()  # This will log the operation
```

## Advanced Configuration

### Custom Client Configuration

You can customize the underlying Boto3 client configuration:

```python
from src.common.aws_client import AWSClientManager

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
from src.s3 import S3Reader

# Read from multiple regions
regions = ['us-east-1', 'us-west-2', 'eu-west-1']
all_buckets = []

for region in regions:
    s3_reader = S3Reader(region_name=region)
    buckets = s3_reader.list_buckets()
    all_buckets.extend(buckets)

print(f"Total buckets across all regions: {len(all_buckets)}")
```

## Available Services

### Currently Implemented
- **S3**: Complete read/write operations for buckets and objects
- **Lambda**: Complete read/write operations for functions, layers, and aliases
- **ECS**: Complete read/write operations for clusters, services, and task definitions

### Coming Soon
- **Step Functions**: State machine management
- **DynamoDB**: Table and item operations
- **EventBridge**: Event bus and rule management
- **Parameter Store**: Parameter management
- **SQS**: Queue and message operations

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
python -c "from src.s3 import S3Reader; print('Import successful')"
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
