"""
CloudWatch Reader - Read operations for Amazon CloudWatch resources.

This module provides methods to read and query CloudWatch logs, metrics,
and alarms. Write operations are not supported for CloudWatch.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from common.aws_client import AWSClientManager
from common.exceptions import AWSResourceError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class CloudWatchReader:
    """CloudWatch read operations using boto3."""
    
    def __init__(self, client_manager: AWSClientManager):
        """
        Initialize CloudWatchReader.
        
        Args:
            client_manager: AWSClientManager instance for AWS service clients
        """
        self.client_manager = client_manager
        self.cloudwatch_client = client_manager.get_client('cloudwatch')
        self.logs_client = client_manager.get_client('logs')
        logger.info("CloudWatchReader initialized successfully")
    
    def list_log_groups(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List CloudWatch log groups with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter log groups
            limit: Optional maximum number of log groups to return
            
        Returns:
            List of log group dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing log groups
        """
        try:
            logger.info(f"Listing log groups{f' with prefix {prefix}' if prefix else ''}")
            
            kwargs = {}
            if prefix:
                kwargs['logGroupNamePrefix'] = prefix
            if limit:
                kwargs['limit'] = limit
            
            response = self.logs_client.describe_log_groups(**kwargs)
            log_groups = response.get('logGroups', [])
            
            logger.info(f"Found {len(log_groups)} log groups")
            return log_groups
            
        except Exception as e:
            logger.error(f"Error listing log groups: {e}")
            raise AWSResourceError(f"Failed to list log groups: {e}")
    
    def list_log_streams(self, log_group_name: str, prefix: Optional[str] = None, 
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List log streams in a specific log group.
        
        Args:
            log_group_name: Name of the log group
            prefix: Optional prefix to filter log streams
            limit: Optional maximum number of log streams to return
            
        Returns:
            List of log stream dictionaries
            
        Raises:
            ResourceNotFoundError: If the log group is not found
            AWSResourceError: If there's an error listing log streams
        """
        try:
            logger.info(f"Listing log streams for group: {log_group_name}")
            
            kwargs = {'logGroupName': log_group_name}
            if prefix:
                kwargs['logStreamNamePrefix'] = prefix
            if limit:
                kwargs['limit'] = limit
            
            response = self.logs_client.describe_log_streams(**kwargs)
            log_streams = response.get('logStreams', [])
            
            logger.info(f"Found {len(log_streams)} log streams")
            return log_streams
            
        except self.logs_client.exceptions.ResourceNotFoundException:
            raise ResourceNotFoundError(f"Log group not found: {log_group_name}")
        except Exception as e:
            logger.error(f"Error listing log streams for {log_group_name}: {e}")
            raise AWSResourceError(f"Failed to list log streams for {log_group_name}: {e}")
    
    def get_log_events(self, log_group_name: str, log_stream_name: str,
                      start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                      limit: Optional[int] = None, start_from_head: bool = False) -> List[Dict[str, Any]]:
        """
        Get log events from a specific log stream.
        
        Args:
            log_group_name: Name of the log group
            log_stream_name: Name of the log stream
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            limit: Optional maximum number of events to return
            start_from_head: Whether to start from the beginning of the stream
            
        Returns:
            List of log event dictionaries
            
        Raises:
            ResourceNotFoundError: If the log group or stream is not found
            AWSResourceError: If there's an error getting log events
        """
        try:
            logger.info(f"Getting log events from {log_group_name}/{log_stream_name}")
            
            kwargs = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'startFromHead': start_from_head
            }
            
            if start_time:
                kwargs['startTime'] = int(start_time.timestamp() * 1000)
            if end_time:
                kwargs['endTime'] = int(end_time.timestamp() * 1000)
            if limit:
                kwargs['limit'] = limit
            
            response = self.logs_client.get_log_events(**kwargs)
            events = response.get('events', [])
            
            logger.info(f"Retrieved {len(events)} log events")
            return events
            
        except self.logs_client.exceptions.ResourceNotFoundException as e:
            if 'log group' in str(e).lower():
                raise ResourceNotFoundError(f"Log group not found: {log_group_name}")
            else:
                raise ResourceNotFoundError(f"Log stream not found: {log_stream_name}")
        except Exception as e:
            logger.error(f"Error getting log events: {e}")
            raise AWSResourceError(f"Failed to get log events: {e}")
    
    def filter_log_events(self, log_group_name: str, filter_pattern: Optional[str] = None,
                         start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                         log_stream_names: Optional[List[str]] = None,
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Filter log events across log streams in a log group.
        
        Args:
            log_group_name: Name of the log group
            filter_pattern: Optional filter pattern to match against log events
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            log_stream_names: Optional list of specific log streams to search
            limit: Optional maximum number of events to return
            
        Returns:
            List of filtered log event dictionaries
            
        Raises:
            ResourceNotFoundError: If the log group is not found
            AWSResourceError: If there's an error filtering log events
        """
        try:
            logger.info(f"Filtering log events in {log_group_name}")
            
            kwargs = {'logGroupName': log_group_name}
            
            if filter_pattern:
                kwargs['filterPattern'] = filter_pattern
            if start_time:
                kwargs['startTime'] = int(start_time.timestamp() * 1000)
            if end_time:
                kwargs['endTime'] = int(end_time.timestamp() * 1000)
            if log_stream_names:
                kwargs['logStreamNames'] = log_stream_names
            if limit:
                kwargs['limit'] = limit
            
            response = self.logs_client.filter_log_events(**kwargs)
            events = response.get('events', [])
            
            logger.info(f"Found {len(events)} matching log events")
            return events
            
        except self.logs_client.exceptions.ResourceNotFoundException:
            raise ResourceNotFoundError(f"Log group not found: {log_group_name}")
        except Exception as e:
            logger.error(f"Error filtering log events: {e}")
            raise AWSResourceError(f"Failed to filter log events: {e}")
    
    def search_log_events(self, log_group_name: str, search_term: str,
                         hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Search for log events containing a specific term.
        
        Args:
            log_group_name: Name of the log group to search
            search_term: Term to search for in log messages
            hours_back: Number of hours back to search (default: 24)
            
        Returns:
            List of matching log event dictionaries
            
        Raises:
            ResourceNotFoundError: If the log group is not found
            AWSResourceError: If there's an error searching log events
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            logger.info(f"Searching for '{search_term}' in {log_group_name}")
            
            return self.filter_log_events(
                log_group_name=log_group_name,
                filter_pattern=search_term,
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            logger.error(f"Error searching log events: {e}")
            raise AWSResourceError(f"Failed to search log events: {e}")
    
    def get_recent_logs(self, log_group_name: str, minutes_back: int = 60,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent log events from a log group.
        
        Args:
            log_group_name: Name of the log group
            minutes_back: Number of minutes back to retrieve logs (default: 60)
            limit: Optional maximum number of events to return
            
        Returns:
            List of recent log event dictionaries
            
        Raises:
            ResourceNotFoundError: If the log group is not found
            AWSResourceError: If there's an error getting recent logs
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            logger.info(f"Getting recent logs from {log_group_name}")
            
            return self.filter_log_events(
                log_group_name=log_group_name,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            raise AWSResourceError(f"Failed to get recent logs: {e}")
    
    def list_metrics(self, namespace: Optional[str] = None, metric_name: Optional[str] = None,
                    dimensions: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        """
        List CloudWatch metrics with optional filters.
        
        Args:
            namespace: Optional namespace to filter metrics
            metric_name: Optional metric name to filter
            dimensions: Optional list of dimension filters
            
        Returns:
            List of metric dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing metrics
        """
        try:
            logger.info("Listing CloudWatch metrics")
            
            kwargs = {}
            if namespace:
                kwargs['Namespace'] = namespace
            if metric_name:
                kwargs['MetricName'] = metric_name
            if dimensions:
                kwargs['Dimensions'] = dimensions
            
            response = self.cloudwatch_client.list_metrics(**kwargs)
            metrics = response.get('Metrics', [])
            
            logger.info(f"Found {len(metrics)} metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error listing metrics: {e}")
            raise AWSResourceError(f"Failed to list metrics: {e}")
    
    def get_metric_statistics(self, namespace: str, metric_name: str,
                             dimensions: List[Dict[str, str]], start_time: datetime,
                             end_time: datetime, period: int, statistics: List[str]) -> Dict[str, Any]:
        """
        Get statistics for a specific CloudWatch metric.
        
        Args:
            namespace: Metric namespace
            metric_name: Name of the metric
            dimensions: List of metric dimensions
            start_time: Start time for the statistics
            end_time: End time for the statistics
            period: Period in seconds for aggregation
            statistics: List of statistics to retrieve (e.g., ['Average', 'Maximum'])
            
        Returns:
            Dictionary containing metric statistics
            
        Raises:
            AWSResourceError: If there's an error getting metric statistics
        """
        try:
            logger.info(f"Getting statistics for metric {namespace}/{metric_name}")
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics
            )
            
            logger.info(f"Retrieved {len(response.get('Datapoints', []))} datapoints")
            return response
            
        except Exception as e:
            logger.error(f"Error getting metric statistics: {e}")
            raise AWSResourceError(f"Failed to get metric statistics: {e}")
    
    def list_alarms(self, alarm_names: Optional[List[str]] = None,
                   alarm_name_prefix: Optional[str] = None,
                   state_value: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List CloudWatch alarms with optional filters.
        
        Args:
            alarm_names: Optional list of specific alarm names
            alarm_name_prefix: Optional prefix to filter alarm names
            state_value: Optional alarm state to filter by (OK, ALARM, INSUFFICIENT_DATA)
            
        Returns:
            List of alarm dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing alarms
        """
        try:
            logger.info("Listing CloudWatch alarms")
            
            kwargs = {}
            if alarm_names:
                kwargs['AlarmNames'] = alarm_names
            if alarm_name_prefix:
                kwargs['AlarmNamePrefix'] = alarm_name_prefix
            if state_value:
                kwargs['StateValue'] = state_value
            
            response = self.cloudwatch_client.describe_alarms(**kwargs)
            alarms = response.get('MetricAlarms', [])
            
            logger.info(f"Found {len(alarms)} alarms")
            return alarms
            
        except Exception as e:
            logger.error(f"Error listing alarms: {e}")
            raise AWSResourceError(f"Failed to list alarms: {e}")
    
    def get_alarm_history(self, alarm_name: str, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         history_item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get history for a specific CloudWatch alarm.
        
        Args:
            alarm_name: Name of the alarm
            start_date: Optional start date for history
            end_date: Optional end date for history
            history_item_type: Optional type of history items to retrieve
            
        Returns:
            List of alarm history items
            
        Raises:
            AWSResourceError: If there's an error getting alarm history
        """
        try:
            logger.info(f"Getting history for alarm: {alarm_name}")
            
            kwargs = {'AlarmName': alarm_name}
            if start_date:
                kwargs['StartDate'] = start_date
            if end_date:
                kwargs['EndDate'] = end_date
            if history_item_type:
                kwargs['HistoryItemType'] = history_item_type
            
            response = self.cloudwatch_client.describe_alarm_history(**kwargs)
            history_items = response.get('AlarmHistoryItems', [])
            
            logger.info(f"Found {len(history_items)} history items")
            return history_items
            
        except Exception as e:
            logger.error(f"Error getting alarm history: {e}")
            raise AWSResourceError(f"Failed to get alarm history: {e}")
    
    def get_dashboard_list(self, dashboard_name_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List CloudWatch dashboards.
        
        Args:
            dashboard_name_prefix: Optional prefix to filter dashboard names
            
        Returns:
            List of dashboard dictionaries
            
        Raises:
            AWSResourceError: If there's an error listing dashboards
        """
        try:
            logger.info("Listing CloudWatch dashboards")
            
            kwargs = {}
            if dashboard_name_prefix:
                kwargs['DashboardNamePrefix'] = dashboard_name_prefix
            
            response = self.cloudwatch_client.list_dashboards(**kwargs)
            dashboards = response.get('DashboardEntries', [])
            
            logger.info(f"Found {len(dashboards)} dashboards")
            return dashboards
            
        except Exception as e:
            logger.error(f"Error listing dashboards: {e}")
            raise AWSResourceError(f"Failed to list dashboards: {e}")
    
    def get_dashboard(self, dashboard_name: str) -> Dict[str, Any]:
        """
        Get details for a specific CloudWatch dashboard.
        
        Args:
            dashboard_name: Name of the dashboard
            
        Returns:
            Dictionary containing dashboard details
            
        Raises:
            ResourceNotFoundError: If the dashboard is not found
            AWSResourceError: If there's an error getting the dashboard
        """
        try:
            logger.info(f"Getting dashboard: {dashboard_name}")
            
            response = self.cloudwatch_client.get_dashboard(DashboardName=dashboard_name)
            
            logger.info(f"Successfully retrieved dashboard: {dashboard_name}")
            return response
            
        except self.cloudwatch_client.exceptions.ResourceNotFound:
            raise ResourceNotFoundError(f"Dashboard not found: {dashboard_name}")
        except Exception as e:
            logger.error(f"Error getting dashboard {dashboard_name}: {e}")
            raise AWSResourceError(f"Failed to get dashboard {dashboard_name}: {e}")
