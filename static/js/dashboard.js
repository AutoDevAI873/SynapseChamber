// Synapse Chamber Analytics Dashboard JavaScript

// Main dashboard initialization
function initializeDashboard() {
    // Initialize dashboard components
    initializeSystemHealth();
    initializeKeyMetrics();
    initializeTrainingCharts();
    initializePlatformCharts();
    initializeUserActivity();
    initializeInsights();
    initializeAssistant();
    
    // Set up refresh button
    document.getElementById('refreshButton').addEventListener('click', function() {
        refreshDashboardData();
    });
    
    // Set up export buttons
    document.getElementById('exportTrainingData').addEventListener('click', function() {
        exportData('training_sessions');
    });
    
    document.getElementById('exportPlatformData').addEventListener('click', function() {
        exportData('platform_metrics');
    });
    
    document.getElementById('exportSystemData').addEventListener('click', function() {
        exportData('system_performance');
    });
    
    // Set up settings button
    document.getElementById('saveSettingsBtn').addEventListener('click', function() {
        saveSettings();
    });
    
    // Set up platform metric toggle buttons
    document.querySelectorAll('.btn-group[role="group"] .btn').forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons in the group
            this.parentElement.querySelectorAll('.btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update chart with new metric
            const metric = this.dataset.metric;
            updatePlatformComparisonChart(metric);
        });
    });
    
    // Set up refresh recommendations button
    document.getElementById('refreshRecommendations').addEventListener('click', function() {
        refreshRecommendations();
    });
    
    // Setup the assistant chatbox
    setupChatbox();
    
    // Check for auto-refresh settings
    checkAutoRefresh();
}

// System Health Dashboard Component
function initializeSystemHealth() {
    // Create the gauge chart for system health
    const ctx = document.createElement('canvas');
    document.getElementById('healthGauge').appendChild(ctx);
    
    const healthScore = 85; // This would come from the API
    
    // Determine color based on health score
    let gaugeColor = '#dc3545'; // Danger/red
    if (healthScore >= 80) {
        gaugeColor = '#198754'; // Success/green
    } else if (healthScore >= 60) {
        gaugeColor = '#ffc107'; // Warning/yellow
    }
    
    const gaugeConfig = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [healthScore, 100 - healthScore],
                backgroundColor: [gaugeColor, '#2a2a2a'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            circumference: 180,
            rotation: 270,
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'System Health',
                    position: 'bottom',
                    color: '#f8f9fa',
                    font: {
                        size: 14
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: true
        }
    };
    
    // Create the gauge chart
    new Chart(ctx, gaugeConfig);
    
    // Add the health score label
    const scoreLabel = document.createElement('div');
    scoreLabel.className = 'position-absolute top-50 start-50 translate-middle text-center';
    scoreLabel.style.marginTop = '-10px';
    scoreLabel.innerHTML = `<div class="h3 mb-0">${healthScore}%</div><div class="small">Health</div>`;
    document.getElementById('healthGauge').appendChild(scoreLabel);
    
    // Update the system health metrics
    updateSystemHealthMetrics({
        memory_usage: 45,
        api_latency: 120,
        error_rate: 1.2,
        status: 'healthy'
    });
}

// Update system health metrics display
function updateSystemHealthMetrics(metrics) {
    // Update memory usage
    const memoryUsageBar = document.getElementById('memoryUsageBar');
    const memoryUsageValue = document.getElementById('memoryUsageValue');
    
    memoryUsageBar.style.width = metrics.memory_usage + '%';
    memoryUsageValue.textContent = metrics.memory_usage + '%';
    
    // Set color based on usage
    if (metrics.memory_usage < 50) {
        memoryUsageBar.className = 'progress-bar bg-success';
    } else if (metrics.memory_usage < 80) {
        memoryUsageBar.className = 'progress-bar bg-warning';
    } else {
        memoryUsageBar.className = 'progress-bar bg-danger';
    }
    
    // Update API latency
    const apiLatencyBar = document.getElementById('apiLatencyBar');
    const apiLatencyValue = document.getElementById('apiLatencyValue');
    
    // Normalize latency to percentage (assuming 500ms is 100%)
    const latencyPercent = Math.min(100, (metrics.api_latency / 500) * 100);
    
    apiLatencyBar.style.width = latencyPercent + '%';
    apiLatencyValue.textContent = metrics.api_latency + 'ms';
    
    // Set color based on latency
    if (metrics.api_latency < 100) {
        apiLatencyBar.className = 'progress-bar bg-success';
    } else if (metrics.api_latency < 300) {
        apiLatencyBar.className = 'progress-bar bg-warning';
    } else {
        apiLatencyBar.className = 'progress-bar bg-danger';
    }
    
    // Update error rate
    const errorRateBar = document.getElementById('errorRateBar');
    const errorRateValue = document.getElementById('errorRateValue');
    
    // Normalize error rate to percentage (assuming 5% is 100%)
    const errorPercent = Math.min(100, (metrics.error_rate / 5) * 100);
    
    errorRateBar.style.width = errorPercent + '%';
    errorRateValue.textContent = metrics.error_rate + '%';
    
    // Set color based on error rate
    if (metrics.error_rate < 1) {
        errorRateBar.className = 'progress-bar bg-success';
    } else if (metrics.error_rate < 3) {
        errorRateBar.className = 'progress-bar bg-warning';
    } else {
        errorRateBar.className = 'progress-bar bg-danger';
    }
    
    // Update system alert
    const systemAlert = document.getElementById('systemAlert');
    const systemAlertMsg = document.getElementById('systemAlertMsg');
    
    systemAlert.className = 'alert alert-success alert-dismissible fade show py-2';
    if (metrics.status === 'healthy') {
        systemAlertMsg.textContent = 'System is operating normally. All components are responsive and healthy.';
    } else if (metrics.status === 'warning') {
        systemAlert.className = 'alert alert-warning alert-dismissible fade show py-2';
        systemAlertMsg.textContent = 'System health is degraded. Check the analytics for potential issues.';
    } else if (metrics.status === 'critical') {
        systemAlert.className = 'alert alert-danger alert-dismissible fade show py-2';
        systemAlertMsg.textContent = 'System is in critical state. Performance may be impacted.';
    }
}

// Key Metrics Dashboard Component
function initializeKeyMetrics() {
    // This would be populated from API data
    updateKeyMetrics({
        total_sessions: 32,
        completed_sessions: 28,
        failed_sessions: 4,
        success_rate: 87,
        avg_duration: 3.2,
        platforms_used: 5
    });
}

// Update key metrics display
function updateKeyMetrics(metrics) {
    document.getElementById('totalSessionsValue').textContent = metrics.total_sessions;
    document.getElementById('successRateValue').textContent = metrics.success_rate + '%';
    document.getElementById('avgDurationValue').textContent = metrics.avg_duration + 'm';
    document.getElementById('platformsUsedValue').textContent = metrics.platforms_used;
}

// Training Performance Dashboard Component
function initializeTrainingCharts() {
    // Session Timeline Chart
    const sessionTimelineCtx = document.getElementById('sessionTimelineChart').getContext('2d');
    
    // Sample data - would come from API
    const sessionTimelineData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
            {
                label: 'Completed',
                data: [4, 6, 8, 9, 7, 10],
                backgroundColor: 'rgba(25, 135, 84, 0.6)',
                borderColor: '#198754',
                borderWidth: 1
            },
            {
                label: 'Failed',
                data: [1, 2, 1, 0, 1, 0],
                backgroundColor: 'rgba(220, 53, 69, 0.6)',
                borderColor: '#dc3545',
                borderWidth: 1
            }
        ]
    };
    
    const sessionTimelineConfig = {
        type: 'bar',
        data: sessionTimelineData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f8f9fa'
                    }
                }
            }
        }
    };
    
    new Chart(sessionTimelineCtx, sessionTimelineConfig);
    
    // Topics Distribution Chart
    const topicsDistributionCtx = document.getElementById('topicsDistributionChart').getContext('2d');
    
    // Sample data - would come from API
    const topicsDistributionData = {
        labels: ['NLP', 'API Integration', 'File Handling', 'Error Handling', 'Automation'],
        datasets: [{
            data: [12, 8, 5, 4, 3],
            backgroundColor: [
                'rgba(13, 110, 253, 0.7)',
                'rgba(25, 135, 84, 0.7)',
                'rgba(255, 193, 7, 0.7)',
                'rgba(220, 53, 69, 0.7)',
                'rgba(13, 202, 240, 0.7)'
            ],
            borderColor: [
                '#0d6efd',
                '#198754',
                '#ffc107',
                '#dc3545',
                '#0dcaf0'
            ],
            borderWidth: 1
        }]
    };
    
    const topicsDistributionConfig = {
        type: 'doughnut',
        data: topicsDistributionData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#f8f9fa',
                        boxWidth: 15,
                        padding: 15
                    }
                }
            }
        }
    };
    
    new Chart(topicsDistributionCtx, topicsDistributionConfig);
    
    // Topic Success Rate Chart
    const topicSuccessCtx = document.getElementById('topicSuccessChart').getContext('2d');
    
    // Sample data - would come from API
    const topicSuccessData = {
        labels: ['NLP', 'API Integration', 'File Handling', 'Error Handling', 'Automation'],
        datasets: [{
            label: 'Success Rate (%)',
            data: [92, 78, 95, 82, 90],
            backgroundColor: 'rgba(13, 110, 253, 0.5)',
            borderColor: '#0d6efd',
            borderWidth: 1
        }]
    };
    
    const topicSuccessConfig = {
        type: 'bar',
        data: topicSuccessData,
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa'
                    },
                    min: 0,
                    max: 100
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };
    
    new Chart(topicSuccessCtx, topicSuccessConfig);
    
    // Populate recent sessions table
    populateRecentSessions([
        { id: 'TS-1001', topic: 'Natural Language Processing', date: '2023-06-15', duration: '2.5m', status: 'completed' },
        { id: 'TS-1002', topic: 'API Integration', date: '2023-06-14', duration: '3.1m', status: 'completed' },
        { id: 'TS-1003', topic: 'Error Handling', date: '2023-06-13', duration: '4.2m', status: 'failed' },
        { id: 'TS-1004', topic: 'File Handling', date: '2023-06-12', duration: '2.8m', status: 'completed' },
        { id: 'TS-1005', topic: 'Automation', date: '2023-06-11', duration: '3.7m', status: 'completed' }
    ]);
}

// Platform Comparison Dashboard Component
function initializePlatformCharts() {
    // Initialize with default metric (success_rate)
    updatePlatformComparisonChart('success_rate');
    
    // Platform Usage Chart
    const platformUsageCtx = document.getElementById('platformUsageChart').getContext('2d');
    
    // Sample data - would come from API
    const platformUsageData = {
        labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
        datasets: [{
            data: [15, 8, 12, 4, 3],
            backgroundColor: [
                'rgba(52, 152, 219, 0.7)',
                'rgba(155, 89, 182, 0.7)',
                'rgba(46, 204, 113, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(231, 76, 60, 0.7)'
            ],
            borderColor: [
                '#3498db',
                '#9b59b6',
                '#2ecc71',
                '#f1c40f',
                '#e74c3c'
            ],
            borderWidth: 1
        }]
    };
    
    const platformUsageConfig = {
        type: 'pie',
        data: platformUsageData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#f8f9fa',
                        boxWidth: 15,
                        padding: 10
                    }
                }
            }
        }
    };
    
    new Chart(platformUsageCtx, platformUsageConfig);
    
    // Platform Performance by Topic Chart
    const platformTopicCtx = document.getElementById('platformTopicChart').getContext('2d');
    
    // Sample data - would come from API
    const platformTopicData = {
        labels: ['NLP', 'API Integration', 'File Handling', 'Error Handling', 'Automation'],
        datasets: [
            {
                label: 'GPT',
                data: [95, 82, 78, 85, 90],
                backgroundColor: 'rgba(52, 152, 219, 0.5)',
                borderColor: '#3498db',
                borderWidth: 1
            },
            {
                label: 'Claude',
                data: [92, 80, 75, 88, 85],
                backgroundColor: 'rgba(155, 89, 182, 0.5)',
                borderColor: '#9b59b6',
                borderWidth: 1
            },
            {
                label: 'Gemini',
                data: [88, 85, 82, 80, 92],
                backgroundColor: 'rgba(46, 204, 113, 0.5)',
                borderColor: '#2ecc71',
                borderWidth: 1
            }
        ]
    };
    
    const platformTopicConfig = {
        type: 'radar',
        data: platformTopicData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa',
                        backdropColor: 'transparent',
                        showLabelBackdrop: false
                    },
                    suggestedMin: 50,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f8f9fa'
                    }
                }
            }
        }
    };
    
    new Chart(platformTopicCtx, platformTopicConfig);
    
    // Populate platform cards
    populatePlatformCards([
        { 
            id: 'gpt',
            name: 'GPT',
            success_rate: 95,
            response_time: 1.8,
            quality: 4.7,
            sessions: 15,
            strength: 'General Knowledge'
        },
        { 
            id: 'claude',
            name: 'Claude',
            success_rate: 92,
            response_time: 2.1,
            quality: 4.5,
            sessions: 8,
            strength: 'Reasoning'
        },
        { 
            id: 'gemini',
            name: 'Gemini',
            success_rate: 88,
            response_time: 1.6,
            quality: 4.3,
            sessions: 12,
            strength: 'Multimodal'
        },
        { 
            id: 'deepseek',
            name: 'DeepSeek',
            success_rate: 86,
            response_time: 2.5,
            quality: 4.1,
            sessions: 4,
            strength: 'Technical Topics'
        },
        { 
            id: 'grok',
            name: 'Grok',
            success_rate: 84,
            response_time: 1.9,
            quality: 4.0,
            sessions: 3,
            strength: 'Creative Approaches'
        }
    ]);
}

// Update platform comparison chart based on selected metric
function updatePlatformComparisonChart(metric) {
    const platformComparisonCtx = document.getElementById('platformComparisonChart').getContext('2d');
    
    // First destroy existing chart if it exists
    if (window.platformComparisonChart) {
        window.platformComparisonChart.destroy();
    }
    
    // Sample data based on metric - would come from API
    let chartData, chartOptions, chartTitle;
    
    if (metric === 'success_rate') {
        chartData = {
            labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
            datasets: [{
                label: 'Success Rate (%)',
                data: [95, 92, 88, 86, 84],
                backgroundColor: 'rgba(25, 135, 84, 0.6)',
                borderColor: '#198754',
                borderWidth: 1
            }]
        };
        chartTitle = 'Success Rate by Platform (%)';
        chartOptions = {
            scales: {
                y: {
                    min: 0,
                    max: 100
                }
            }
        };
    } else if (metric === 'response_time') {
        chartData = {
            labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
            datasets: [{
                label: 'Response Time (seconds)',
                data: [1.8, 2.1, 1.6, 2.5, 1.9],
                backgroundColor: 'rgba(13, 202, 240, 0.6)',
                borderColor: '#0dcaf0',
                borderWidth: 1
            }]
        };
        chartTitle = 'Response Time by Platform (seconds)';
        chartOptions = {
            scales: {
                y: {
                    min: 0
                }
            }
        };
    } else if (metric === 'quality') {
        chartData = {
            labels: ['GPT', 'Claude', 'Gemini', 'DeepSeek', 'Grok'],
            datasets: [{
                label: 'Quality Score (0-5)',
                data: [4.7, 4.5, 4.3, 4.1, 4.0],
                backgroundColor: 'rgba(13, 110, 253, 0.6)',
                borderColor: '#0d6efd',
                borderWidth: 1
            }]
        };
        chartTitle = 'Quality Score by Platform (0-5)';
        chartOptions = {
            scales: {
                y: {
                    min: 0,
                    max: 5
                }
            }
        };
    }
    
    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: '#f8f9fa'
                }
            },
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: '#f8f9fa'
                },
                beginAtZero: true,
                ...chartOptions.scales.y
            }
        },
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: chartTitle,
                color: '#f8f9fa',
                font: {
                    size: 14
                }
            }
        }
    };
    
    // Create the new chart
    window.platformComparisonChart = new Chart(platformComparisonCtx, {
        type: 'bar',
        data: chartData,
        options: commonOptions
    });
}

// User Activity Dashboard Component
function initializeUserActivity() {
    // Activity Heatmap
    const activityHeatmapEl = document.getElementById('activityHeatmap');
    
    // Sample data - would come from API
    // Data is structured as [day_of_week, hour, value]
    // Day of week: 0 = Sunday, 6 = Saturday
    // Hour: 0-23
    const activityData = [
        { x: 'Monday', y: '10:00', value: 3 },
        { x: 'Monday', y: '14:00', value: 5 },
        { x: 'Tuesday', y: '11:00', value: 7 },
        { x: 'Wednesday', y: '09:00', value: 2 },
        { x: 'Wednesday', y: '15:00', value: 9 },
        { x: 'Thursday', y: '13:00', value: 6 },
        { x: 'Friday', y: '10:00', value: 4 },
        { x: 'Friday', y: '16:00', value: 8 },
        { x: 'Saturday', y: '12:00', value: 1 },
        { x: 'Sunday', y: '14:00', value: 3 }
    ];
    
    // Transform data for heatmap
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'];
    
    // Create a full data set with zeros for missing values
    const fullData = [];
    for (let day of days) {
        for (let hour of hours) {
            // Find if we have data for this day/hour
            const existingData = activityData.find(d => d.x === day && d.y === hour);
            if (existingData) {
                fullData.push(existingData.value);
            } else {
                fullData.push(0);
            }
        }
    }
    
    // Create heatmap using ApexCharts
    const heatmapOptions = {
        series: days.map((day, dayIndex) => {
            return {
                name: day,
                data: fullData.slice(dayIndex * 24, (dayIndex + 1) * 24)
            };
        }),
        chart: {
            height: 350,
            type: 'heatmap',
            background: 'transparent',
            toolbar: {
                show: false
            }
        },
        dataLabels: {
            enabled: false
        },
        colors: ["#0d6efd"],
        xaxis: {
            categories: hours,
            labels: {
                show: true,
                rotate: -45,
                style: {
                    colors: '#f8f9fa'
                }
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false
            }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#f8f9fa'
                }
            }
        },
        plotOptions: {
            heatmap: {
                colorScale: {
                    ranges: [{
                        from: 0,
                        to: 0,
                        color: '#212529',
                        name: 'none',
                    }, {
                        from: 1,
                        to: 3,
                        color: 'rgba(13, 110, 253, 0.3)',
                        name: 'low',
                    }, {
                        from: 4,
                        to: 6,
                        color: 'rgba(13, 110, 253, 0.5)',
                        name: 'medium',
                    }, {
                        from: 7,
                        to: 9,
                        color: 'rgba(13, 110, 253, 0.8)',
                        name: 'high',
                    }]
                }
            }
        },
        tooltip: {
            theme: 'dark',
            y: {
                formatter: function(value) {
                    return value === 0 ? 'No activity' : value + ' sessions';
                }
            }
        },
        title: {
            text: 'Activity by Day and Hour',
            align: 'center',
            style: {
                color: '#f8f9fa'
            }
        }
    };
    
    const heatmapChart = new ApexCharts(activityHeatmapEl, heatmapOptions);
    heatmapChart.render();
    
    // Feature Usage Chart
    const featureUsageCtx = document.getElementById('featureUsageChart').getContext('2d');
    
    // Sample data - would come from API
    const featureUsageData = {
        labels: ['Training', 'Analytics', 'Logs', 'Settings', 'Recommendations'],
        datasets: [{
            label: 'Usage Count',
            data: [45, 32, 28, 15, 20],
            backgroundColor: [
                'rgba(13, 110, 253, 0.7)',
                'rgba(25, 135, 84, 0.7)',
                'rgba(255, 193, 7, 0.7)',
                'rgba(13, 202, 240, 0.7)',
                'rgba(111, 66, 193, 0.7)'
            ],
            borderColor: [
                '#0d6efd',
                '#198754',
                '#ffc107',
                '#0dcaf0',
                '#6f42c1'
            ],
            borderWidth: 1
        }]
    };
    
    const featureUsageConfig = {
        type: 'polarArea',
        data: featureUsageData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    ticks: {
                        color: '#f8f9fa',
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#f8f9fa'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#f8f9fa',
                        boxWidth: 15,
                        padding: 10
                    }
                }
            }
        }
    };
    
    new Chart(featureUsageCtx, featureUsageConfig);
    
    // Update user activity metrics
    updateUserActivityMetrics({
        current_streak: 5,
        max_streak: 10,
        days_active_week: 4,
        days_active_month: 16,
        topics_explored: 3,
        topics_total: 5,
        platforms_explored: 4,
        platforms_total: 5,
        achievements: 7,
        achievements_total: 20
    });
}

// Update user activity metrics
function updateUserActivityMetrics(metrics) {
    // Streak progress
    document.getElementById('currentStreakValue').textContent = metrics.current_streak;
    const streakProgress = (metrics.current_streak / metrics.max_streak) * 100;
    document.getElementById('streakProgressBar').style.width = streakProgress + '%';
    
    // Active days
    document.getElementById('daysActiveWeekValue').textContent = metrics.days_active_week;
    document.getElementById('daysActiveMonthValue').textContent = metrics.days_active_month;
    
    // Learning progress
    document.getElementById('topicsExploredValue').textContent = `${metrics.topics_explored}/${metrics.topics_total}`;
    const topicsProgress = (metrics.topics_explored / metrics.topics_total) * 100;
    document.getElementById('topicsProgressBar').style.width = topicsProgress + '%';
    
    document.getElementById('platformsExploredValue').textContent = `${metrics.platforms_explored}/${metrics.platforms_total}`;
    const platformsProgress = (metrics.platforms_explored / metrics.platforms_total) * 100;
    document.getElementById('platformsProgressBar').style.width = platformsProgress + '%';
    
    document.getElementById('achievementsValue').textContent = `${metrics.achievements}/${metrics.achievements_total}`;
    const achievementsProgress = (metrics.achievements / metrics.achievements_total) * 100;
    document.getElementById('achievementsProgressBar').style.width = achievementsProgress + '%';
}

// Insights Dashboard Component
function initializeInsights() {
    // Performance Gauge
    const performanceGaugeCtx = document.getElementById('performanceGauge').getContext('2d');
    
    // Sample data - would come from API
    const performanceScore = 76;
    
    // Determine color based on performance score
    let gaugeColor = '#dc3545'; // Danger/red
    let performanceLabel = 'Needs Improvement';
    
    if (performanceScore >= 80) {
        gaugeColor = '#198754'; // Success/green
        performanceLabel = 'Excellent';
    } else if (performanceScore >= 60) {
        gaugeColor = '#0d6efd'; // Primary/blue
        performanceLabel = 'Good';
    } else if (performanceScore >= 40) {
        gaugeColor = '#ffc107'; // Warning/yellow
        performanceLabel = 'Average';
    }
    
    const gaugeConfig = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [performanceScore, 100 - performanceScore],
                backgroundColor: [gaugeColor, '#2a2a2a'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                }
            }
        }
    };
    
    new Chart(performanceGaugeCtx, gaugeConfig);
    document.getElementById('performanceScoreValue').textContent = performanceScore;
    document.getElementById('performanceLabel').textContent = performanceLabel;
    
    // Populate recommendations
    populateRecommendations([
        {
            type: 'new_topic',
            title: 'Explore Error Handling',
            description: 'You haven\'t trained AutoDev on error handling yet. This could enhance its self-recovery capabilities.',
            action: 'start_training',
            action_params: { topic: 'error_handling' },
            relevance: 0.9
        },
        {
            type: 'platform_diversity',
            title: 'Include Claude in Sessions',
            description: 'Claude offers unique reasoning capabilities that could complement your existing training approach.',
            action: 'learn_more',
            action_params: { platform: 'claude' },
            relevance: 0.85
        },
        {
            type: 'optimization',
            title: 'Longer Training Sessions',
            description: 'Your training sessions are shorter than optimal. Consider adding more detailed prompts.',
            action: 'view_guide',
            action_params: { guide: 'effective_prompting' },
            relevance: 0.8
        }
    ]);
}

// AI Assistant Dashboard Component
function initializeAssistant() {
    // This is just the UI setup, actual assistant functionality
    // would be implemented separately
}

// Helper function to populate recent sessions table
function populateRecentSessions(sessions) {
    const tbody = document.getElementById('recentSessionsTable');
    tbody.innerHTML = '';
    
    sessions.forEach(session => {
        const row = document.createElement('tr');
        
        // Status badge class
        let statusBadgeClass = 'bg-success';
        if (session.status === 'failed') {
            statusBadgeClass = 'bg-danger';
        } else if (session.status === 'in_progress') {
            statusBadgeClass = 'bg-warning';
        }
        
        row.innerHTML = `
            <td>${session.id}</td>
            <td>${session.topic}</td>
            <td>${session.date}</td>
            <td>${session.duration}</td>
            <td><span class="badge ${statusBadgeClass}">${session.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-info">View</button>
                ${session.status === 'completed' ? '<button class="btn btn-sm btn-outline-success">Apply</button>' : ''}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Helper function to populate platform cards
function populatePlatformCards(platforms) {
    const container = document.getElementById('platformCards');
    container.innerHTML = '';
    
    platforms.forEach(platform => {
        const card = document.createElement('div');
        card.className = 'col-md-4 col-lg-2-4 mb-3'; // 2-4 would be custom class for 20% width
        
        // Use different colors for each platform
        let platformColor;
        switch(platform.id) {
            case 'gpt': platformColor = '#3498db'; break;
            case 'claude': platformColor = '#9b59b6'; break;
            case 'gemini': platformColor = '#2ecc71'; break;
            case 'deepseek': platformColor = '#f1c40f'; break;
            case 'grok': platformColor = '#e74c3c'; break;
            default: platformColor = '#3498db';
        }
        
        card.innerHTML = `
            <div class="card border-0 dashboard-card h-100">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="fas fa-robot me-2" style="color: ${platformColor}"></i>
                        ${platform.name}
                    </h5>
                    <div class="small">
                        <div class="d-flex justify-content-between mb-1">
                            <span>Success Rate:</span>
                            <span class="fw-bold">${platform.success_rate}%</span>
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                            <span>Response Time:</span>
                            <span class="fw-bold">${platform.response_time}s</span>
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                            <span>Quality Score:</span>
                            <span class="fw-bold">${platform.quality}/5</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Sessions:</span>
                            <span class="fw-bold">${platform.sessions}</span>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <small class="text-muted">Strength: ${platform.strength}</small>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Helper function to populate recommendations
function populateRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-3';
        
        // Determine badge color and action button based on recommendation type
        let badgeClass, actionText;
        
        switch(rec.type) {
            case 'new_topic':
                badgeClass = 'bg-info';
                actionText = 'Start Training';
                break;
            case 'platform_diversity':
                badgeClass = 'bg-warning';
                actionText = 'Learn More';
                break;
            case 'optimization':
                badgeClass = 'bg-success';
                actionText = 'View Guide';
                break;
            case 'advanced_training':
                badgeClass = 'bg-primary';
                actionText = 'Advanced Training';
                break;
            case 'skill_gap':
                badgeClass = 'bg-danger';
                actionText = 'Fill Gap';
                break;
            default:
                badgeClass = 'bg-secondary';
                actionText = 'View Details';
        }
        
        card.innerHTML = `
            <div class="card border-0 bg-dark h-100">
                <div class="card-body">
                    <span class="badge ${badgeClass} mb-2">${rec.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                    <h6 class="card-title">${rec.title}</h6>
                    <p class="card-text small">${rec.description}</p>
                </div>
                <div class="card-footer bg-transparent border-0">
                    <button class="btn btn-sm btn-outline-info" data-action="${rec.action}" data-params='${JSON.stringify(rec.action_params)}'>${actionText}</button>
                </div>
            </div>
        `;
        
        // Add click handler to the action button
        card.querySelector('button').addEventListener('click', function() {
            const action = this.dataset.action;
            const params = JSON.parse(this.dataset.params);
            
            handleRecommendationAction(action, params);
        });
        
        container.appendChild(card);
    });
}

// Handle recommendation action
function handleRecommendationAction(action, params) {
    console.log(`Handling action: ${action}`, params);
    
    // In a real application, this would navigate to the appropriate page
    // or trigger the appropriate action
    
    switch(action) {
        case 'start_training':
            // Redirect to training page with topic pre-selected
            window.location.href = `/training?topic=${params.topic}`;
            break;
        case 'learn_more':
            // Show modal or redirect to documentation
            alert(`This would show more information about ${params.platform || params.topic}`);
            break;
        case 'view_guide':
            // Redirect to guide page
            alert(`This would show the guide for ${params.guide}`);
            break;
        default:
            console.log('Unknown action:', action);
    }
}

// Set up the chat assistant interface
function setupChatbox() {
    const chatbox = document.getElementById('assistantChatbox');
    const chatboxHeader = document.getElementById('chatboxHeader');
    const minimizeBtn = document.getElementById('minimizeChatBtn');
    const toggleIcon = document.getElementById('chatToggleIcon');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');
    
    // Toggle chatbox
    chatboxHeader.addEventListener('click', function() {
        chatbox.classList.toggle('chatbox-minimized');
        
        if (chatbox.classList.contains('chatbox-minimized')) {
            toggleIcon.classList.remove('fa-chevron-down');
            toggleIcon.classList.add('fa-chevron-up');
        } else {
            toggleIcon.classList.remove('fa-chevron-up');
            toggleIcon.classList.add('fa-chevron-down');
        }
    });
    
    // Send message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        const userMessageEl = document.createElement('div');
        userMessageEl.className = 'chat-message user-message';
        userMessageEl.textContent = message;
        chatMessages.appendChild(userMessageEl);
        
        // Clear input
        chatInput.value = '';
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // In a real application, this would call the assistant API
        // For demo, just show a simulated response after a delay
        setTimeout(() => {
            const responseEl = document.createElement('div');
            responseEl.className = 'chat-message assistant-message';
            
            // Simple pattern matching for demo
            let responseText;
            if (message.toLowerCase().includes('success rate')) {
                responseText = "Success rate measures how many training sessions complete successfully. Your current rate of 87% is quite good! To improve it further, try using more detailed prompts and including diverse AI platforms in your sessions.";
            } else if (message.toLowerCase().includes('platform') && message.toLowerCase().includes('best')) {
                responseText = "Each platform has different strengths. GPT excels at general knowledge tasks, while Claude is better at reasoning. Gemini performs well on multimodal inputs. You can see detailed comparisons in the Platforms tab of this dashboard.";
            } else if (message.toLowerCase().includes('improve')) {
                responseText = "To improve your training effectiveness, consider: 1) Using more diverse AI platforms, 2) Exploring topics you haven't trained on yet, 3) Creating more detailed prompts, and 4) Applying successful training results to AutoDev promptly.";
            } else {
                responseText = "I can help you interpret your analytics data and suggest ways to improve your training approach. Would you like to know more about success rates, platform comparisons, or improvement strategies?";
            }
            
            responseEl.innerHTML = responseText;
            
            // Add suggestion chips
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'suggestion-chips';
            
            const suggestions = [
                "Show best platform",
                "Improve success rate",
                "Analyze my data"
            ];
            
            suggestions.forEach(suggestion => {
                const chip = document.createElement('button');
                chip.className = 'suggestion-chip';
                chip.textContent = suggestion;
                chip.addEventListener('click', function() {
                    chatInput.value = suggestion;
                    sendMessage();
                });
                suggestionsDiv.appendChild(chip);
            });
            
            responseEl.appendChild(suggestionsDiv);
            chatMessages.appendChild(responseEl);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);
    }
    
    sendChatBtn.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Handle suggestion chips
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-chip')) {
            const suggestion = e.target.textContent;
            chatInput.value = suggestion;
            sendMessage();
        }
    });
}

// Refresh dashboard data
function refreshDashboardData() {
    // Show loading spinner
    document.getElementById('refreshButton').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
    
    // In a real application, this would make API calls to fetch the latest data
    // For demo, just simulate a delay
    setTimeout(() => {
        // Reinitialize all dashboard components with fresh data
        initializeSystemHealth();
        initializeKeyMetrics();
        initializeTrainingCharts();
        initializePlatformCharts();
        initializeUserActivity();
        initializeInsights();
        
        // Restore button text
        document.getElementById('refreshButton').innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Data';
        
        // Show success toast
        showToast('Data refreshed successfully', 'success');
    }, 1500);
}

// Refresh recommendations
function refreshRecommendations() {
    // Show loading state
    document.getElementById('refreshRecommendations').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    
    // In a real application, this would make an API call to get fresh recommendations
    // For demo, just simulate a delay
    setTimeout(() => {
        // Sample recommendations - in a real app, these would come from the API
        const recommendations = [
            {
                type: 'new_topic',
                title: 'Try File Handling Training',
                description: 'You haven\'t explored file handling capabilities yet. This would enhance AutoDev\'s ability to process data files.',
                action: 'start_training',
                action_params: { topic: 'file_handling' },
                relevance: 0.92
            },
            {
                type: 'advanced_training',
                title: 'Advanced NLP Training',
                description: 'You\'ve had great results with NLP. Take it further with specialized training on entity extraction.',
                action: 'start_training',
                action_params: { topic: 'natural_language', advanced: true },
                relevance: 0.88
            },
            {
                type: 'skill_gap',
                title: 'Improve Error Recovery',
                description: 'Analysis shows AutoDev could benefit from better error recovery strategies. Focus on this area next.',
                action: 'learn_skill',
                action_params: { skill: 'error_recovery' },
                relevance: 0.85
            }
        ];
        
        // Update recommendations display
        populateRecommendations(recommendations);
        
        // Restore button text
        document.getElementById('refreshRecommendations').innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        
        // Show success toast
        showToast('Recommendations refreshed with new insights', 'success');
    }, 1500);
}

// Save dashboard settings
function saveSettings() {
    const refreshInterval = document.getElementById('refreshInterval').value;
    const chartAnimation = document.getElementById('chartAnimation').checked;
    const showAssistant = document.getElementById('showAssistant').checked;
    const dashboardTheme = document.getElementById('dashboardTheme').value;
    
    // In a real application, this would save settings to the server
    // For demo, just log the settings and show a success message
    console.log('Saving settings:', {
        refreshInterval,
        chartAnimation,
        showAssistant,
        dashboardTheme
    });
    
    // Apply settings immediately
    if (showAssistant) {
        document.getElementById('assistantChatbox').style.display = 'block';
    } else {
        document.getElementById('assistantChatbox').style.display = 'none';
    }
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal.hide();
    
    // Show success toast
    showToast('Settings saved successfully', 'success');
}

// Export dashboard data
function exportData(dataType) {
    // In a real application, this would generate and download the data file
    // For demo, just show a message
    showToast(`Exporting ${dataType} data...`, 'info');
    
    // Simulate download after delay
    setTimeout(() => {
        showToast(`${dataType}.csv downloaded successfully`, 'success');
    }, 1500);
}

// Check if auto-refresh is enabled and set up interval
function checkAutoRefresh() {
    // In a real app, this would load from saved settings
    const refreshInterval = 60; // seconds
    
    if (refreshInterval > 0) {
        // Set up auto-refresh
        setInterval(() => {
            refreshDashboardData();
        }, refreshInterval * 1000);
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}