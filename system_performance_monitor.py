import os
import logging
import time
import json
import datetime
import threading
import psutil
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class SystemPerformanceMonitor:
    """
    Advanced system performance monitoring for Synapse Chamber
    
    Tracks CPU, memory, disk, network usage, and process metrics in real-time
    Provides historical performance data analysis and visualization
    Triggers alerts based on thresholds
    """
    
    def __init__(self, analytics_system=None):
        self.logger = logging.getLogger(__name__)
        self.analytics_system = analytics_system
        self.monitor_dir = "data/performance_monitoring"
        
        # Create directories if they don't exist
        os.makedirs(self.monitor_dir, exist_ok=True)
        
        # Initialize metrics storage
        self.metrics = {
            'cpu': {
                'usage_percent': deque(maxlen=1000),
                'per_core': deque(maxlen=1000),
                'temperature': deque(maxlen=1000),
                'context_switches': deque(maxlen=1000),
                'interrupts': deque(maxlen=1000)
            },
            'memory': {
                'usage_percent': deque(maxlen=1000),
                'available': deque(maxlen=1000),
                'used': deque(maxlen=1000),
                'swap_used': deque(maxlen=1000),
                'swap_percent': deque(maxlen=1000)
            },
            'disk': {
                'usage_percent': deque(maxlen=1000),
                'io_read': deque(maxlen=1000),
                'io_write': deque(maxlen=1000),
                'io_time': deque(maxlen=1000)
            },
            'network': {
                'bytes_sent': deque(maxlen=1000),
                'bytes_recv': deque(maxlen=1000),
                'packets_sent': deque(maxlen=1000),
                'packets_recv': deque(maxlen=1000),
                'connections': deque(maxlen=1000)
            },
            'processes': {
                'total': deque(maxlen=1000),
                'running': deque(maxlen=1000),
                'sleeping': deque(maxlen=1000),
                'stopped': deque(maxlen=1000),
                'zombie': deque(maxlen=1000),
                'threads': deque(maxlen=1000)
            },
            'python_process': {
                'cpu_percent': deque(maxlen=1000),
                'memory_percent': deque(maxlen=1000),
                'threads': deque(maxlen=1000),
                'open_files': deque(maxlen=1000),
                'connections': deque(maxlen=1000)
            },
            'system': {
                'boot_time': 0,
                'uptime': deque(maxlen=1000),
                'load_avg_1min': deque(maxlen=1000),
                'load_avg_5min': deque(maxlen=1000),
                'load_avg_15min': deque(maxlen=1000)
            }
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 90.0,
            'disk_percent': 90.0,
            'swap_percent': 80.0,
            'python_cpu_percent': 70.0,
            'python_memory_percent': 60.0
        }
        
        # Track past alerts to avoid spamming
        self.last_alerts = {}
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 5  # seconds
        
        # IO counters for calculating rates
        self.last_disk_io = None
        self.last_net_io = None
        self.last_check_time = None
        
        # Load metrics if available
        self._load_metrics()
        
    def _load_metrics(self):
        """Load saved metrics from file if available"""
        metrics_path = os.path.join(self.monitor_dir, 'recent_metrics.json')
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    saved_metrics = json.load(f)
                    
                # Convert loaded lists back to deques with maxlen
                for category in saved_metrics:
                    if isinstance(saved_metrics[category], dict):
                        for metric in saved_metrics[category]:
                            if isinstance(saved_metrics[category][metric], list):
                                # Only keep the last 1000 entries
                                data = saved_metrics[category][metric][-1000:]
                                # Only restore metrics that exist in our structure
                                if category in self.metrics and metric in self.metrics[category]:
                                    self.metrics[category][metric] = deque(data, maxlen=1000)
                            elif metric == 'boot_time' and category == 'system':
                                self.metrics[category][metric] = saved_metrics[category][metric]
                
                self.logger.info("Loaded performance metrics from disk")
            except Exception as e:
                self.logger.error(f"Error loading performance metrics: {str(e)}")
    
    def _save_metrics(self):
        """Save metrics to file for persistence"""
        metrics_path = os.path.join(self.monitor_dir, 'recent_metrics.json')
        try:
            # Convert deques to lists for JSON serialization
            serializable_metrics = {}
            for category in self.metrics:
                serializable_metrics[category] = {}
                for metric in self.metrics[category]:
                    if isinstance(self.metrics[category][metric], deque):
                        serializable_metrics[category][metric] = list(self.metrics[category][metric])
                    else:
                        serializable_metrics[category][metric] = self.metrics[category][metric]
            
            with open(metrics_path, 'w') as f:
                json.dump(serializable_metrics, f)
                
            self.logger.debug("Performance metrics saved to disk")
            return True
        except Exception as e:
            self.logger.error(f"Error saving performance metrics: {str(e)}")
            return False
    
    def start_monitoring(self):
        """Start the monitoring thread if not already running"""
        if self.monitoring:
            self.logger.info("Performance monitoring already running")
            return False
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Started performance monitoring")
        return True
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        if not self.monitoring:
            self.logger.info("Performance monitoring already stopped")
            return False
            
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
            
        self._save_metrics()
        self.logger.info("Stopped performance monitoring")
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        self.logger.info("Performance monitoring loop started")
        
        # Initialize last check time and IO counters
        self.last_check_time = time.time()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_net_io = psutil.net_io_counters()
        
        while self.monitoring:
            try:
                # Collect all metrics
                self._collect_system_metrics()
                
                # Check for threshold violations
                self._check_thresholds()
                
                # Update analytics system if available
                if self.analytics_system:
                    self._update_analytics()
                
                # Save metrics periodically (every 5 minutes)
                current_time = int(time.time())
                if current_time % 300 < self.monitor_interval:
                    self._save_metrics()
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {str(e)}")
            
            # Sleep for the monitoring interval
            time.sleep(self.monitor_interval)
    
    def _collect_system_metrics(self):
        """Collect all system metrics"""
        timestamp = datetime.datetime.now().isoformat()
        current_time = time.time()
        time_delta = current_time - self.last_check_time
        
        # Get CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        
        # Get context switches and interrupts (psutil doesn't provide temperature)
        try:
            ctx_switches = psutil.cpu_stats().ctx_switches
            interrupts = psutil.cpu_stats().interrupts
        except:
            ctx_switches = 0
            interrupts = 0
        
        # Store CPU metrics
        self.metrics['cpu']['usage_percent'].append({'timestamp': timestamp, 'value': cpu_percent})
        self.metrics['cpu']['per_core'].append({'timestamp': timestamp, 'value': cpu_per_core})
        self.metrics['cpu']['context_switches'].append({'timestamp': timestamp, 'value': ctx_switches})
        self.metrics['cpu']['interrupts'].append({'timestamp': timestamp, 'value': interrupts})
        
        # Get memory metrics
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Store memory metrics
        self.metrics['memory']['usage_percent'].append({'timestamp': timestamp, 'value': mem.percent})
        self.metrics['memory']['available'].append({'timestamp': timestamp, 'value': mem.available})
        self.metrics['memory']['used'].append({'timestamp': timestamp, 'value': mem.used})
        self.metrics['memory']['swap_used'].append({'timestamp': timestamp, 'value': swap.used})
        self.metrics['memory']['swap_percent'].append({'timestamp': timestamp, 'value': swap.percent})
        
        # Get disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Calculate disk IO rates
        if self.last_disk_io and time_delta > 0:
            read_rate = (disk_io.read_bytes - self.last_disk_io.read_bytes) / time_delta
            write_rate = (disk_io.write_bytes - self.last_disk_io.write_bytes) / time_delta
            io_time = disk_io.busy_time if hasattr(disk_io, 'busy_time') else 0
        else:
            read_rate = 0
            write_rate = 0
            io_time = 0
        
        self.last_disk_io = disk_io
        
        # Store disk metrics
        self.metrics['disk']['usage_percent'].append({'timestamp': timestamp, 'value': disk.percent})
        self.metrics['disk']['io_read'].append({'timestamp': timestamp, 'value': read_rate})
        self.metrics['disk']['io_write'].append({'timestamp': timestamp, 'value': write_rate})
        self.metrics['disk']['io_time'].append({'timestamp': timestamp, 'value': io_time})
        
        # Get network metrics
        net_io = psutil.net_io_counters()
        
        # Calculate network IO rates
        if self.last_net_io and time_delta > 0:
            sent_rate = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta
            recv_rate = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta
            packets_sent_rate = (net_io.packets_sent - self.last_net_io.packets_sent) / time_delta
            packets_recv_rate = (net_io.packets_recv - self.last_net_io.packets_recv) / time_delta
        else:
            sent_rate = 0
            recv_rate = 0
            packets_sent_rate = 0
            packets_recv_rate = 0
        
        self.last_net_io = net_io
        
        # Count active connections
        try:
            connections_count = len(psutil.net_connections())
        except:
            connections_count = 0
        
        # Store network metrics
        self.metrics['network']['bytes_sent'].append({'timestamp': timestamp, 'value': sent_rate})
        self.metrics['network']['bytes_recv'].append({'timestamp': timestamp, 'value': recv_rate})
        self.metrics['network']['packets_sent'].append({'timestamp': timestamp, 'value': packets_sent_rate})
        self.metrics['network']['packets_recv'].append({'timestamp': timestamp, 'value': packets_recv_rate})
        self.metrics['network']['connections'].append({'timestamp': timestamp, 'value': connections_count})
        
        # Get process metrics
        process_stats = {
            'total': 0,
            'running': 0,
            'sleeping': 0,
            'stopped': 0,
            'zombie': 0,
            'threads': 0
        }
        
        for proc in psutil.process_iter(['status', 'num_threads']):
            process_stats['total'] += 1
            try:
                if proc.info['status']:
                    status = proc.info['status'].lower()
                    if status in process_stats:
                        process_stats[status] += 1
                
                if proc.info['num_threads']:
                    process_stats['threads'] += proc.info['num_threads']
            except:
                pass
        
        # Store process metrics
        for key, value in process_stats.items():
            self.metrics['processes'][key].append({'timestamp': timestamp, 'value': value})
        
        # Get python process metrics (our own process)
        python_proc = psutil.Process()
        
        # Make sure we get all the info we need
        try:
            with python_proc.oneshot():
                py_cpu = python_proc.cpu_percent()
                py_mem = python_proc.memory_percent()
                py_threads = python_proc.num_threads()
                try:
                    py_files = len(python_proc.open_files())
                except:
                    py_files = 0
                
                try:
                    py_connections = len(python_proc.connections())
                except:
                    py_connections = 0
        except:
            py_cpu = 0
            py_mem = 0
            py_threads = 0
            py_files = 0
            py_connections = 0
        
        # Store python process metrics
        self.metrics['python_process']['cpu_percent'].append({'timestamp': timestamp, 'value': py_cpu})
        self.metrics['python_process']['memory_percent'].append({'timestamp': timestamp, 'value': py_mem})
        self.metrics['python_process']['threads'].append({'timestamp': timestamp, 'value': py_threads})
        self.metrics['python_process']['open_files'].append({'timestamp': timestamp, 'value': py_files})
        self.metrics['python_process']['connections'].append({'timestamp': timestamp, 'value': py_connections})
        
        # Get system uptime and load
        self.metrics['system']['boot_time'] = psutil.boot_time()
        current_uptime = time.time() - psutil.boot_time()
        self.metrics['system']['uptime'].append({'timestamp': timestamp, 'value': current_uptime})
        
        try:
            load_avg = psutil.getloadavg()
            self.metrics['system']['load_avg_1min'].append({'timestamp': timestamp, 'value': load_avg[0]})
            self.metrics['system']['load_avg_5min'].append({'timestamp': timestamp, 'value': load_avg[1]})
            self.metrics['system']['load_avg_15min'].append({'timestamp': timestamp, 'value': load_avg[2]})
        except:
            # Fall back for systems without getloadavg
            self.metrics['system']['load_avg_1min'].append({'timestamp': timestamp, 'value': cpu_percent/100.0})
            self.metrics['system']['load_avg_5min'].append({'timestamp': timestamp, 'value': cpu_percent/100.0})
            self.metrics['system']['load_avg_15min'].append({'timestamp': timestamp, 'value': cpu_percent/100.0})
        
        # Update last check time
        self.last_check_time = current_time
    
    def _check_thresholds(self):
        """Check if any metrics exceed defined thresholds and log warnings"""
        alerts = []
        now = time.time()
        
        # Check CPU usage
        if self.metrics['cpu']['usage_percent'] and self.metrics['cpu']['usage_percent'][-1]['value'] > self.thresholds['cpu_percent']:
            # Only alert once per minute for the same issue
            if 'cpu_percent' not in self.last_alerts or (now - self.last_alerts['cpu_percent']) > 60:
                alerts.append(f"High CPU usage: {self.metrics['cpu']['usage_percent'][-1]['value']}% (threshold: {self.thresholds['cpu_percent']}%)")
                self.last_alerts['cpu_percent'] = now
        
        # Check memory usage
        if self.metrics['memory']['usage_percent'] and self.metrics['memory']['usage_percent'][-1]['value'] > self.thresholds['memory_percent']:
            if 'memory_percent' not in self.last_alerts or (now - self.last_alerts['memory_percent']) > 60:
                alerts.append(f"High memory usage: {self.metrics['memory']['usage_percent'][-1]['value']}% (threshold: {self.thresholds['memory_percent']}%)")
                self.last_alerts['memory_percent'] = now
        
        # Check disk usage
        if self.metrics['disk']['usage_percent'] and self.metrics['disk']['usage_percent'][-1]['value'] > self.thresholds['disk_percent']:
            if 'disk_percent' not in self.last_alerts or (now - self.last_alerts['disk_percent']) > 60:
                alerts.append(f"High disk usage: {self.metrics['disk']['usage_percent'][-1]['value']}% (threshold: {self.thresholds['disk_percent']}%)")
                self.last_alerts['disk_percent'] = now
        
        # Check swap usage
        if self.metrics['memory']['swap_percent'] and self.metrics['memory']['swap_percent'][-1]['value'] > self.thresholds['swap_percent']:
            if 'swap_percent' not in self.last_alerts or (now - self.last_alerts['swap_percent']) > 60:
                alerts.append(f"High swap usage: {self.metrics['memory']['swap_percent'][-1]['value']}% (threshold: {self.thresholds['swap_percent']}%)")
                self.last_alerts['swap_percent'] = now
        
        # Check Python process CPU usage
        if self.metrics['python_process']['cpu_percent'] and self.metrics['python_process']['cpu_percent'][-1]['value'] > self.thresholds['python_cpu_percent']:
            if 'python_cpu_percent' not in self.last_alerts or (now - self.last_alerts['python_cpu_percent']) > 60:
                alerts.append(f"High Python process CPU usage: {self.metrics['python_process']['cpu_percent'][-1]['value']}% (threshold: {self.thresholds['python_cpu_percent']}%)")
                self.last_alerts['python_cpu_percent'] = now
        
        # Check Python process memory usage
        if self.metrics['python_process']['memory_percent'] and self.metrics['python_process']['memory_percent'][-1]['value'] > self.thresholds['python_memory_percent']:
            if 'python_memory_percent' not in self.last_alerts or (now - self.last_alerts['python_memory_percent']) > 60:
                alerts.append(f"High Python process memory usage: {self.metrics['python_process']['memory_percent'][-1]['value']}% (threshold: {self.thresholds['python_memory_percent']}%)")
                self.last_alerts['python_memory_percent'] = now
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"PERFORMANCE ALERT: {alert}")
        
        return alerts
    
    def _update_analytics(self):
        """Update the analytics system with performance data if available"""
        if not self.analytics_system:
            return
            
        # Update system performance in analytics
        try:
            # Extract the latest metrics
            if self.metrics['cpu']['usage_percent']:
                cpu_percent = self.metrics['cpu']['usage_percent'][-1]['value']
            else:
                cpu_percent = 0
                
            if self.metrics['memory']['usage_percent']:
                memory_percent = self.metrics['memory']['usage_percent'][-1]['value']
            else:
                memory_percent = 0
                
            if self.metrics['disk']['usage_percent']:
                disk_percent = self.metrics['disk']['usage_percent'][-1]['value']
            else:
                disk_percent = 0
                
            if self.metrics['network']['bytes_sent'] and self.metrics['network']['bytes_recv']:
                network_throughput = (
                    self.metrics['network']['bytes_sent'][-1]['value'] + 
                    self.metrics['network']['bytes_recv'][-1]['value']
                )
            else:
                network_throughput = 0
            
            # Pass to analytics system if it has a method to update system performance
            if hasattr(self.analytics_system, 'update_system_performance'):
                self.analytics_system.update_system_performance(
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_percent=disk_percent,
                    network_throughput=network_throughput
                )
        except Exception as e:
            self.logger.error(f"Error updating analytics system: {str(e)}")
    
    def get_current_metrics(self):
        """Get the current system metrics"""
        # Build a snapshot of the latest values from each metric
        snapshot = {}
        
        for category in self.metrics:
            snapshot[category] = {}
            for metric in self.metrics[category]:
                if isinstance(self.metrics[category][metric], deque) and self.metrics[category][metric]:
                    snapshot[category][metric] = self.metrics[category][metric][-1]['value']
                else:
                    snapshot[category][metric] = self.metrics[category][metric]
        
        # Calculate current uptime
        if 'boot_time' in snapshot['system']:
            snapshot['system']['uptime'] = time.time() - snapshot['system']['boot_time']
            
        # Add timestamp
        snapshot['timestamp'] = datetime.datetime.now().isoformat()
        
        return snapshot
    
    def get_performance_history(self, category=None, metric=None, time_range=None):
        """
        Get historical performance data for a specific metric or category
        
        Args:
            category (str, optional): The metric category (cpu, memory, etc.)
            metric (str, optional): The specific metric within the category
            time_range (str, optional): Time range to retrieve ('hour', 'day', 'week', 'all')
            
        Returns:
            dict: Historical performance data
        """
        result = {}
        now = datetime.datetime.now()
        
        # Calculate time threshold based on time_range
        if time_range == 'hour':
            threshold = now - datetime.timedelta(hours=1)
        elif time_range == 'day':
            threshold = now - datetime.timedelta(days=1)
        elif time_range == 'week':
            threshold = now - datetime.timedelta(weeks=1)
        else:
            threshold = None  # All data
        
        # Filter data by category and metric
        if category and category in self.metrics:
            result[category] = {}
            
            if metric and metric in self.metrics[category]:
                # Return data for specific metric
                if isinstance(self.metrics[category][metric], deque):
                    if threshold:
                        # Filter by time
                        filtered_data = [
                            item for item in self.metrics[category][metric]
                            if 'timestamp' in item and datetime.datetime.fromisoformat(item['timestamp']) >= threshold
                        ]
                        result[category][metric] = filtered_data
                    else:
                        result[category][metric] = list(self.metrics[category][metric])
                else:
                    result[category][metric] = self.metrics[category][metric]
            else:
                # Return all metrics in the category
                for m in self.metrics[category]:
                    if isinstance(self.metrics[category][m], deque):
                        if threshold:
                            # Filter by time
                            filtered_data = [
                                item for item in self.metrics[category][m]
                                if 'timestamp' in item and datetime.datetime.fromisoformat(item['timestamp']) >= threshold
                            ]
                            result[category][m] = filtered_data
                        else:
                            result[category][m] = list(self.metrics[category][m])
                    else:
                        result[category][m] = self.metrics[category][m]
        else:
            # Return all categories with all metrics
            for cat in self.metrics:
                result[cat] = {}
                for m in self.metrics[cat]:
                    if isinstance(self.metrics[cat][m], deque):
                        if threshold:
                            # Filter by time
                            filtered_data = [
                                item for item in self.metrics[cat][m]
                                if 'timestamp' in item and datetime.datetime.fromisoformat(item['timestamp']) >= threshold
                            ]
                            result[cat][m] = filtered_data
                        else:
                            result[cat][m] = list(self.metrics[cat][m])
                    else:
                        result[cat][m] = self.metrics[cat][m]
        
        return result
    
    def get_performance_report(self):
        """
        Generate a comprehensive performance report
        
        Returns:
            dict: Performance report with statistics and summaries
        """
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'summary': {},
            'statistics': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Get current metrics
        current = self.get_current_metrics()
        
        # Get alerts
        alerts = self._check_thresholds()
        report['alerts'] = alerts
        
        # Build summary
        summary = {}
        
        # CPU summary
        if 'cpu' in current and 'usage_percent' in current['cpu']:
            cpu_percent = current['cpu']['usage_percent']
            summary['cpu'] = {
                'current_usage': f"{cpu_percent:.1f}%",
                'status': 'high' if cpu_percent > 80 else 'moderate' if cpu_percent > 50 else 'normal'
            }
        
        # Memory summary
        if 'memory' in current and 'usage_percent' in current['memory']:
            memory_percent = current['memory']['usage_percent']
            summary['memory'] = {
                'current_usage': f"{memory_percent:.1f}%",
                'status': 'high' if memory_percent > 80 else 'moderate' if memory_percent > 50 else 'normal'
            }
        
        # Disk summary
        if 'disk' in current and 'usage_percent' in current['disk']:
            disk_percent = current['disk']['usage_percent']
            summary['disk'] = {
                'current_usage': f"{disk_percent:.1f}%",
                'status': 'high' if disk_percent > 80 else 'moderate' if disk_percent > 50 else 'normal'
            }
        
        # Process summary
        if 'processes' in current and 'total' in current['processes']:
            total_processes = current['processes']['total']
            summary['processes'] = {
                'total': total_processes,
                'status': 'high' if total_processes > 300 else 'moderate' if total_processes > 200 else 'normal'
            }
        
        # Network summary
        if ('network' in current and 'bytes_sent' in current['network'] and 
            'bytes_recv' in current['network'] and current['network']['bytes_sent'] is not None and
            current['network']['bytes_recv'] is not None):
            network_throughput = current['network']['bytes_sent'] + current['network']['bytes_recv']
            # Convert to more readable format
            if network_throughput > 1024*1024:
                network_str = f"{network_throughput/(1024*1024):.2f} MB/s"
            else:
                network_str = f"{network_throughput/1024:.2f} KB/s"
                
            summary['network'] = {
                'throughput': network_str,
                'status': 'high' if network_throughput > 5*1024*1024 else 'moderate' if network_throughput > 1024*1024 else 'normal'
            }
        
        # Python process summary
        if ('python_process' in current and 'cpu_percent' in current['python_process'] and
            'memory_percent' in current['python_process']):
            py_cpu = current['python_process']['cpu_percent']
            py_mem = current['python_process']['memory_percent']
            summary['python_process'] = {
                'cpu_usage': f"{py_cpu:.1f}%",
                'memory_usage': f"{py_mem:.1f}%",
                'status': 'high' if (py_cpu > 50 or py_mem > 40) else 'moderate' if (py_cpu > 30 or py_mem > 25) else 'normal'
            }
        
        # System uptime
        if 'system' in current and 'uptime' in current['system']:
            uptime_seconds = current['system']['uptime']
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = ''
            if days > 0:
                uptime_str += f"{int(days)}d "
            if hours > 0 or days > 0:
                uptime_str += f"{int(hours)}h "
            uptime_str += f"{int(minutes)}m"
            
            summary['system'] = {
                'uptime': uptime_str
            }
        
        report['summary'] = summary
        
        # Calculate statistics for key metrics over the past hour
        hour_history = self.get_performance_history(time_range='hour')
        statistics = {}
        
        # CPU statistics
        if 'cpu' in hour_history and 'usage_percent' in hour_history['cpu']:
            cpu_values = [item['value'] for item in hour_history['cpu']['usage_percent'] if 'value' in item]
            if cpu_values:
                statistics['cpu'] = {
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'avg': sum(cpu_values) / len(cpu_values),
                    'samples': len(cpu_values)
                }
        
        # Memory statistics
        if 'memory' in hour_history and 'usage_percent' in hour_history['memory']:
            mem_values = [item['value'] for item in hour_history['memory']['usage_percent'] if 'value' in item]
            if mem_values:
                statistics['memory'] = {
                    'min': min(mem_values),
                    'max': max(mem_values),
                    'avg': sum(mem_values) / len(mem_values),
                    'samples': len(mem_values)
                }
        
        # Python process CPU statistics
        if 'python_process' in hour_history and 'cpu_percent' in hour_history['python_process']:
            py_cpu_values = [item['value'] for item in hour_history['python_process']['cpu_percent'] if 'value' in item]
            if py_cpu_values:
                statistics['python_cpu'] = {
                    'min': min(py_cpu_values),
                    'max': max(py_cpu_values),
                    'avg': sum(py_cpu_values) / len(py_cpu_values),
                    'samples': len(py_cpu_values)
                }
        
        # Python process memory statistics
        if 'python_process' in hour_history and 'memory_percent' in hour_history['python_process']:
            py_mem_values = [item['value'] for item in hour_history['python_process']['memory_percent'] if 'value' in item]
            if py_mem_values:
                statistics['python_memory'] = {
                    'min': min(py_mem_values),
                    'max': max(py_mem_values),
                    'avg': sum(py_mem_values) / len(py_mem_values),
                    'samples': len(py_mem_values)
                }
        
        # Network statistics
        if 'network' in hour_history and 'bytes_sent' in hour_history['network'] and 'bytes_recv' in hour_history['network']:
            sent_values = [item['value'] for item in hour_history['network']['bytes_sent'] if 'value' in item]
            recv_values = [item['value'] for item in hour_history['network']['bytes_recv'] if 'value' in item]
            
            if sent_values and recv_values and len(sent_values) == len(recv_values):
                throughput_values = [s + r for s, r in zip(sent_values, recv_values)]
                statistics['network_throughput'] = {
                    'min': min(throughput_values),
                    'max': max(throughput_values),
                    'avg': sum(throughput_values) / len(throughput_values),
                    'samples': len(throughput_values)
                }
        
        report['statistics'] = statistics
        
        # Generate recommendations based on metrics and trends
        recommendations = []
        
        # CPU recommendations
        if 'cpu' in statistics and statistics['cpu']['avg'] > 70:
            recommendations.append("High CPU usage detected. Consider optimizing resource-intensive processes or increasing CPU resources.")
        
        # Memory recommendations
        if 'memory' in statistics and statistics['memory']['avg'] > 80:
            recommendations.append("High memory usage detected. Check for memory leaks or consider increasing memory allocation.")
        
        # Disk recommendations
        if 'disk' in current and 'usage_percent' in current['disk'] and current['disk']['usage_percent'] > 85:
            recommendations.append("Disk usage is very high. Clean up unnecessary files or increase disk space.")
        
        # Python process recommendations
        if 'python_cpu' in statistics and statistics['python_cpu']['avg'] > 50:
            recommendations.append("The Python application is using high CPU. Profile the application to identify and optimize CPU-intensive functions.")
            
        if 'python_memory' in statistics and statistics['python_memory']['avg'] > 40:
            recommendations.append("The Python application is using high memory. Check for memory leaks or optimize memory usage.")
        
        # Network recommendations
        if 'network_throughput' in statistics and statistics['network_throughput']['avg'] > 5*1024*1024:  # 5 MB/s
            recommendations.append("High network traffic detected. Consider optimizing data transfers or implementing caching.")
        
        report['recommendations'] = recommendations
        
        return report
    
    def generate_performance_charts(self, output_dir=None):
        """
        Generate performance charts for visualization
        
        Args:
            output_dir (str, optional): Directory to save the charts
                
        Returns:
            dict: Paths to the generated chart files
        """
        if not output_dir:
            output_dir = os.path.join(self.monitor_dir, 'charts')
        
        os.makedirs(output_dir, exist_ok=True)
        
        chart_paths = {}
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get one hour of history
        history = self.get_performance_history(time_range='hour')
        
        # CPU usage chart
        if 'cpu' in history and 'usage_percent' in history['cpu'] and history['cpu']['usage_percent']:
            try:
                plt.figure(figsize=(10, 6))
                
                # Extract timestamps and values
                timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['cpu']['usage_percent']]
                values = [item['value'] for item in history['cpu']['usage_percent']]
                
                plt.plot(timestamps, values, 'b-')
                plt.title('CPU Usage (Last Hour)')
                plt.xlabel('Time')
                plt.ylabel('CPU Usage (%)')
                plt.grid(True)
                plt.ylim(0, 100)
                
                # Add threshold line
                plt.axhline(y=self.thresholds['cpu_percent'], color='r', linestyle='--', label=f'Threshold ({self.thresholds["cpu_percent"]}%)')
                plt.legend()
                
                # Format x-axis to show time
                plt.gcf().autofmt_xdate()
                
                # Save the chart
                chart_file = os.path.join(output_dir, f'cpu_usage_{timestamp}.png')
                plt.savefig(chart_file)
                plt.close()
                
                chart_paths['cpu_usage'] = chart_file
                
            except Exception as e:
                self.logger.error(f"Error generating CPU usage chart: {str(e)}")
        
        # Memory usage chart
        if 'memory' in history and 'usage_percent' in history['memory'] and history['memory']['usage_percent']:
            try:
                plt.figure(figsize=(10, 6))
                
                # Extract timestamps and values
                timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['memory']['usage_percent']]
                values = [item['value'] for item in history['memory']['usage_percent']]
                
                plt.plot(timestamps, values, 'g-')
                plt.title('Memory Usage (Last Hour)')
                plt.xlabel('Time')
                plt.ylabel('Memory Usage (%)')
                plt.grid(True)
                plt.ylim(0, 100)
                
                # Add threshold line
                plt.axhline(y=self.thresholds['memory_percent'], color='r', linestyle='--', label=f'Threshold ({self.thresholds["memory_percent"]}%)')
                plt.legend()
                
                # Format x-axis to show time
                plt.gcf().autofmt_xdate()
                
                # Save the chart
                chart_file = os.path.join(output_dir, f'memory_usage_{timestamp}.png')
                plt.savefig(chart_file)
                plt.close()
                
                chart_paths['memory_usage'] = chart_file
                
            except Exception as e:
                self.logger.error(f"Error generating memory usage chart: {str(e)}")
        
        # Python process charts (combined CPU and memory)
        if ('python_process' in history and 'cpu_percent' in history['python_process'] and 
            'memory_percent' in history['python_process'] and history['python_process']['cpu_percent'] and 
            history['python_process']['memory_percent']):
            try:
                plt.figure(figsize=(10, 6))
                
                # Create two subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
                
                # CPU usage subplot
                cpu_timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['python_process']['cpu_percent']]
                cpu_values = [item['value'] for item in history['python_process']['cpu_percent']]
                
                ax1.plot(cpu_timestamps, cpu_values, 'b-')
                ax1.set_title('Python Process CPU Usage (Last Hour)')
                ax1.set_ylabel('CPU Usage (%)')
                ax1.grid(True)
                ax1.axhline(y=self.thresholds['python_cpu_percent'], color='r', linestyle='--', 
                          label=f'Threshold ({self.thresholds["python_cpu_percent"]}%)')
                ax1.legend()
                
                # Memory usage subplot
                mem_timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['python_process']['memory_percent']]
                mem_values = [item['value'] for item in history['python_process']['memory_percent']]
                
                ax2.plot(mem_timestamps, mem_values, 'g-')
                ax2.set_title('Python Process Memory Usage (Last Hour)')
                ax2.set_xlabel('Time')
                ax2.set_ylabel('Memory Usage (%)')
                ax2.grid(True)
                ax2.axhline(y=self.thresholds['python_memory_percent'], color='r', linestyle='--', 
                          label=f'Threshold ({self.thresholds["python_memory_percent"]}%)')
                ax2.legend()
                
                # Format x-axis to show time
                fig.autofmt_xdate()
                
                plt.tight_layout()
                
                # Save the chart
                chart_file = os.path.join(output_dir, f'python_process_{timestamp}.png')
                plt.savefig(chart_file)
                plt.close()
                
                chart_paths['python_process'] = chart_file
                
            except Exception as e:
                self.logger.error(f"Error generating Python process charts: {str(e)}")
        
        # Network throughput chart
        if ('network' in history and 'bytes_sent' in history['network'] and 
            'bytes_recv' in history['network'] and history['network']['bytes_sent'] and 
            history['network']['bytes_recv']):
            try:
                plt.figure(figsize=(10, 6))
                
                # Extract timestamps and values
                sent_timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['network']['bytes_sent']]
                sent_values = [item['value'] / 1024 for item in history['network']['bytes_sent']]  # Convert to KB/s
                
                recv_timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in history['network']['bytes_recv']]
                recv_values = [item['value'] / 1024 for item in history['network']['bytes_recv']]  # Convert to KB/s
                
                plt.plot(sent_timestamps, sent_values, 'b-', label='Sent')
                plt.plot(recv_timestamps, recv_values, 'g-', label='Received')
                plt.title('Network Throughput (Last Hour)')
                plt.xlabel('Time')
                plt.ylabel('Throughput (KB/s)')
                plt.grid(True)
                plt.legend()
                
                # Format x-axis to show time
                plt.gcf().autofmt_xdate()
                
                # Save the chart
                chart_file = os.path.join(output_dir, f'network_throughput_{timestamp}.png')
                plt.savefig(chart_file)
                plt.close()
                
                chart_paths['network_throughput'] = chart_file
                
            except Exception as e:
                self.logger.error(f"Error generating network throughput chart: {str(e)}")
        
        return chart_paths
    
    def set_threshold(self, metric, value):
        """
        Set a threshold for a specific metric
        
        Args:
            metric (str): The metric name (e.g., 'cpu_percent', 'memory_percent')
            value (float): The threshold value
                
        Returns:
            bool: Success status
        """
        if metric in self.thresholds:
            self.thresholds[metric] = value
            self.logger.info(f"Set threshold for {metric} to {value}")
            return True
        else:
            self.logger.error(f"Unknown metric: {metric}")
            return False