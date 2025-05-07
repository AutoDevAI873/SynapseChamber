document.addEventListener('DOMContentLoaded', function() {
  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') {
    console.error('Chart.js library not loaded');
    showNotification('error', 'Failed to load Chart.js library');
    return;
  }
  
  // Add compatibility for Chart.instances if it doesn't exist
  if (!Chart.instances) {
    Chart.instances = [];
    Chart.instances.forEach = function() { /* Empty function */ };
    console.log('Added Chart.instances compatibility');
  }
  
  // Initialize dashboard components
  try {
    // Initialize charts if they exist
    initializeCharts();
    
    // Set up refresh button
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
      refreshButton.addEventListener('click', function() {
        refreshDashboardData();
      });
    }
    
    // Set up metric selection buttons
    const metricButtons = document.querySelectorAll('[data-metric]');
    metricButtons.forEach(button => {
      button.addEventListener('click', function() {
        metricButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        
        // Update chart based on selected metric
        updatePlatformComparison(this.dataset.metric);
      });
    });
    
    // Load initial data
    loadDashboardData();
  } catch (error) {
    console.error('Error initializing dashboard:', error);
    showNotification('error', 'Failed to initialize dashboard');
  }
});

function initializeCharts() {
  // Platform Comparison chart
  const platformComparisonElem = document.getElementById('platformComparisonChart');
  if (platformComparisonElem) {
    try {
      const ctx = platformComparisonElem.getContext('2d');
      window.platformComparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
          datasets: [{
            label: 'Success Rate (%)',
            data: [92, 88, 85, 75, 80],
            backgroundColor: 'rgba(13, 110, 253, 0.2)',
            borderColor: 'rgba(13, 110, 253, 1)',
            pointBackgroundColor: 'rgba(13, 110, 253, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(13, 110, 253, 1)',
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                backdropColor: 'transparent',
                color: '#adb5bd'
              },
              pointLabels: {
                color: '#adb5bd',
                font: {
                  size: 12
                }
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating platform comparison chart:', error);
    }
  }
  
  // Sessions Timeline chart
  const sessionTimelineElem = document.getElementById('sessionTimelineChart');
  if (sessionTimelineElem) {
    try {
      const ctx = sessionTimelineElem.getContext('2d');
      window.sessionTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['January', 'February', 'March', 'April', 'May'],
          datasets: [{
            label: 'Training Sessions',
            data: [5, 12, 15, 20, 25],
            fill: true,
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            borderColor: 'rgba(13, 110, 253, 1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#adb5bd'
              }
            },
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#adb5bd'
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating session timeline chart:', error);
    }
  }
  
  // Topic Distribution chart
  const topicDistributionElem = document.getElementById('topicsDistributionChart');
  if (topicDistributionElem) {
    try {
      const ctx = topicDistributionElem.getContext('2d');
      window.topicDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['API Design', 'Database', 'UI/UX', 'Algorithms', 'Testing'],
          datasets: [{
            data: [30, 25, 20, 15, 10],
            backgroundColor: [
              '#0d6efd',
              '#6610f2',
              '#6f42c1',
              '#dc3545',
              '#fd7e14'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#adb5bd'
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating topic distribution chart:', error);
    }
  }
  
  // Platform Usage chart
  const platformUsageElem = document.getElementById('platformUsageChart');
  if (platformUsageElem) {
    try {
      const ctx = platformUsageElem.getContext('2d');
      window.platformUsageChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
          datasets: [{
            data: [45, 25, 15, 10, 5],
            backgroundColor: [
              '#10a37f',
              '#a33a33',
              '#4285f4',
              '#6f42c1',
              '#e03c31'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#adb5bd'
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating platform usage chart:', error);
    }
  }
  
  // Topic Success Rate chart
  const topicSuccessElem = document.getElementById('topicSuccessChart');
  if (topicSuccessElem) {
    try {
      const ctx = topicSuccessElem.getContext('2d');
      window.topicSuccessChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['API Design', 'Database', 'UI/UX', 'Algorithms', 'Testing'],
          datasets: [{
            label: 'Success Rate (%)',
            data: [92, 88, 95, 75, 90],
            backgroundColor: [
              'rgba(13, 110, 253, 0.7)',
              'rgba(102, 16, 242, 0.7)',
              'rgba(111, 66, 193, 0.7)',
              'rgba(220, 53, 69, 0.7)',
              'rgba(253, 126, 20, 0.7)'
            ],
            borderRadius: 4,
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#adb5bd'
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                color: '#adb5bd'
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating topic success chart:', error);
    }
  }
}

function loadDashboardData() {
  // Update system health metrics
  updateSystemHealth({
    memory_usage: 45,
    api_latency: 120,
    error_rate: 1.2,
    status: 'success',
    message: 'System is operating normally. All components are responsive and healthy.'
  });
  
  // Fetch real data from API (with fallback to default values)
  fetchDashboardData();
}

function refreshDashboardData() {
  // Show loading indicators
  const refreshBtn = document.getElementById('refreshButton');
  if (refreshBtn) {
    const originalContent = refreshBtn.innerHTML;
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
    
    // Add loading overlays to charts
    document.querySelectorAll('.chart-container').forEach(container => {
      let overlay = container.querySelector('.loading-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        container.appendChild(overlay);
      }
    });
    
    // Simulate loading delay
    setTimeout(() => {
      // Remove loading indicators
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = originalContent;
      
      document.querySelectorAll('.loading-overlay').forEach(overlay => {
        overlay.parentNode.removeChild(overlay);
      });
      
      // Fetch fresh data
      fetchDashboardData();
      
      // Show success notification
      showNotification('success', 'Dashboard data refreshed successfully');
    }, 1200);
  }
}

function fetchDashboardData() {
  // Fetch system health data
  fetch('/api/analytics/system_health')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updateSystemHealth(data.health);
      }
    })
    .catch(error => {
      console.error('Error fetching system health:', error);
    });
  
  // Fetch training summary
  fetch('/api/analytics/training_summary')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updateMetrics(data.summary);
        updateRecentSessions(data.summary.recent_sessions);
      }
    })
    .catch(error => {
      console.error('Error fetching training summary:', error);
    });
  
  // Fetch platform comparison
  fetch('/api/analytics/platform_comparison')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updatePlatformComparison('success_rate', data.comparison);
      }
    })
    .catch(error => {
      console.error('Error fetching platform comparison:', error);
    });
}

function updateSystemHealth(health) {
  // Memory usage
  const memoryUsageValue = document.getElementById('memoryUsageValue');
  const memoryUsageBar = document.getElementById('memoryUsageBar');
  
  if (memoryUsageValue && memoryUsageBar) {
    memoryUsageValue.textContent = health.memory_usage + '%';
    memoryUsageBar.style.width = health.memory_usage + '%';
    
    // Update color based on usage level
    if (health.memory_usage > 80) {
      memoryUsageBar.className = 'progress-bar bg-danger';
    } else if (health.memory_usage > 60) {
      memoryUsageBar.className = 'progress-bar bg-warning';
    } else {
      memoryUsageBar.className = 'progress-bar bg-success';
    }
  }
  
  // API latency
  const apiLatencyValue = document.getElementById('apiLatencyValue');
  const apiLatencyBar = document.getElementById('apiLatencyBar');
  
  if (apiLatencyValue && apiLatencyBar) {
    apiLatencyValue.textContent = health.api_latency + 'ms';
    
    // Scale latency for progress bar (0-200ms = 0-100%)
    const latencyPercentage = Math.min(100, health.api_latency / 2);
    apiLatencyBar.style.width = latencyPercentage + '%';
    
    // Update color based on latency level
    if (health.api_latency > 150) {
      apiLatencyBar.className = 'progress-bar bg-danger';
    } else if (health.api_latency > 100) {
      apiLatencyBar.className = 'progress-bar bg-warning';
    } else {
      apiLatencyBar.className = 'progress-bar bg-success';
    }
  }
  
  // Error rate
  const errorRateValue = document.getElementById('errorRateValue');
  const errorRateBar = document.getElementById('errorRateBar');
  
  if (errorRateValue && errorRateBar) {
    errorRateValue.textContent = health.error_rate + '%';
    
    // Scale error rate for progress bar (0-20% = 0-100%)
    const errorPercentage = Math.min(100, health.error_rate * 5);
    errorRateBar.style.width = errorPercentage + '%';
    
    // Update color based on error level
    if (health.error_rate > 5) {
      errorRateBar.className = 'progress-bar bg-danger';
    } else if (health.error_rate > 2) {
      errorRateBar.className = 'progress-bar bg-warning';
    } else {
      errorRateBar.className = 'progress-bar bg-success';
    }
  }
  
  // System alert
  const systemAlert = document.getElementById('systemAlert');
  const systemAlertMsg = document.getElementById('systemAlertMsg');
  
  if (systemAlert && systemAlertMsg) {
    systemAlertMsg.textContent = health.message;
    
    if (health.status === 'error' || health.status === 'critical') {
      systemAlert.className = 'alert alert-danger alert-dismissible fade show py-2';
    } else if (health.status === 'warning') {
      systemAlert.className = 'alert alert-warning alert-dismissible fade show py-2';
    } else {
      systemAlert.className = 'alert alert-success alert-dismissible fade show py-2';
    }
  }
}

function updateMetrics(summary) {
  // Update key metrics in cards
  if (summary) {
    // Total Sessions
    const totalSessionsElem = document.getElementById('totalSessionsValue');
    if (totalSessionsElem) {
      totalSessionsElem.textContent = summary.total_sessions || '0';
    }
    
    // Success Rate
    const successRateElem = document.getElementById('successRateValue');
    if (successRateElem) {
      successRateElem.textContent = (summary.success_rate || '0') + '%';
    }
    
    // Average Duration
    const avgDurationElem = document.getElementById('avgDurationValue');
    if (avgDurationElem) {
      avgDurationElem.textContent = summary.avg_duration || '0.0m';
    }
    
    // Platforms Used
    const platformsUsedElem = document.getElementById('platformsUsedValue');
    if (platformsUsedElem) {
      platformsUsedElem.textContent = summary.platforms_used || '0';
    }
  }
}

function updateRecentSessions(sessions) {
  const tableBody = document.getElementById('recentSessionsTable');
  if (!tableBody) return;
  
  // Clear existing rows
  tableBody.innerHTML = '';
  
  if (sessions && sessions.length > 0) {
    // Add session rows
    sessions.forEach(session => {
      const row = document.createElement('tr');
      
      // Determine status badge class
      let statusClass = 'secondary';
      if (session.status === 'completed') statusClass = 'success';
      else if (session.status === 'failed') statusClass = 'danger';
      else if (session.status === 'in_progress') statusClass = 'info';
      
      row.innerHTML = `
        <td>${session.id}</td>
        <td>${session.topic}</td>
        <td>${formatDate(session.date)}</td>
        <td>${session.duration}</td>
        <td><span class="badge bg-${statusClass}">${session.status}</span></td>
        <td>
          <button class="btn btn-sm btn-outline-info view-session-btn" data-session-id="${session.id}">
            <i class="fas fa-eye"></i>
          </button>
        </td>
      `;
      
      tableBody.appendChild(row);
    });
    
    // Add event listeners to view buttons
    document.querySelectorAll('.view-session-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const sessionId = this.dataset.sessionId;
        window.location.href = `/training?session=${sessionId}`;
      });
    });
  } else {
    // No sessions message
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="6" class="text-center">No recent training sessions</td>`;
    tableBody.appendChild(row);
  }
}

function updatePlatformComparison(metric, data) {
  if (!window.platformComparisonChart) return;
  
  // Update chart metric label
  let metricLabel = 'Success Rate (%)';
  if (metric === 'response_time') metricLabel = 'Response Time (ms)';
  else if (metric === 'quality') metricLabel = 'Quality Score (0-10)';
  
  window.platformComparisonChart.data.datasets[0].label = metricLabel;
  
  // Update chart data if provided
  if (data) {
    window.platformComparisonChart.data.labels = data.labels;
    window.platformComparisonChart.data.datasets[0].data = data.values;
  }
  
  window.platformComparisonChart.update();
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showNotification(type, message) {
  // If global showNotification function exists, use it
  if (typeof window.showNotification === 'function') {
    window.showNotification(type, message);
    return;
  }
  
  // Check if notification container exists
  let container = document.getElementById('notificationContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notificationContainer';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
  }
  
  // Create notification
  const notification = document.createElement('div');
  notification.className = 'toast show';
  notification.role = 'alert';
  
  // Style based on type
  let bgClass = 'bg-primary';
  if (type === 'success') bgClass = 'bg-success';
  if (type === 'error') bgClass = 'bg-danger';
  if (type === 'warning') bgClass = 'bg-warning text-dark';
  if (type === 'info') bgClass = 'bg-info text-dark';
  
  notification.innerHTML = `
    <div class="toast-header ${bgClass} text-white">
      <strong class="me-auto">Synapse Chamber</strong>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body bg-dark text-white">
      ${message}
    </div>
  `;
  
  container.appendChild(notification);
  
  // Initialize Bootstrap toast
  const toast = new bootstrap.Toast(notification, {
    autohide: true,
    delay: 5000
  });
  
  // Remove from DOM when hidden
  notification.addEventListener('hidden.bs.toast', function() {
    container.removeChild(notification);
  });
}
