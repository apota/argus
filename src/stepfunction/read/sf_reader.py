"""
Step Functions Reader Module

This module provides functionality for reading and exploring AWS Step Functions resources.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from ...common.aws_client import AWSClientManager
from ...common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class StepFunctionReader:
    """
    A class for reading AWS Step Functions resources.
    
    This class provides methods to list and retrieve information about
    state machines, executions, and activities.
    """
    
    def __init__(self, profile_name: str = 'default', region_name: str = 'us-east-1'):
        """
        Initialize the Step Functions reader.
        
        Args:
            profile_name: AWS profile name to use for authentication
            region_name: AWS region name
        """
        self.client_manager = AWSClientManager(profile_name, region_name)
        self.stepfunctions_client = self.client_manager.get_client('stepfunctions')
    
    def list_state_machines(self, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all state machines in the account.
        
        Args:
            max_results: Maximum number of state machines to return
            
        Returns:
            List of state machine configurations
            
        Raises:
            AWSResourceError: If there's an error listing state machines
        """
        try:
            logger.info("Listing Step Functions state machines")
            
            kwargs = {}
            if max_results:
                kwargs['maxResults'] = max_results
            
            paginator = self.stepfunctions_client.get_paginator('list_state_machines')
            page_iterator = paginator.paginate(
                PaginationConfig={'MaxItems': max_results} if max_results else {}
            )
            
            state_machines = []
            for page in page_iterator:
                state_machines.extend(page.get('stateMachines', []))
            
            logger.info("Found %d Step Functions state machines", len(state_machines))
            return state_machines
            
        except ClientError as e:
            error_message = f"Failed to list Step Functions state machines: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_state_machine(self, state_machine_arn: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific state machine.
        
        Args:
            state_machine_arn: ARN of the state machine
            
        Returns:
            State machine configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error retrieving the state machine
        """
        try:
            logger.info("Describing Step Functions state machine: %s", state_machine_arn)
            
            response = self.stepfunctions_client.describe_state_machine(
                stateMachineArn=state_machine_arn
            )
            
            logger.info("Retrieved state machine information for %s", state_machine_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe state machine {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_state_machine_definition(self, state_machine_arn: str) -> Dict[str, Any]:
        """
        Get the definition of a state machine.
        
        Args:
            state_machine_arn: ARN of the state machine
            
        Returns:
            State machine definition as a parsed JSON object
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error retrieving the definition
        """
        try:
            logger.info("Getting state machine definition: %s", state_machine_arn)
            
            response = self.stepfunctions_client.describe_state_machine(
                stateMachineArn=state_machine_arn
            )
            
            # Parse the definition JSON string
            definition_json = response.get('definition', '{}')
            definition = json.loads(definition_json)
            
            logger.info("Retrieved state machine definition for %s", state_machine_arn)
            return definition
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get state machine definition {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse state machine definition JSON: {e}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def list_executions(self, state_machine_arn: str, 
                       status_filter: Optional[str] = None,
                       max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List executions for a state machine.
        
        Args:
            state_machine_arn: ARN of the state machine
            status_filter: Optional status filter (RUNNING, SUCCEEDED, FAILED, TIMED_OUT, ABORTED)
            max_results: Maximum number of executions to return
            
        Returns:
            List of execution configurations
            
        Raises:
            ResourceNotFoundError: If the state machine doesn't exist
            AWSResourceError: If there's an error listing executions
        """
        try:
            logger.info("Listing executions for state machine: %s", state_machine_arn)
            
            kwargs = {'stateMachineArn': state_machine_arn}
            if status_filter:
                kwargs['statusFilter'] = status_filter
            if max_results:
                kwargs['maxResults'] = max_results
            
            paginator = self.stepfunctions_client.get_paginator('list_executions')
            page_iterator = paginator.paginate(**kwargs)
            
            executions = []
            for page in page_iterator:
                executions.extend(page.get('executions', []))
            
            logger.info("Found %d executions for state machine", len(executions))
            return executions
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'StateMachineDoesNotExist':
                error_message = f"Step Functions state machine not found: {state_machine_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to list executions for {state_machine_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def describe_execution(self, execution_arn: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific execution.
        
        Args:
            execution_arn: ARN of the execution
            
        Returns:
            Execution configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the execution doesn't exist
            AWSResourceError: If there's an error retrieving the execution
        """
        try:
            logger.info("Describing execution: %s", execution_arn)
            
            response = self.stepfunctions_client.describe_execution(
                executionArn=execution_arn
            )
            
            logger.info("Retrieved execution information for %s", execution_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ExecutionDoesNotExist':
                error_message = f"Step Functions execution not found: {execution_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe execution {execution_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def get_execution_history(self, execution_arn: str, 
                             reverse_order: bool = False,
                             include_execution_data: bool = False,
                             max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the execution history for a specific execution.
        
        Args:
            execution_arn: ARN of the execution
            reverse_order: Whether to return events in reverse chronological order
            include_execution_data: Whether to include input/output data in the response
            max_results: Maximum number of events to return
            
        Returns:
            List of execution history events
            
        Raises:
            ResourceNotFoundError: If the execution doesn't exist
            AWSResourceError: If there's an error retrieving the execution history
        """
        try:
            logger.info("Getting execution history for: %s", execution_arn)
            
            kwargs = {
                'executionArn': execution_arn,
                'reverseOrder': reverse_order,
                'includeExecutionData': include_execution_data
            }
            if max_results:
                kwargs['maxResults'] = max_results
            
            paginator = self.stepfunctions_client.get_paginator('get_execution_history')
            page_iterator = paginator.paginate(**kwargs)
            
            events = []
            for page in page_iterator:
                events.extend(page.get('events', []))
            
            logger.info("Found %d execution history events", len(events))
            return events
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ExecutionDoesNotExist':
                error_message = f"Step Functions execution not found: {execution_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to get execution history for {execution_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
    
    def list_activities(self, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all activities in the account.
        
        Args:
            max_results: Maximum number of activities to return
            
        Returns:
            List of activity configurations
            
        Raises:
            AWSResourceError: If there's an error listing activities
        """
        try:
            logger.info("Listing Step Functions activities")
            
            kwargs = {}
            if max_results:
                kwargs['maxResults'] = max_results
            
            paginator = self.stepfunctions_client.get_paginator('list_activities')
            page_iterator = paginator.paginate(
                PaginationConfig={'MaxItems': max_results} if max_results else {}
            )
            
            activities = []
            for page in page_iterator:
                activities.extend(page.get('activities', []))
            
            logger.info("Found %d Step Functions activities", len(activities))
            return activities
            
        except ClientError as e:
            error_message = f"Failed to list Step Functions activities: {e.response['Error']['Message']}"
            logger.error(error_message)
            raise AWSResourceError(error_message) from e
    
    def describe_activity(self, activity_arn: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific activity.
        
        Args:
            activity_arn: ARN of the activity
            
        Returns:
            Activity configuration and metadata
            
        Raises:
            ResourceNotFoundError: If the activity doesn't exist
            AWSResourceError: If there's an error retrieving the activity
        """
        try:
            logger.info("Describing activity: %s", activity_arn)
            
            response = self.stepfunctions_client.describe_activity(
                activityArn=activity_arn
            )
            
            logger.info("Retrieved activity information for %s", activity_arn)
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ActivityDoesNotExist':
                error_message = f"Step Functions activity not found: {activity_arn}"
                logger.error(error_message)
                raise ResourceNotFoundError(error_message) from e
            else:
                error_message = f"Failed to describe activity {activity_arn}: {e.response['Error']['Message']}"
                logger.error(error_message)
                raise AWSResourceError(error_message) from e
