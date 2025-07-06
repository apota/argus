# Argus - AWS Resource Explorer Library

Argus is a Python library for exploring and managing AWS resources using Boto3. It provides a modular, organized approach to interact with various AWS services through a consistent interface.

## Target Audience

- Devs who want to quickly toggle across multiple AWS environments (production, dev, test) to query and manage the AWS landscape. All that pointing & clicking on AWS console can slow you down and frankly give you carpal tunnel syndrome (CTS)!

## Features

- **Modular Structure**: Separate read and write modules for each AWS service
- **Consistent Interface**: Unified approach across all AWS services using AWSClientManager pattern
- **Profile Support**: Uses AWS credential profiles for authentication
- **Comprehensive Coverage**: Supports major AWS services including S3, Lambda, ECS, Step Functions, DynamoDB, EventBridge, Parameter Store, SQS, EC2, Elastic Beanstalk, EKS, and CloudWatch
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
    ├── ec2/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── ec2_reader.py      # EC2 read operations
    │   └── write/
    │       └── ec2_writer.py      # EC2 write operations
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
    ├── sqs/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── sqs_reader.py      # SQS read operations
    │   └── write/
    │       └── sqs_writer.py      # SQS write operations
    ├── ebs/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── ebs_reader.py      # Elastic Beanstalk read operations
    │   └── write/
    │       └── ebs_writer.py      # Elastic Beanstalk write operations
    ├── eks/
    │   ├── __init__.py
    │   ├── read/
    │   │   └── eks_reader.py      # Elastic Kubernetes Service read operations
    │   └── write/
    │       └── eks_writer.py      # Elastic Kubernetes Service write operations
    └── cloudwatch/
        ├── __init__.py
        └── read/
            └── cloudwatch_reader.py # CloudWatch read operations
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

# Scale service
ecs_writer.scale_service('my-web-service', 'my-new-cluster', 5)
```

### EC2 Operations

#### Reading EC2 Resources
```python
from common.aws_client import AWSClientManager
from ec2.read.ec2_reader import EC2Reader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EC2 reader
ec2_reader = EC2Reader(client_manager)

# List all instances
instances = ec2_reader.list_instances()
for instance in instances:
    print(f"Instance: {instance['InstanceId']}, State: {instance['State']['Name']}")

# Get specific instance details
instance = ec2_reader.get_instance('i-1234567890abcdef0')
print(f"Instance Type: {instance['InstanceType']}")
print(f"Public IP: {instance.get('PublicIpAddress', 'N/A')}")

# List security groups
security_groups = ec2_reader.list_security_groups()
for sg in security_groups:
    print(f"Security Group: {sg['GroupId']}, Name: {sg['GroupName']}")

# List key pairs
key_pairs = ec2_reader.list_key_pairs()
for kp in key_pairs:
    print(f"Key Pair: {kp['KeyName']}")

# List VPCs
vpcs = ec2_reader.list_vpcs()
for vpc in vpcs:
    print(f"VPC: {vpc['VpcId']}, CIDR: {vpc['CidrBlock']}")

# List subnets for a VPC
subnets = ec2_reader.list_subnets(vpc_id='vpc-12345678')
for subnet in subnets:
    print(f"Subnet: {subnet['SubnetId']}, CIDR: {subnet['CidrBlock']}")
```

#### Writing EC2 Resources
```python
from common.aws_client import AWSClientManager
from ec2.write.ec2_writer import EC2Writer

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EC2 writer
ec2_writer = EC2Writer(client_manager)

# Launch new instances
response = ec2_writer.create_instance(
    image_id='ami-0abcdef1234567890',
    instance_type='t2.micro',
    key_name='my-key-pair',
    security_group_ids=['sg-12345678'],
    subnet_id='subnet-12345678',
    min_count=1,
    max_count=1
)

instance_id = response['Instances'][0]['InstanceId']
print(f"Launched instance: {instance_id}")

# Start a stopped instance
ec2_writer.start_instance(instance_id)

# Stop a running instance
ec2_writer.stop_instance(instance_id)

# Reboot an instance
ec2_writer.reboot_instance(instance_id)

# Create a security group
sg_response = ec2_writer.create_security_group(
    group_name='my-web-sg',
    description='Security group for web servers',
    vpc_id='vpc-12345678'
)

group_id = sg_response['GroupId']

# Add inbound rules to security group
ip_permissions = [
    {
        'IpProtocol': 'tcp',
        'FromPort': 80,
        'ToPort': 80,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 443,
        'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }
]

ec2_writer.authorize_security_group_ingress(group_id, ip_permissions)

# Create a key pair
key_response = ec2_writer.create_key_pair('my-new-key')
print(f"Created key pair: {key_response['KeyName']}")

# Create tags for resources
ec2_writer.create_tags(
    resource_ids=[instance_id, group_id],
    tags=[
        {'Key': 'Environment', 'Value': 'Development'},
        {'Key': 'Project', 'Value': 'MyApp'}
    ]
)

# Terminate instance when done
ec2_writer.terminate_instance(instance_id)
```

### Step Functions Operations

#### Reading Step Functions Resources
```python
from common.aws_client import AWSClientManager
from stepfunction.read.sf_reader import SFReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Step Functions reader
sf_reader = SFReader(client_manager)

# List state machines
state_machines = sf_reader.list_state_machines()
for sm in state_machines:
    print(f"State Machine: {sm['name']}, Status: {sm['status']}")

# Get state machine details
sm_detail = sf_reader.describe_state_machine('my-state-machine')
print(f"Definition: {sm_detail['definition']}")

# List executions
executions = sf_reader.list_executions('my-state-machine')
for execution in executions:
    print(f"Execution: {execution['name']}, Status: {execution['status']}")
```

#### Writing Step Functions Resources
```python
from common.aws_client import AWSClientManager
from stepfunction.write.sf_writer import SFWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Step Functions writer
sf_writer = SFWriter(client_manager)

# Define state machine
definition = {
    "Comment": "A Hello World example",
    "StartAt": "HelloWorld",
    "States": {
        "HelloWorld": {
            "Type": "Pass",
            "Result": "Hello World!",
            "End": True
        }
    }
}

# Create state machine
state_machine = sf_writer.create_state_machine(
    name='my-hello-world-sm',
    definition=definition,
    role_arn='arn:aws:iam::123456789012:role/StepFunctionsRole'
)

# Start execution
execution = sf_writer.start_execution(
    state_machine_arn=state_machine['stateMachineArn'],
    name='execution-1',
    input_data={'key': 'value'}
)
```

### DynamoDB Operations

#### Reading DynamoDB Resources
```python
from common.aws_client import AWSClientManager
from dynamodb.read.dynamodb_reader import DynamoDBReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize DynamoDB reader
dynamo_reader = DynamoDBReader(client_manager)

# List all tables
tables = dynamo_reader.list_tables()
for table in tables:
    print(f"Table: {table}")

# Get table details
table_info = dynamo_reader.describe_table('my-table')
print(f"Item count: {table_info['Table']['ItemCount']}")

# Get item
item = dynamo_reader.get_item('my-table', {'id': 'user-123'})
print(f"Item: {item}")

# Query items
items = dynamo_reader.query('my-table', key_condition='id = :id', 
                           expression_values={':id': 'user-123'})
for item in items:
    print(f"Found: {item}")
```

#### Writing DynamoDB Resources
```python
from common.aws_client import AWSClientManager
from dynamodb.write.dynamodb_writer import DynamoDBWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize DynamoDB writer
dynamo_writer = DynamoDBWriter(client_manager)

# Create table
table = dynamo_writer.create_table(
    table_name='my-new-table',
    key_schema=[
        {'AttributeName': 'id', 'KeyType': 'HASH'}
    ],
    attribute_definitions=[
        {'AttributeName': 'id', 'AttributeType': 'S'}
    ],
    billing_mode='PAY_PER_REQUEST'
)

# Put item
dynamo_writer.put_item('my-new-table', {
    'id': 'user-123',
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Update item
dynamo_writer.update_item(
    'my-new-table',
    {'id': 'user-123'},
    update_expression='SET #name = :name',
    expression_attribute_names={'#name': 'name'},
    expression_attribute_values={':name': 'John Smith'}
)
```

### EventBridge Operations

#### Reading EventBridge Resources
```python
from common.aws_client import AWSClientManager
from eventbridge.read.eb_reader import EBReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EventBridge reader
eb_reader = EBReader(client_manager)

# List event buses
event_buses = eb_reader.list_event_buses()
for bus in event_buses:
    print(f"Event Bus: {bus['Name']}")

# List rules
rules = eb_reader.list_rules(event_bus_name='default')
for rule in rules:
    print(f"Rule: {rule['Name']}, State: {rule['State']}")

# Get rule details
rule_detail = eb_reader.describe_rule('my-rule')
print(f"Schedule: {rule_detail.get('ScheduleExpression')}")
```

#### Writing EventBridge Resources
```python
from common.aws_client import AWSClientManager
from eventbridge.write.eb_writer import EBWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EventBridge writer
eb_writer = EBWriter(client_manager)

# Create custom event bus
event_bus = eb_writer.create_event_bus('my-custom-bus')

# Create rule
rule = eb_writer.put_rule(
    name='my-scheduled-rule',
    schedule_expression='rate(5 minutes)',
    description='Runs every 5 minutes',
    event_bus_name='my-custom-bus'
)

# Add targets to rule
eb_writer.put_targets(
    rule='my-scheduled-rule',
    event_bus_name='my-custom-bus',
    targets=[
        {
            'Id': '1',
            'Arn': 'arn:aws:lambda:us-east-1:123456789012:function:my-function'
        }
    ]
)

# Send custom event
eb_writer.put_events([
    {
        'Source': 'my.application',
        'DetailType': 'User Action',
        'Detail': '{"action": "login", "user": "john"}',
        'EventBusName': 'my-custom-bus'
    }
])
```

### Parameter Store Operations

#### Reading Parameter Store Resources
```python
from common.aws_client import AWSClientManager
from parameterstore.read.ps_reader import PSReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Parameter Store reader
ps_reader = PSReader(client_manager)

# Get parameter
parameter = ps_reader.get_parameter('/myapp/database/url')
print(f"Value: {parameter['Parameter']['Value']}")

# Get parameters by path
parameters = ps_reader.get_parameters_by_path('/myapp/', recursive=True)
for param in parameters:
    print(f"Name: {param['Name']}, Value: {param['Value']}")

# Get parameter history
history = ps_reader.get_parameter_history('/myapp/database/url')
for version in history:
    print(f"Version: {version['Version']}, Modified: {version['LastModifiedDate']}")
```

#### Writing Parameter Store Resources
```python
from common.aws_client import AWSClientManager
from parameterstore.write.ps_writer import PSWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize Parameter Store writer
ps_writer = PSWriter(client_manager)

# Put parameter
ps_writer.put_parameter(
    name='/myapp/database/url',
    value='postgresql://localhost:5432/mydb',
    parameter_type='String',
    description='Database connection URL'
)

# Put secure parameter
ps_writer.put_parameter(
    name='/myapp/database/password',
    value='super-secret-password',
    parameter_type='SecureString',
    description='Database password',
    overwrite=True
)

# Delete parameter
ps_writer.delete_parameter('/myapp/old/config')
```

### SQS Operations

#### Reading SQS Resources
```python
from common.aws_client import AWSClientManager
from sqs.read.sqs_reader import SQSReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize SQS reader
sqs_reader = SQSReader(client_manager)

# List queues
queues = sqs_reader.list_queues()
for queue_url in queues:
    print(f"Queue: {queue_url}")

# Get queue attributes
attributes = sqs_reader.get_queue_attributes('my-queue')
print(f"Messages available: {attributes.get('ApproximateNumberOfMessages')}")

# Receive messages
messages = sqs_reader.receive_messages('my-queue', max_messages=10)
for message in messages:
    print(f"Message: {message['Body']}")
```

#### Writing SQS Resources
```python
from common.aws_client import AWSClientManager
from sqs.write.sqs_writer import SQSWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize SQS writer
sqs_writer = SQSWriter(client_manager)

# Create queue
queue_url = sqs_writer.create_queue(
    queue_name='my-new-queue',
    attributes={
        'VisibilityTimeoutSeconds': '300',
        'MessageRetentionPeriod': '1209600'
    }
)

# Send message
sqs_writer.send_message(
    queue_url=queue_url,
    message_body='Hello from SQS!',
    message_attributes={
        'Author': {'StringValue': 'Argus', 'DataType': 'String'}
    }
)

# Send batch of messages
messages = [
    {
        'Id': '1',
        'MessageBody': 'First message'
    },
    {
        'Id': '2',
        'MessageBody': 'Second message'
    }
]
sqs_writer.send_message_batch(queue_url, messages)

# Delete message
sqs_writer.delete_message(queue_url, receipt_handle)
```

### Elastic Beanstalk Operations

#### Reading Elastic Beanstalk Resources
```python
from common.aws_client import AWSClientManager
from ebs.read.ebs_reader import EBSReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EBS reader
ebs_reader = EBSReader(client_manager)

# List all applications
applications = ebs_reader.list_applications()
for app in applications:
    print(f"Application: {app['ApplicationName']}")

# Get specific application
app_details = ebs_reader.get_application('my-web-app')
print(f"Application ARN: {app_details['ApplicationArn']}")

# List environments for an application
environments = ebs_reader.list_environments('my-web-app')
for env in environments:
    print(f"Environment: {env['EnvironmentName']}, Status: {env['Status']}")

# Get environment health
health = ebs_reader.get_environment_health(environment_name='my-web-app-prod')
print(f"Health Status: {health['HealthStatus']}")

# List application versions
versions = ebs_reader.list_application_versions('my-web-app')
for version in versions:
    print(f"Version: {version['VersionLabel']}, Status: {version['Status']}")
```

#### Writing Elastic Beanstalk Resources
```python
from common.aws_client import AWSClientManager
from ebs.write.ebs_writer import EBSWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EBS writer
ebs_writer = EBSWriter(client_manager)

# Create a new application
application = ebs_writer.create_application(
    application_name='my-new-app',
    description='My new web application'
)

# Create application version
source_bundle = {
    'S3Bucket': 'my-app-bucket',
    'S3Key': 'app-v1.0.zip'
}
version = ebs_writer.create_application_version(
    application_name='my-new-app',
    version_label='v1.0',
    source_bundle=source_bundle,
    description='Initial version'
)

# Create environment
environment = ebs_writer.create_environment(
    application_name='my-new-app',
    environment_name='my-new-app-prod',
    solution_stack_name='64bit Amazon Linux 2 v5.8.0 running Node.js 18',
    version_label='v1.0',
    description='Production environment'
)

# Update environment with new version
ebs_writer.update_environment(
    environment_name='my-new-app-prod',
    version_label='v2.0'
)

# Terminate environment
ebs_writer.terminate_environment(environment_name='my-new-app-prod')
```

### EKS Operations

#### Reading EKS Resources
```python
from common.aws_client import AWSClientManager
from eks.read.eks_reader import EKSReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EKS reader
eks_reader = EKSReader(client_manager)

# List all clusters
clusters = eks_reader.list_clusters()
for cluster_name in clusters:
    print(f"Cluster: {cluster_name}")

# Get cluster details
cluster_details = eks_reader.describe_cluster('my-cluster')
if cluster_details:
    print(f"Status: {cluster_details['status']}")
    print(f"Version: {cluster_details['version']}")
    print(f"Endpoint: {cluster_details['endpoint']}")

# List node groups
nodegroups = eks_reader.list_nodegroups('my-cluster')
for ng in nodegroups:
    print(f"Node Group: {ng}")

# Get node group details
ng_details = eks_reader.describe_nodegroup('my-cluster', 'my-nodegroup')
if ng_details:
    print(f"Node Group Status: {ng_details['status']}")
    print(f"Instance Types: {ng_details['instanceTypes']}")

# List Fargate profiles
fargate_profiles = eks_reader.list_fargate_profiles('my-cluster')
for profile in fargate_profiles:
    print(f"Fargate Profile: {profile}")

# List add-ons
addons = eks_reader.list_addons('my-cluster')
for addon in addons:
    print(f"Add-on: {addon}")
```

#### Writing EKS Resources
```python
from common.aws_client import AWSClientManager
from eks.write.eks_writer import EKSWriter

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize EKS writer
eks_writer = EKSWriter(client_manager)

# Create a new cluster
vpc_config = {
    'subnetIds': ['subnet-12345', 'subnet-67890'],
    'endpointConfigAccess': {
        'privateAccess': True,
        'publicAccess': True
    }
}

cluster = eks_writer.create_cluster(
    name='my-new-cluster',
    version='1.28',
    role_arn='arn:aws:iam::123456789012:role/eks-service-role',
    resources_vpc_config=vpc_config,
    tags={'Environment': 'production'}
)

# Create a managed node group
scaling_config = {
    'minSize': 1,
    'maxSize': 5,
    'desiredSize': 2
}

nodegroup = eks_writer.create_nodegroup(
    cluster_name='my-new-cluster',
    nodegroup_name='my-nodegroup',
    subnets=['subnet-12345', 'subnet-67890'],
    node_role='arn:aws:iam::123456789012:role/NodeInstanceRole',
    scaling_config=scaling_config,
    instance_types=['t3.medium'],
    ami_type='AL2_x86_64'
)

# Create Fargate profile
selectors = [
    {
        'namespace': 'default',
        'labels': {'app': 'my-app'}
    }
]

fargate_profile = eks_writer.create_fargate_profile(
    fargate_profile_name='my-fargate-profile',
    cluster_name='my-new-cluster',
    pod_execution_role_arn='arn:aws:iam::123456789012:role/eks-fargate-profile',
    subnets=['subnet-12345', 'subnet-67890'],
    selectors=selectors
)

# Install an add-on
addon = eks_writer.create_addon(
    cluster_name='my-new-cluster',
    addon_name='vpc-cni',
    addon_version='v1.15.1-eksbuild.1',
    resolve_conflicts='OVERWRITE'
)

# Delete resources (cleanup)
eks_writer.delete_addon('my-new-cluster', 'vpc-cni')
eks_writer.delete_fargate_profile('my-new-cluster', 'my-fargate-profile')
eks_writer.delete_nodegroup('my-new-cluster', 'my-nodegroup')
eks_writer.delete_cluster('my-new-cluster')
```

### CloudWatch Operations

#### Reading CloudWatch Resources
```python
from common.aws_client import AWSClientManager
from cloudwatch.read.cloudwatch_reader import CloudWatchReader

# Initialize AWS client manager
client_manager = AWSClientManager('default', 'us-east-1')

# Initialize CloudWatch reader
cw_reader = CloudWatchReader(client_manager)

# List metrics
metrics = cw_reader.list_metrics(namespace='AWS/EC2')
for metric in metrics:
    print(f"Metric: {metric['MetricName']}")

# Get metric statistics
stats = cw_reader.get_metric_statistics(
    namespace='AWS/EC2',
    metric_name='CPUUtilization',
    dimensions=[
        {'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}
    ],
    start_time='2023-01-01T00:00:00Z',
    end_time='2023-01-02T00:00:00Z',
    period=3600,
    statistics=['Average', 'Maximum']
)

# List alarms
alarms = cw_reader.list_alarms()
for alarm in alarms:
    print(f"Alarm: {alarm['AlarmName']}, State: {alarm['StateValue']}")

# Get log groups
log_groups = cw_reader.list_log_groups()
for group in log_groups:
    print(f"Log Group: {group['logGroupName']}")
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

### AWSClientManager Pattern

All Argus modules use the consistent AWSClientManager pattern for initialization:

```python
from common.aws_client import AWSClientManager
from ecs.read.ecs_reader import ECSReader
from ecs.write.ecs_writer import ECSWriter

# Initialize client manager once
client_manager = AWSClientManager('default', 'us-east-1')

# Use with any service
ecs_reader = ECSReader(client_manager)
ecs_writer = ECSWriter(client_manager)
```

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
    buckets = s3_reader.list_buckets()
    all_buckets.extend(buckets)

print(f"Total buckets across all regions: {len(all_buckets)}")
```

## Available Services

### Currently Implemented ✅

The following AWS services are implemented with comprehensive read and write operations:

- **S3**: Complete read/write operations for buckets and objects
- **Lambda**: Complete read/write operations for functions, layers, and aliases  
- **ECS**: Complete read/write operations for clusters, services, and task definitions
- **EC2**: Complete read/write operations for instances, security groups, key pairs, and VPCs
- **Step Functions**: Complete state machine management and execution control
- **DynamoDB**: Complete table and item operations with advanced querying capabilities
- **EventBridge**: Complete event bus and rule management
- **Parameter Store**: Complete parameter management with hierarchical organization
- **SQS**: Complete queue and message operations
- **Elastic Beanstalk**: Complete application and environment lifecycle management
- **EKS**: Complete Kubernetes cluster and node group management
- **CloudWatch**: Read operations for metrics, logs, and alarms

### Key Features by Service

#### ECS
- **Cluster Management**: Full cluster lifecycle operations
- **Service Operations**: Create, update, and scale services
- **Task Management**: Complete task lifecycle management
- **Task Definitions**: Register and manage task definitions

#### EC2
- **Instance Management**: Launch, stop, start, reboot, and terminate instances
- **Security Groups**: Create, modify, and delete security groups and rules
- **Key Pair Management**: Create and delete SSH key pairs
- **VPC Operations**: List VPCs, subnets, and network resources
- **Tagging**: Add and remove tags from EC2 resources

#### Step Functions
- **State Machine Management**: Create, update, and delete state machines
- **Execution Control**: Start, stop, and monitor executions
- **Activity Support**: Manage Step Function activities
- **History Tracking**: Access detailed execution history

#### Parameter Store
- **Parameter Operations**: Full CRUD operations for parameters
- **Hierarchical Access**: Get parameters by path with filtering
- **Version Management**: Access parameter history and versions
- **Secure Parameters**: Support for SecureString parameter types

#### EventBridge
- **Event Bus Management**: Create and manage custom event buses
- **Rule Operations**: Complete rule lifecycle management
- **Target Management**: Add/remove targets for rules
- **Event Publishing**: Send custom events to event buses

#### DynamoDB
- **Table Operations**: Complete table lifecycle management
- **Item Operations**: Advanced CRUD with conditional operations
- **Query & Scan**: Optimized querying with pagination support
- **Index Management**: Global and local secondary index operations

#### SQS
- **Queue Management**: Full queue lifecycle operations
- **Message Operations**: Send, receive, and delete messages
- **Batch Operations**: Send and delete messages in batches
- **Queue Attributes**: Configure and manage queue settings

#### Elastic Beanstalk
- **Application Management**: Create, deploy, and manage applications
- **Environment Operations**: Full environment lifecycle including creation, updates, and termination
- **Version Control**: Manage application versions and deployments
- **Configuration Management**: Handle platform configurations and option settings
- **Health Monitoring**: Access environment health and resource information

#### EKS
- **Cluster Management**: Create, update, and delete Kubernetes clusters
- **Node Group Operations**: Manage managed node groups with scaling and configuration
- **Fargate Profiles**: Create and manage serverless Fargate profiles
- **Add-on Management**: Install, update, and manage EKS add-ons
- **Identity Provider Integration**: Configure OIDC identity providers

#### CloudWatch
- **Metrics Retrieval**: Get CloudWatch metrics with flexible filtering
- **Log Operations**: Access and search CloudWatch logs
- **Alarm Management**: Read CloudWatch alarms and their states
- **Dashboard Access**: Retrieve CloudWatch dashboard configurations

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
