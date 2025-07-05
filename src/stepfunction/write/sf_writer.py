"""
Step Functions Writer Module

This module provides functionality for creating and managing AWS Step Functions resources.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class StepFunctionWriter:
    """
    A class for creating and managing AWS Step Functions resources.
    
    This class provides methods to create, update, and delete state machines,
    executions, and activities.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the Step Functions writer.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.stepfunctions_client = self.client_manager.get_client('stepfunctions')
    
    def create_state_machine(self, name: str, definition: Dict[str, Any], 
                           role_arn: str, type_: str = 'STANDARD',
                           logging_configuration: Optional[Dict[str, Any]] = None,
                           tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new state machine.
        
        Args:
            name: Name of the state machine
            definition: State machine definition as a dictionary
            role_arn: ARN of the IAM role for the state machine
            type_: Type of state machine (STANDARD or EXPRESS)
            logging_configuration: Optional logging configuration
            tags: Resource tags
            
        Returns:
            State machine configuration
            
        Raises:
            AWSResourceError: If there's an error creating the state machine
        """
        try:
            logger.info("Creating Step Functions state machine: %s", name)
            
            kwargs = {
                'name': name,
                'definition': json.dumps(definition),
                'roleArn': role_arn,
                'type': type_
            }
            
            if logging_configuration:
                kwargs['loggingConfiguration'] = logging_configuration
            if tags:
                kwargs['tags'] = tags
            
            response = self.stepfunctions_client.create_state_machine(**kwargs)
            
            logger.info("Created Step Functions state machine: %s", name)
            return response
            
        except ClientError as e:
            error_message = f"Failed to create Step Functions state machine {name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def update_state_machine(self, state_machine_arn: str,
                           definition: Optional[Dict[str, Any]] = None,
                           role_arn: Optional[str] = None,
                           logging_configuration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update an existing state machine.
        
        Args:
            state_machine_arn: ARN of the state machine to update
            definition: New state machine definition
            role_arn: New IAM role ARN
            logging_configuration: New logging configuration
            
        Returns:
            Update response
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error updating the state machine
        """
        try:
            logger.info("Updating Step Functions state machine: %s", state_machine_arn)
            
            kwargs = {'stateMachineArn': state_machine_arn}
            
            if definition:
                kwargs['definition'] = json.dumps(definition)
            if role_arn:
                kwargs['roleArn'] = role_arn
            if logging_configuration:
                kwargs['loggingConfiguration'] = logging_configuration
            
            response = self.stepfunctions_client.update_state_machine(**kwargs)
            
            logger.info("Updated Step Functions state machine: %s", state_machine_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to update state machine {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def delete_state_machine(self, state_machine_arn: str) -> Dict[str, Any]:
        """
        Delete a state machine.
        
        Args:
            state_machine_arn: ARN of the state machine to delete
            
        Returns:
            Delete response
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error deleting the state machine
        """
        try:
            logger.info("Deleting Step Functions state machine: %s", state_machine_arn)
            
            response = self.stepfunctions_client.delete_state_machine(
                stateMachineArn=state_machine_arn
            )
            
            logger.info("Deleted Step Functions state machine: %s", state_machine_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete state machine {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def start_execution(self, state_machine_arn: str, name: Optional[str] = None,
                       input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start execution of a state machine.
        
        Args:
            state_machine_arn: ARN of the state machine to execute
            name: Optional name for the execution
            input_data: Optional input data for the execution
            
        Returns:
            Execution response
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error starting the execution
        """
        try:
            logger.info("Starting execution for state machine: %s", state_machine_arn)
            
            kwargs = {'stateMachineArn': state_machine_arn}
            
            if name:
                kwargs['name'] = name
            if input_data:
                kwargs['input'] = json.dumps(input_data)
            
            response = self.stepfunctions_client.start_execution(**kwargs)
            
            logger.info("Started execution: %s", response.get('executionArn'))
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to start execution for {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def stop_execution(self, execution_arn: str, error: Optional[str] = None,
                      cause: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop execution of a state machine.
        
        Args:
            execution_arn: ARN of the execution to stop
            error: Optional error code
            cause: Optional cause description
            
        Returns:
            Stop response
            
        Raises:
            ResourceNotFoundError: If the execution doesn't exist
            AWSResourceError: If there's an error stopping the execution
        """
        try:
            logger.info("Stopping execution: %s", execution_arn)
            
            kwargs = {'executionArn': execution_arn}
            
            if error:
                kwargs['error'] = error
            if cause:
                kwargs['cause'] = cause
            
            response = self.stepfunctions_client.stop_execution(**kwargs)
            
            logger.info("Stopped execution: %s", execution_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ExecutionDoesNotExist':
                error_message = f"Step Functions execution not found: {execution_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to stop execution {execution_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def create_activity(self, name: str, tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Create a new activity.
        
        Args:
            name: Name of the activity
            tags: Resource tags
            
        Returns:
            Activity configuration
            
        Raises:
            AWSResourceError: If there's an error creating the activity
        """
        try:
            logger.info("Creating Step Functions activity: %s", name)
            
            kwargs = {'name': name}
            if tags:
                kwargs['tags'] = tags
            
            response = self.stepfunctions_client.create_activity(**kwargs)
            
            logger.info("Created Step Functions activity: %s", name)
            return response
            
        except ClientError as e:
            error_message = f"Failed to create Step Functions activity {name}: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def delete_activity(self, activity_arn: str) -> Dict[str, Any]:
        """
        Delete an activity.
        
        Args:
            activity_arn: ARN of the activity to delete
            
        Returns:
            Delete response
            
        Raises:
            ResourceNotFoundError: If the activity doesn't exist
            AWSResourceError: If there's an error deleting the activity
        """
        try:
            logger.info("Deleting Step Functions activity: %s", activity_arn)
            
            response = self.stepfunctions_client.delete_activity(
                activityArn=activity_arn
            )
            
            logger.info("Deleted Step Functions activity: %s", activity_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ActivityDoesNotExist':
                error_message = f"Step Functions activity not found: {activity_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to delete activity {activity_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def send_task_success(self, task_token: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send task success for an activity task.
        
        Args:
            task_token: Task token received from the activity
            output: Output data from the task
            
        Returns:
            Success response
            
        Raises:
            AWSResourceError: If there's an error sending task success
        """
        try:
            logger.info("Sending task success for token: %s", task_token[:20] + "...")
            
            response = self.stepfunctions_client.send_task_success(
                taskToken=task_token,
                output=json.dumps(output)
            )
            
            logger.info("Sent task success")
            return response
            
        except ClientError as e:
            error_message = f"Failed to send task success: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def send_task_failure(self, task_token: str, error: Optional[str] = None,
                         cause: Optional[str] = None) -> Dict[str, Any]:
        """
        Send task failure for an activity task.
        
        Args:
            task_token: Task token received from the activity
            error: Optional error code
            cause: Optional cause description
            
        Returns:
            Failure response
            
        Raises:
            AWSResourceError: If there's an error sending task failure
        """
        try:
            logger.info("Sending task failure for token: %s", task_token[:20] + "...")
            
            kwargs = {'taskToken': task_token}
            if error:
                kwargs['error'] = error
            if cause:
                kwargs['cause'] = cause
            
            response = self.stepfunctions_client.send_task_failure(**kwargs)
            
            logger.info("Sent task failure")
            return response
            
        except ClientError as e:
            error_message = f"Failed to send task failure: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def send_task_heartbeat(self, task_token: str) -> Dict[str, Any]:
        """
        Send task heartbeat for an activity task.
        
        Args:
            task_token: Task token received from the activity
            
        Returns:
            Heartbeat response
            
        Raises:
            AWSResourceError: If there's an error sending task heartbeat
        """
        try:
            logger.info("Sending task heartbeat for token: %s", task_token[:20] + "...")
            
            response = self.stepfunctions_client.send_task_heartbeat(
                taskToken=task_token
            )
            
            logger.info("Sent task heartbeat")
            return response
            
        except ClientError as e:
            error_message = f"Failed to send task heartbeat: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
