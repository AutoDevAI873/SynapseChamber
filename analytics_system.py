import os
import logging
import json
import datetime
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict, Counter

class AnalyticsSystem:
    """
    Advanced analytics system for Synapse Chamber
    
    Tracks system performance, training metrics, AI platform metrics,
    and generates visualizations for the dashboard
    """
    
    def __init__(self, memory_system, performance_monitor=None):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.analytics_dir = "data/analytics"
        self.metrics = {}
        self.last_metrics_update = None
        self.performance_monitor = performance_monitor
        
        # Ensure analytics directory exists
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        # Initialize metrics storage
        self._init_metrics()
        
        # Start performance monitoring if monitor is provided
        if self.performance_monitor and not self.performance_monitor.monitoring:
            try:
                self.performance_monitor.start_monitoring()
                self.logger.info("Started performance monitoring")
            except Exception as e:
                self.logger.error(f"Failed to start performance monitoring: {str(e)}")
        
    def _init_metrics(self):
        """Initialize metrics structure"""
        self.metrics = {
            'system_performance': {
                'memory_usage': [],
                'response_times': [],
                'api_latency': [],
                'error_rates': [],
                'uptime': []
            },
            'training_metrics': {
                'sessions_total': 0,
                'sessions_completed': 0,
                'sessions_failed': 0,
                'topics': Counter(),
                'platforms': Counter(),
                'success_rate': 0,
                'avg_session_duration': 0,
                'session_history': []
            },
            'platform_metrics': {
                'platform_success_rates': {},
                'platform_response_times': {},
                'platform_usage': {},
                'platform_contribution_quality': {}
            },
            'user_engagement': {
                'active_days': [],
                'session_frequency': [],
                'feature_usage': Counter(),
                'interaction_patterns': []
            },
            'last_updated': datetime.datetime.now().isoformat()
        }
        
        # Load existing metrics if available
        metrics_path = os.path.join(self.analytics_dir, 'metrics.json')
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    saved_metrics = json.load(f)
                    # Update only existing keys to maintain structure
                    self._update_nested_dict(self.metrics, saved_metrics)
                    
                self.logger.info("Loaded existing analytics metrics")
            except Exception as e:
                self.logger.error(f"Error loading analytics metrics: {str(e)}")
    
    def _update_nested_dict(self, d, u):
        """Update nested dictionary with another dictionary's values"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def _save_metrics(self):
        """Save metrics to file"""
        metrics_path = os.path.join(self.analytics_dir, 'metrics.json')
        try:
            # Update timestamp
            self.metrics['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving analytics metrics: {str(e)}")
            return False
    
    def update_metrics(self, force=False):
        """
        Update all metrics from data sources
        
        Args:
            force (bool): Force update even if recently updated
        
        Returns:
            bool: Success status
        """
        # Check if metrics were recently updated (within last 5 minutes)
        now = datetime.datetime.now()
        if not force and self.last_metrics_update and (now - self.last_metrics_update).total_seconds() < 300:
            self.logger.info("Metrics recently updated, skipping...")
            return True
            
        try:
            # Update system performance metrics
            self._update_system_performance()
            
            # Update training metrics from threads
            self._update_training_metrics()
            
            # Update platform metrics
            self._update_platform_metrics()
            
            # Update user engagement metrics
            self._update_user_engagement()
            
            # Save updated metrics
            self._save_metrics()
            
            self.last_metrics_update = now
            self.logger.info("Analytics metrics updated successfully")
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating analytics metrics: {str(e)}")
            return False
    
    def _update_system_performance(self):
        """Update system performance metrics"""
        # If we have an integrated performance monitor, use its data
        if hasattr(self, 'performance_monitor') and self.performance_monitor:
            try:
                # Get current metrics from the performance monitor
                current_metrics = self.performance_monitor.get_current_metrics()
                timestamp = datetime.datetime.now().isoformat()
                
                # Update memory usage from real data
                if 'memory' in current_metrics and 'usage_percent' in current_metrics['memory']:
                    mem_usage = {'timestamp': timestamp, 'value': current_metrics['memory']['usage_percent']}
                    self.metrics['system_performance']['memory_usage'].append(mem_usage)
                else:
                    # Fallback to simulated data
                    mem_usage = {'timestamp': timestamp, 'value': np.random.uniform(30, 80)}
                    self.metrics['system_performance']['memory_usage'].append(mem_usage)
                
                # Update API latency (we don't have direct API latency in performance monitor, use simulated)
                api_latency = {'timestamp': timestamp, 'value': np.random.uniform(50, 500)}
                self.metrics['system_performance']['api_latency'].append(api_latency)
                
                # Update error rate (using network errors or disk errors as proxy if available)
                if 'network' in current_metrics and 'errors' in current_metrics['network']:
                    error_value = current_metrics['network']['errors']
                    error_rate = {'timestamp': timestamp, 'value': min(5.0, error_value)}  # Cap at 5%
                else:
                    # Fallback to simulated data
                    error_rate = {'timestamp': timestamp, 'value': np.random.uniform(0, 5)}
                
                self.metrics['system_performance']['error_rates'].append(error_rate)
                
                # Add response times if available
                if 'network' in current_metrics and 'bytes_recv' in current_metrics['network']:
                    response_time = {'timestamp': timestamp, 'value': current_metrics['network']['bytes_recv'] / 1024}  # KB
                    if 'response_times' in self.metrics['system_performance']:
                        self.metrics['system_performance']['response_times'].append(response_time)
                
                # Add CPU usage
                if 'cpu' in current_metrics and 'usage_percent' in current_metrics['cpu']:
                    cpu_usage = {'timestamp': timestamp, 'value': current_metrics['cpu']['usage_percent']}
                    if 'cpu_usage' not in self.metrics['system_performance']:
                        self.metrics['system_performance']['cpu_usage'] = []
                    self.metrics['system_performance']['cpu_usage'].append(cpu_usage)
                
                # Add disk usage
                if 'disk' in current_metrics and 'usage_percent' in current_metrics['disk']:
                    disk_usage = {'timestamp': timestamp, 'value': current_metrics['disk']['usage_percent']}
                    if 'disk_usage' not in self.metrics['system_performance']:
                        self.metrics['system_performance']['disk_usage'] = []
                    self.metrics['system_performance']['disk_usage'].append(disk_usage)
                
                self.logger.debug("Updated system performance metrics from performance monitor")
                
            except Exception as e:
                self.logger.error(f"Error getting metrics from performance monitor: {str(e)}")
                # Fall back to simulated data in case of error
                self._update_system_performance_simulated()
        else:
            # No performance monitor, use simulated data
            self._update_system_performance_simulated()
    
    def _update_system_performance_simulated(self):
        """Update system performance metrics with simulated data"""
        # Record memory usage (simulated)
        mem_usage = {'timestamp': datetime.datetime.now().isoformat(), 'value': np.random.uniform(30, 80)}
        self.metrics['system_performance']['memory_usage'].append(mem_usage)
        
        # Limit history length
        if len(self.metrics['system_performance']['memory_usage']) > 1000:
            self.metrics['system_performance']['memory_usage'] = self.metrics['system_performance']['memory_usage'][-1000:]
        
        # Record API latency (simulated)
        api_latency = {'timestamp': datetime.datetime.now().isoformat(), 'value': np.random.uniform(50, 500)}
        self.metrics['system_performance']['api_latency'].append(api_latency)
        
        # Limit history length
        if len(self.metrics['system_performance']['api_latency']) > 1000:
            self.metrics['system_performance']['api_latency'] = self.metrics['system_performance']['api_latency'][-1000:]
        
        # Record error rate (simulated)
        error_rate = {'timestamp': datetime.datetime.now().isoformat(), 'value': np.random.uniform(0, 5)}
        self.metrics['system_performance']['error_rates'].append(error_rate)
        
        # Limit history length
        if len(self.metrics['system_performance']['error_rates']) > 1000:
            self.metrics['system_performance']['error_rates'] = self.metrics['system_performance']['error_rates'][-1000:]
        
        # Add CPU usage if not present
        if 'cpu_usage' not in self.metrics['system_performance']:
            self.metrics['system_performance']['cpu_usage'] = []
        
        cpu_usage = {'timestamp': datetime.datetime.now().isoformat(), 'value': np.random.uniform(10, 90)}
        self.metrics['system_performance']['cpu_usage'].append(cpu_usage)
        
        # Limit history length
        if len(self.metrics['system_performance']['cpu_usage']) > 1000:
            self.metrics['system_performance']['cpu_usage'] = self.metrics['system_performance']['cpu_usage'][-1000:]
            
        # Add disk usage if not present
        if 'disk_usage' not in self.metrics['system_performance']:
            self.metrics['system_performance']['disk_usage'] = []
        
        disk_usage = {'timestamp': datetime.datetime.now().isoformat(), 'value': np.random.uniform(30, 70)}
        self.metrics['system_performance']['disk_usage'].append(disk_usage)
        
        # Limit history length
        if len(self.metrics['system_performance']['disk_usage']) > 1000:
            self.metrics['system_performance']['disk_usage'] = self.metrics['system_performance']['disk_usage'][-1000:]
    
    def _update_training_metrics(self):
        """Update training metrics from thread data"""
        try:
            # Get all training threads
            threads = self.memory_system.get_threads(limit=100)
            if not threads:
                return
            
            # Count totals
            total_threads = len(threads)
            completed_threads = sum(1 for t in threads if t.get('final_plan'))
            failed_threads = sum(1 for t in threads if not t.get('final_plan') and t.get('status') == 'failed')
            
            # Update overall metrics
            self.metrics['training_metrics']['sessions_total'] = total_threads
            self.metrics['training_metrics']['sessions_completed'] = completed_threads
            self.metrics['training_metrics']['sessions_failed'] = failed_threads
            
            # Calculate success rate
            if total_threads > 0:
                self.metrics['training_metrics']['success_rate'] = completed_threads / total_threads
            
            # Update topic metrics
            topic_counter = Counter()
            for thread in threads:
                subject = thread.get('subject', '')
                if subject:
                    # Extract the main topic from the subject (remove "Training: " prefix if exists)
                    if subject.startswith("Training: "):
                        topic = subject[len("Training: "):]
                    else:
                        topic = subject
                    topic_counter[topic] += 1
            
            self.metrics['training_metrics']['topics'] = dict(topic_counter)
            
            # Update platform metrics
            platform_counter = Counter()
            for thread in threads:
                for conv in thread.get('conversations', []):
                    if 'platform' in conv:
                        platform_counter[conv['platform']] += 1
            
            self.metrics['training_metrics']['platforms'] = dict(platform_counter)
            
            # Update session history
            session_history = []
            for thread in threads:
                created_at = thread.get('created_at')
                if not created_at:
                    continue
                    
                # Convert string timestamp to datetime if needed
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.datetime.now()
                
                session_history.append({
                    'id': thread.get('id'),
                    'timestamp': created_at.isoformat(),
                    'topic': thread.get('subject', 'Unknown'),
                    'completed': bool(thread.get('final_plan')),
                    'platforms': len(thread.get('conversations', [])),
                    'contributions': len(thread.get('ai_contributions', {}))
                })
            
            # Sort by timestamp and keep limited history
            session_history.sort(key=lambda x: x['timestamp'], reverse=True)
            self.metrics['training_metrics']['session_history'] = session_history[:100]
            
            # Calculate average session duration (simulated)
            self.metrics['training_metrics']['avg_session_duration'] = np.random.uniform(60, 300)
            
        except Exception as e:
            self.logger.error(f"Error updating training metrics: {str(e)}")
    
    def _update_platform_metrics(self):
        """Update metrics for individual AI platforms"""
        try:
            # Get all training threads
            threads = self.memory_system.get_threads(limit=100)
            if not threads:
                return
            
            # Initialize platform metrics
            platform_success = defaultdict(lambda: {'success': 0, 'total': 0})
            platform_response_times = defaultdict(list)
            platform_usage = Counter()
            platform_quality = defaultdict(list)
            
            # Analyze threads for platform metrics
            for thread in threads:
                thread_completed = bool(thread.get('final_plan'))
                
                # Track which platforms were used in this thread
                thread_platforms = set()
                
                for conv in thread.get('conversations', []):
                    if 'platform' not in conv:
                        continue
                        
                    platform = conv['platform']
                    thread_platforms.add(platform)
                    
                    # Track platform usage
                    platform_usage[platform] += 1
                    
                    # Track platform success contribution
                    if thread_completed:
                        platform_success[platform]['success'] += 1
                    platform_success[platform]['total'] += 1
                    
                    # Simulate response times (in real system would be stored with conversation)
                    platform_response_times[platform].append(np.random.uniform(1, 10))
                    
                    # Simulate quality score (in real system would be based on contribution value)
                    quality_score = np.random.uniform(0.5, 1.0)
                    platform_quality[platform].append(quality_score)
            
            # Calculate success rates
            platform_success_rates = {}
            for platform, counts in platform_success.items():
                if counts['total'] > 0:
                    platform_success_rates[platform] = counts['success'] / counts['total']
                else:
                    platform_success_rates[platform] = 0
            
            # Calculate average response times
            platform_avg_response_times = {}
            for platform, times in platform_response_times.items():
                if times:
                    platform_avg_response_times[platform] = sum(times) / len(times)
                else:
                    platform_avg_response_times[platform] = 0
            
            # Calculate average quality scores
            platform_avg_quality = {}
            for platform, scores in platform_quality.items():
                if scores:
                    platform_avg_quality[platform] = sum(scores) / len(scores)
                else:
                    platform_avg_quality[platform] = 0
            
            # Update the metrics
            self.metrics['platform_metrics']['platform_success_rates'] = platform_success_rates
            self.metrics['platform_metrics']['platform_response_times'] = platform_avg_response_times
            self.metrics['platform_metrics']['platform_usage'] = dict(platform_usage)
            self.metrics['platform_metrics']['platform_contribution_quality'] = platform_avg_quality
            
        except Exception as e:
            self.logger.error(f"Error updating platform metrics: {str(e)}")
    
    def _update_user_engagement(self):
        """Update user engagement metrics"""
        # This would normally come from user interaction tracking
        # For now, we'll use simulated data
        
        # Add today as an active day if not already present
        today = datetime.date.today().isoformat()
        active_days = self.metrics['user_engagement']['active_days']
        if today not in active_days:
            active_days.append(today)
            # Keep only the last 90 days
            self.metrics['user_engagement']['active_days'] = sorted(active_days)[-90:]
        
        # Update feature usage (simulated)
        features = ['training', 'logs', 'settings', 'dashboard', 'recommendations']
        feature = np.random.choice(features)
        self.metrics['user_engagement']['feature_usage'][feature] = \
            self.metrics['user_engagement']['feature_usage'].get(feature, 0) + 1
        
        # Update interaction patterns (simulated)
        hour_of_day = datetime.datetime.now().hour
        day_of_week = datetime.datetime.now().weekday()
        pattern = {
            'timestamp': datetime.datetime.now().isoformat(),
            'hour': hour_of_day,
            'day_of_week': day_of_week,
            'feature': feature
        }
        self.metrics['user_engagement']['interaction_patterns'].append(pattern)
        
        # Limit history length
        if len(self.metrics['user_engagement']['interaction_patterns']) > 1000:
            self.metrics['user_engagement']['interaction_patterns'] = \
                self.metrics['user_engagement']['interaction_patterns'][-1000:]
    
    def get_system_health(self):
        """
        Get current system health metrics
        
        Returns:
            dict: System health summary
        """
        self.update_metrics()
        
        # Get the most recent metrics
        memory_usage = self.metrics['system_performance']['memory_usage'][-1]['value'] \
            if self.metrics['system_performance']['memory_usage'] else 0
            
        api_latency = self.metrics['system_performance']['api_latency'][-1]['value'] \
            if self.metrics['system_performance']['api_latency'] else 0
            
        error_rate = self.metrics['system_performance']['error_rates'][-1]['value'] \
            if self.metrics['system_performance']['error_rates'] else 0
        
        # Calculate health scores
        memory_score = 100 - (memory_usage / 100 * 100)
        latency_score = 100 - (api_latency / 1000 * 100)  # Assuming 1000ms is the max acceptable
        error_score = 100 - (error_rate * 20)  # Assuming 5% is the max acceptable
        
        # Calculate overall health score (weighted average)
        overall_score = (memory_score * 0.3) + (latency_score * 0.4) + (error_score * 0.3)
        overall_score = max(0, min(100, overall_score))  # Clamp to 0-100
        
        # Determine health status
        if overall_score >= 80:
            status = "healthy"
        elif overall_score >= 60:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'score': overall_score,
            'memory_usage': memory_usage,
            'api_latency': api_latency,
            'error_rate': error_rate,
            'memory_score': memory_score,
            'latency_score': latency_score,
            'error_score': error_score,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def get_training_summary(self):
        """
        Get summary of training metrics
        
        Returns:
            dict: Training metrics summary
        """
        self.update_metrics()
        
        return {
            'total_sessions': self.metrics['training_metrics']['sessions_total'],
            'completed_sessions': self.metrics['training_metrics']['sessions_completed'],
            'failed_sessions': self.metrics['training_metrics']['sessions_failed'],
            'success_rate': self.metrics['training_metrics']['success_rate'],
            'avg_duration': self.metrics['training_metrics']['avg_session_duration'],
            'top_topics': dict(Counter(self.metrics['training_metrics']['topics']).most_common(5)),
            'top_platforms': dict(Counter(self.metrics['training_metrics']['platforms']).most_common(5)),
            'recent_sessions': self.metrics['training_metrics']['session_history'][:5]
        }
    
    def get_platform_comparison(self):
        """
        Get comparative metrics for AI platforms
        
        Returns:
            dict: Platform comparison metrics
        """
        self.update_metrics()
        
        return {
            'success_rates': self.metrics['platform_metrics']['platform_success_rates'],
            'response_times': self.metrics['platform_metrics']['platform_response_times'],
            'usage': self.metrics['platform_metrics']['platform_usage'],
            'quality': self.metrics['platform_metrics']['platform_contribution_quality']
        }
    
    def get_user_activity(self):
        """
        Get user activity metrics
        
        Returns:
            dict: User activity summary
        """
        self.update_metrics()
        
        # Calculate active days in last week/month
        today = datetime.date.today()
        active_days = self.metrics['user_engagement']['active_days']
        
        # Convert string dates to date objects
        date_objects = []
        for day_str in active_days:
            try:
                date_objects.append(datetime.date.fromisoformat(day_str))
            except ValueError:
                continue
        
        # Count days in time periods
        last_week = today - datetime.timedelta(days=7)
        last_month = today - datetime.timedelta(days=30)
        
        days_active_week = sum(1 for d in date_objects if d >= last_week)
        days_active_month = sum(1 for d in date_objects if d >= last_month)
        
        # Calculate feature usage percentages
        feature_usage = self.metrics['user_engagement']['feature_usage']
        total_usage = sum(feature_usage.values())
        
        feature_percentages = {}
        if total_usage > 0:
            for feature, count in feature_usage.items():
                feature_percentages[feature] = count / total_usage
        
        return {
            'days_active_week': days_active_week,
            'days_active_month': days_active_month,
            'active_day_streak': self._calculate_streak(date_objects),
            'feature_usage': feature_percentages,
            'total_interactions': total_usage
        }
    
    def _calculate_streak(self, date_list):
        """Calculate the current streak of consecutive days"""
        if not date_list:
            return 0
            
        # Sort dates in descending order
        sorted_dates = sorted(date_list, reverse=True)
        
        # Check if today is in the list
        today = datetime.date.today()
        if not sorted_dates or sorted_dates[0] != today:
            return 0
            
        # Count streak
        streak = 1
        for i in range(len(sorted_dates) - 1):
            if (sorted_dates[i] - sorted_dates[i+1]).days == 1:
                streak += 1
            else:
                break
                
        return streak
    
    def generate_performance_chart(self, metric_type, time_range='week'):
        """
        Generate chart data for a specific performance metric
        
        Args:
            metric_type (str): Type of metric to chart ('memory', 'latency', 'error', etc.)
            time_range (str): Time range for chart ('day', 'week', 'month')
            
        Returns:
            dict: Chart data in format suitable for plotting
        """
        self.update_metrics()
        
        # Define time range in hours
        hours = {
            'day': 24,
            'week': 168,
            'month': 720
        }.get(time_range, 168)
        
        # Get current time for filtering
        now = datetime.datetime.now()
        cutoff_time = now - datetime.timedelta(hours=hours)
        
        # Select the appropriate metric based on type
        if metric_type == 'memory':
            data = self.metrics['system_performance']['memory_usage']
            title = 'Memory Usage Over Time'
            y_label = 'Memory Usage (%)'
        elif metric_type == 'latency':
            data = self.metrics['system_performance']['api_latency']
            title = 'API Latency Over Time'
            y_label = 'Latency (ms)'
        elif metric_type == 'error':
            data = self.metrics['system_performance']['error_rates']
            title = 'Error Rate Over Time'
            y_label = 'Error Rate (%)'
        else:
            return {'error': f"Unknown metric type: {metric_type}"}
        
        # Filter data by time range
        filtered_data = []
        for entry in data:
            try:
                timestamp = datetime.datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if timestamp >= cutoff_time:
                    filtered_data.append({
                        'timestamp': entry['timestamp'],
                        'value': entry['value']
                    })
            except Exception as e:
                self.logger.error(f"Error parsing timestamp: {e}")
        
        # Sort by timestamp
        filtered_data.sort(key=lambda x: x['timestamp'])
        
        # Prepare chart data
        timestamps = [entry['timestamp'] for entry in filtered_data]
        values = [entry['value'] for entry in filtered_data]
        
        return {
            'title': title,
            'x_label': 'Time',
            'y_label': y_label,
            'x_data': timestamps,
            'y_data': values,
            'type': 'line'
        }
    
    def generate_topic_distribution_chart(self):
        """
        Generate chart data for topic distribution
        
        Returns:
            dict: Chart data for plotting
        """
        self.update_metrics()
        
        topics = self.metrics['training_metrics']['topics']
        
        # Sort topics by count
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        labels = [item[0] for item in sorted_topics]
        values = [item[1] for item in sorted_topics]
        
        return {
            'title': 'Training Topics Distribution',
            'labels': labels,
            'values': values,
            'type': 'pie'
        }
    
    def generate_platform_comparison_chart(self, metric='success_rate'):
        """
        Generate chart data comparing AI platforms
        
        Args:
            metric (str): Metric to compare ('success_rate', 'response_time', 'quality')
            
        Returns:
            dict: Chart data for plotting
        """
        self.update_metrics()
        
        if metric == 'success_rate':
            data = self.metrics['platform_metrics']['platform_success_rates']
            title = 'AI Platform Success Rates'
            y_label = 'Success Rate'
        elif metric == 'response_time':
            data = self.metrics['platform_metrics']['platform_response_times']
            title = 'AI Platform Response Times'
            y_label = 'Avg. Response Time (s)'
        elif metric == 'quality':
            data = self.metrics['platform_metrics']['platform_contribution_quality']
            title = 'AI Platform Contribution Quality'
            y_label = 'Quality Score'
        elif metric == 'usage':
            data = self.metrics['platform_metrics']['platform_usage']
            title = 'AI Platform Usage'
            y_label = 'Number of Sessions'
        else:
            return {'error': f"Unknown metric: {metric}"}
        
        # Sort by value
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        platforms = [item[0] for item in sorted_data]
        values = [item[1] for item in sorted_data]
        
        return {
            'title': title,
            'x_label': 'Platform',
            'y_label': y_label,
            'x_data': platforms,
            'y_data': values,
            'type': 'bar'
        }
    
    def generate_user_activity_heatmap(self):
        """
        Generate heatmap data for user activity by day and hour
        
        Returns:
            dict: Heatmap data for plotting
        """
        self.update_metrics()
        
        # Initialize heatmap data structure (day x hour)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        # Create 2D array filled with zeros
        heatmap_data = np.zeros((7, 24))
        
        # Fill from interaction patterns
        for interaction in self.metrics['user_engagement']['interaction_patterns']:
            day = interaction.get('day_of_week')
            hour = interaction.get('hour')
            if day is not None and hour is not None and 0 <= day < 7 and 0 <= hour < 24:
                heatmap_data[day, hour] += 1
        
        return {
            'title': 'User Activity by Day and Hour',
            'x_labels': hours,
            'y_labels': days,
            'data': heatmap_data.tolist(),
            'type': 'heatmap'
        }
    
    def export_metrics_csv(self, metric_type):
        """
        Export specific metrics to CSV format
        
        Args:
            metric_type (str): Type of metrics to export
            
        Returns:
            str: Path to the exported CSV file
        """
        self.update_metrics()
        
        export_path = os.path.join(self.analytics_dir, f"{metric_type}_export_{int(time.time())}.csv")
        
        try:
            if metric_type == 'training_sessions':
                # Export training session history
                df = pd.DataFrame(self.metrics['training_metrics']['session_history'])
                df.to_csv(export_path, index=False)
                
            elif metric_type == 'platform_metrics':
                # Export platform comparison metrics
                success_rates = self.metrics['platform_metrics']['platform_success_rates']
                response_times = self.metrics['platform_metrics']['platform_response_times']
                usage = self.metrics['platform_metrics']['platform_usage']
                quality = self.metrics['platform_metrics']['platform_contribution_quality']
                
                # Combine into a single dataframe
                data = []
                platforms = set(list(success_rates.keys()) + list(response_times.keys()) + 
                               list(usage.keys()) + list(quality.keys()))
                               
                for platform in platforms:
                    data.append({
                        'platform': platform,
                        'success_rate': success_rates.get(platform, 0),
                        'response_time': response_times.get(platform, 0),
                        'usage': usage.get(platform, 0),
                        'quality': quality.get(platform, 0)
                    })
                    
                df = pd.DataFrame(data)
                df.to_csv(export_path, index=False)
                
            elif metric_type == 'system_performance':
                # Export system performance metrics
                memory_data = self.metrics['system_performance']['memory_usage']
                latency_data = self.metrics['system_performance']['api_latency']
                error_data = self.metrics['system_performance']['error_rates']
                
                # Create separate dataframes and then merge
                mem_df = pd.DataFrame(memory_data)
                mem_df.rename(columns={'value': 'memory_usage'}, inplace=True)
                
                lat_df = pd.DataFrame(latency_data)
                lat_df.rename(columns={'value': 'api_latency'}, inplace=True)
                
                err_df = pd.DataFrame(error_data)
                err_df.rename(columns={'value': 'error_rate'}, inplace=True)
                
                # Merge on timestamp (this is simplified and would need proper time alignment in production)
                # For now, just export memory usage as an example
                mem_df.to_csv(export_path, index=False)
                
            else:
                return f"Unknown metric type: {metric_type}"
                
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics to CSV: {str(e)}")
            return f"Error: {str(e)}"