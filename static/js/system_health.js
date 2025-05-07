/**
 * Synapse Chamber - System Health Dashboard
 * Provides real-time monitoring of system performance and component status
 * Part of the Synapse Chamber UX enhancement project
 */

class SystemHealthDashboard {
    constructor(options = {}) {
        // Configuration
        this.config = {
            updateInterval: options.updateInterval || 5000, // Update interval in ms
            containerSelector: options.containerSelector || '#system-health-dashboard',
            apiEndpoint: options.apiEndpoint || '/api/system-health',
            showDetailedMetrics: options.showDetailedMetrics || false,
            enableAlerts: options.enableAlerts || true,
            alertThreshold: options.alertThreshold || 0.7 // 70% threshold for warnings
        };
        
        // Initialize component states
        this.componentStatus = {
            memory: { status: 'unknown', metrics: {} },
            browser: { status: 'unknown', metrics: {} },
            database: { status: 'unknown', metrics: {} },
            ai: { 
                status: 'unknown', 
                platforms: {
                    gpt: { status: 'unknown', last_success: null },
                    claude: { status: 'unknown', last_success: null },
                    gemini: { status: 'unknown', last_success: null },
                    grok: { status: 'unknown', last_success: null },
                    deepseek: { status: 'unknown', last_success: null }
                }
            },
            system: { status: 'unknown', metrics: {} }
        };
        
        // Chart references
        this.charts = {};
        
        // Performance history
        this.performanceHistory = {
            timestamps: [],
            memory: [],
            cpu: [],
            requests: [],
            errors: []
        };
        
        // Initialize the dashboard
        this.init();
    }
    
    /**
     * Initialize the dashboard
     */
    init() {
        // Initialize on document ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    /**
     * Setup dashboard components and start monitoring
     */
    setup() {
        // Find or create container
        this.container = document.querySelector(this.config.containerSelector);
        if (!this.container) {
            console.warn(`System health dashboard container ${this.config.containerSelector} not found.`);
            return;
        }
        
        // Create dashboard structure
        this.createDashboardStructure();
        
        // Setup charts
        this.setupCharts();
        
        // Initial data fetch
        this.fetchHealthData();
        
        // Start update interval
        this.updateInterval = setInterval(() => {
            this.fetchHealthData();
        }, this.config.updateInterval);
        
        // Add event listeners
        this.setupEventListeners();
    }
    
    /**
     * Create the HTML structure for the dashboard
     */
    createDashboardStructure() {
        this.container.innerHTML = `
            <div class="system-health-container">
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card health-summary-card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">System Health Overview</h5>
                                <div class="overall-health-indicator">
                                    <div class="health-status">
                                        <span class="status-indicator unknown"></span>
                                        <span class="status-text">Unknown</span>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row health-indicators">
                                    <div class="col-md-2 col-sm-4 col-6 mb-3">
                                        <div class="health-component memory" data-tooltip="top" data-tooltip-category="system" data-tooltip-id="memory_usage">
                                            <div class="component-icon">
                                                <i class="fas fa-memory"></i>
                                            </div>
                                            <div class="component-name">Memory</div>
                                            <div class="component-status">
                                                <span class="status-indicator unknown"></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-2 col-sm-4 col-6 mb-3">
                                        <div class="health-component browser" data-tooltip="top" data-tooltip-category="system" data-tooltip-id="driver_status">
                                            <div class="component-icon">
                                                <i class="fas fa-globe"></i>
                                            </div>
                                            <div class="component-name">Browser</div>
                                            <div class="component-status">
                                                <span class="status-indicator unknown"></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-2 col-sm-4 col-6 mb-3">
                                        <div class="health-component database">
                                            <div class="component-icon">
                                                <i class="fas fa-database"></i>
                                            </div>
                                            <div class="component-name">Database</div>
                                            <div class="component-status">
                                                <span class="status-indicator unknown"></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-2 col-sm-4 col-6 mb-3">
                                        <div class="health-component ai">
                                            <div class="component-icon">
                                                <i class="fas fa-robot"></i>
                                            </div>
                                            <div class="component-name">AI Platforms</div>
                                            <div class="component-status">
                                                <span class="status-indicator unknown"></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-2 col-sm-4 col-6 mb-3">
                                        <div class="health-component system">
                                            <div class="component-icon">
                                                <i class="fas fa-server"></i>
                                            </div>
                                            <div class="component-name">System</div>
                                            <div class="component-status">
                                                <span class="status-indicator unknown"></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Performance Metrics</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="performance-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Resource Usage</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="resource-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <div class="card ai-platforms-card">
                            <div class="card-header">
                                <h5 class="mb-0">AI Platforms Status</h5>
                            </div>
                            <div class="card-body">
                                <div class="ai-platforms-status">
                                    <div class="platform-status" data-platform="gpt">
                                        <div class="platform-name">ChatGPT</div>
                                        <div class="platform-indicator">
                                            <span class="status-indicator unknown"></span>
                                        </div>
                                        <div class="platform-details">
                                            <span class="last-success">Unknown</span>
                                        </div>
                                    </div>
                                    <div class="platform-status" data-platform="claude">
                                        <div class="platform-name">Claude</div>
                                        <div class="platform-indicator">
                                            <span class="status-indicator unknown"></span>
                                        </div>
                                        <div class="platform-details">
                                            <span class="last-success">Unknown</span>
                                        </div>
                                    </div>
                                    <div class="platform-status" data-platform="gemini">
                                        <div class="platform-name">Gemini</div>
                                        <div class="platform-indicator">
                                            <span class="status-indicator unknown"></span>
                                        </div>
                                        <div class="platform-details">
                                            <span class="last-success">Unknown</span>
                                        </div>
                                    </div>
                                    <div class="platform-status" data-platform="grok">
                                        <div class="platform-name">Grok</div>
                                        <div class="platform-indicator">
                                            <span class="status-indicator unknown"></span>
                                        </div>
                                        <div class="platform-details">
                                            <span class="last-success">Unknown</span>
                                        </div>
                                    </div>
                                    <div class="platform-status" data-platform="deepseek">
                                        <div class="platform-name">DeepSeek</div>
                                        <div class="platform-indicator">
                                            <span class="status-indicator unknown"></span>
                                        </div>
                                        <div class="platform-details">
                                            <span class="last-success">Unknown</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="card activity-log-card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">System Activity Log</h5>
                                <button class="btn btn-sm btn-outline-secondary refresh-log">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                            <div class="card-body">
                                <div class="activity-log-container">
                                    <div class="activity-log">
                                        <div class="log-entry">
                                            <span class="timestamp">00:00:00</span>
                                            <span class="log-type info">INFO</span>
                                            <span class="log-message">System health monitoring started.</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add the dashboard styles
        this.addStyles();
    }
    
    /**
     * Add required CSS styles
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .system-health-container {
                font-family: var(--bs-font-sans-serif);
            }
            
            .health-summary-card {
                border-left: 4px solid var(--bs-secondary);
            }
            
            .health-indicators {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .health-component {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 15px 10px;
                text-align: center;
                border-radius: 8px;
                transition: all 0.2s;
                cursor: pointer;
            }
            
            .health-component:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            
            .component-icon {
                font-size: 24px;
                margin-bottom: 8px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            .component-name {
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 5px;
            }
            
            .status-indicator.healthy {
                background-color: #28a745;
                box-shadow: 0 0 8px rgba(40, 167, 69, 0.6);
            }
            
            .status-indicator.warning {
                background-color: #ffc107;
                box-shadow: 0 0 8px rgba(255, 193, 7, 0.6);
            }
            
            .status-indicator.critical {
                background-color: #dc3545;
                box-shadow: 0 0 8px rgba(220, 53, 69, 0.6);
            }
            
            .status-indicator.unknown {
                background-color: #6c757d;
                box-shadow: 0 0 8px rgba(108, 117, 125, 0.6);
            }
            
            .overall-health-indicator {
                font-size: 16px;
                font-weight: 500;
            }
            
            .health-status {
                display: flex;
                align-items: center;
            }
            
            .chart-container {
                position: relative;
                height: 200px;
            }
            
            .ai-platforms-status {
                display: flex;
                flex-direction: column;
            }
            
            .platform-status {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
                padding: 5px 10px;
                border-radius: 4px;
                border-left: 3px solid transparent;
            }
            
            .platform-status[data-platform="gpt"] {
                border-left-color: #10a37f;
            }
            
            .platform-status[data-platform="claude"] {
                border-left-color: #8a3ffc;
            }
            
            .platform-status[data-platform="gemini"] {
                border-left-color: #4285f4;
            }
            
            .platform-status[data-platform="grok"] {
                border-left-color: #1DA1F2;
            }
            
            .platform-status[data-platform="deepseek"] {
                border-left-color: #ff6b6b;
            }
            
            .platform-name {
                flex: 0 0 100px;
                font-weight: 500;
            }
            
            .platform-indicator {
                margin: 0 15px;
            }
            
            .platform-details {
                flex: 1;
                font-size: 12px;
                color: var(--bs-secondary);
            }
            
            .activity-log-container {
                height: 200px;
                overflow-y: auto;
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            }
            
            .log-entry {
                margin-bottom: 4px;
                white-space: pre-wrap;
                word-break: break-word;
            }
            
            .timestamp {
                color: var(--bs-secondary);
                margin-right: 8px;
            }
            
            .log-type {
                display: inline-block;
                width: 60px;
                padding: 0 5px;
                border-radius: 3px;
                margin-right: 8px;
                text-align: center;
                font-weight: bold;
            }
            
            .log-type.info {
                background-color: rgba(0, 123, 255, 0.2);
                color: #0056b3;
            }
            
            .log-type.warning {
                background-color: rgba(255, 193, 7, 0.2);
                color: #d39e00;
            }
            
            .log-type.error {
                background-color: rgba(220, 53, 69, 0.2);
                color: #a71d2a;
            }
            
            .log-type.success {
                background-color: rgba(40, 167, 69, 0.2);
                color: #1e7e34;
            }
            
            @media (max-width: 768px) {
                .component-icon {
                    font-size: 18px;
                    width: 32px;
                    height: 32px;
                }
                
                .component-name {
                    font-size: 12px;
                }
                
                .platform-name {
                    flex: 0 0 80px;
                    font-size: 12px;
                }
                
                .platform-details {
                    font-size: 10px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Set up chart.js charts
     */
    setupCharts() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js is required for the system health dashboard charts');
            return;
        }
        
        // Performance chart - Line chart showing performance over time
        const performanceCtx = document.getElementById('performance-chart');
        this.charts.performance = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.2)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Error Rate (%)',
                        data: [],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.2)',
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        },
                        min: 0
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Error Rate (%)'
                        },
                        min: 0,
                        max: 100,
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
        
        // Resource chart - Doughnut chart showing resource usage
        const resourceCtx = document.getElementById('resource-chart');
        this.charts.resource = new Chart(resourceCtx, {
            type: 'doughnut',
            data: {
                labels: ['Memory Used', 'Memory Free', 'CPU Usage', 'CPU Idle'],
                datasets: [{
                    data: [0, 100, 0, 100],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(52, 152, 219, 0.2)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(231, 76, 60, 0.2)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw}%`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Refresh log button
        const refreshBtn = this.container.querySelector('.refresh-log');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.fetchHealthData(true); // Force refresh
            });
        }
        
        // Component click handlers for detailed info
        const components = this.container.querySelectorAll('.health-component');
        components.forEach(component => {
            component.addEventListener('click', (e) => {
                const componentType = component.classList[1]; // e.g., 'memory', 'browser'
                this.showComponentDetails(componentType);
            });
        });
    }
    
    /**
     * Fetch health data from the API
     */
    fetchHealthData(forceRefresh = false) {
        // For demo/development, use mock data
        // In production, uncomment the fetch code and use real API
        
        /* 
        fetch(this.config.apiEndpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.updateDashboard(data);
            })
            .catch(error => {
                console.error('Error fetching health data:', error);
                this.logActivity('error', `Failed to fetch health data: ${error.message}`);
            });
        */
        
        // For development: Generate mock data
        const mockData = this.generateMockHealthData();
        this.updateDashboard(mockData);
    }
    
    /**
     * Generate mock health data for development/testing
     */
    generateMockHealthData() {
        // Random helper
        const random = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);
        
        // Generate statuses with weighted randomness (mostly healthy)
        const generateStatus = () => {
            const rand = Math.random();
            if (rand > 0.85) return 'warning';
            if (rand > 0.95) return 'critical';
            return 'healthy';
        };
        
        // AI platform status with time drift (platforms degrade over time)
        const now = new Date();
        const timeDrift = Math.sin(now.getMinutes() / 60 * Math.PI) * 0.5 + 0.5; // 0-1 value that cycles every hour
        
        const aiPlatformStatus = (platform) => {
            // Some platforms are more reliable than others in this simulation
            const reliability = {
                gpt: 0.9,
                claude: 0.85,
                gemini: 0.8,
                grok: 0.75,
                deepseek: 0.7
            };
            
            const baseReliability = reliability[platform] || 0.8;
            const adjustedReliability = baseReliability - (timeDrift * 0.3); // Reduce reliability as time drifts
            
            const rand = Math.random();
            let status = 'healthy';
            
            if (rand > adjustedReliability) {
                status = 'warning';
            }
            if (rand > adjustedReliability + 0.15) {
                status = 'critical';
            }
            
            // Last success time (more recent for healthier platforms)
            let lastSuccess = null;
            if (status === 'healthy') {
                // Within the last 5 minutes
                lastSuccess = new Date(now - random(1, 300) * 1000);
            } else if (status === 'warning') {
                // Between 5 and 30 minutes ago
                lastSuccess = new Date(now - random(300, 1800) * 1000);
            } else {
                // Over 30 minutes ago
                lastSuccess = new Date(now - random(1800, 7200) * 1000);
            }
            
            return {
                status: status,
                last_success: lastSuccess,
                success_rate: Math.round((adjustedReliability) * 100)
            };
        };
        
        // Memory usage increases over time (simulating memory leak or load)
        const memoryBaseline = 40; // Starting around 40%
        const memoryVariation = 20; // Can go up or down by 20%
        const memoryUsage = Math.min(95, Math.max(10, 
            memoryBaseline + (timeDrift * memoryVariation) + random(-5, 5)
        ));
        
        // CPU follows a different pattern with short spikes
        const cpuBaseline = 30;
        const cpuSpike = Math.random() > 0.8 ? random(20, 50) : 0; // Occasional CPU spikes
        const cpuUsage = Math.min(95, Math.max(5, 
            cpuBaseline + cpuSpike + random(-10, 10)
        ));
        
        // Determine component statuses based on metrics
        const memoryStatus = memoryUsage > 80 ? 'critical' : (memoryUsage > 60 ? 'warning' : 'healthy');
        const cpuStatus = cpuUsage > 80 ? 'critical' : (cpuUsage > 60 ? 'warning' : 'healthy');
        
        // Browser driver status (more stable)
        const browserStatus = Math.random() > 0.9 ? 'warning' : 'healthy';
        
        // Database status (very stable)
        const dbStatus = Math.random() > 0.95 ? 'warning' : 'healthy';
        
        // Generate log entries
        const logTypes = ['info', 'warning', 'error', 'success'];
        const logMessages = [
            'System health check completed',
            'Memory usage above threshold',
            'CPU usage spiked temporarily',
            'Database connection pool expanded',
            'Browser driver reinitialized',
            'Failed to connect to platform API',
            'Automatic memory optimization triggered',
            'Session cleanup completed',
            'User login attempt failed',
            'Training session completed successfully'
        ];
        
        const randomLogEntry = () => {
            const type = logTypes[random(0, logTypes.length - 1)];
            const message = logMessages[random(0, logMessages.length - 1)];
            const timestamp = new Date(now - random(0, 3600) * 1000);
            
            return {
                type,
                message,
                timestamp: timestamp.toISOString()
            };
        };
        
        const logEntries = Array(10).fill(0).map(() => randomLogEntry())
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Generate performance metrics history
        const generateTimePoint = (minutes) => {
            const time = new Date(now.getTime() - minutes * 60000);
            return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        };
        
        const timePoints = Array(12).fill(0).map((_, i) => generateTimePoint(60 - i * 5));
        
        // Response time increases with memory usage
        const responseTimeBase = 200; // ms
        const responseTimeFactor = 5; // multiplier
        const responseTime = Array(12).fill(0).map((_, i) => {
            const memUsage = Math.min(95, Math.max(10, 
                memoryBaseline + (i/12 * memoryVariation) + random(-5, 5)
            ));
            return responseTimeBase + (memUsage * responseTimeFactor) + random(-50, 50);
        });
        
        // Error rate increases dramatically with memory pressure
        const errorRate = Array(12).fill(0).map((_, i) => {
            const memUsage = Math.min(95, Math.max(10, 
                memoryBaseline + (i/12 * memoryVariation) + random(-5, 5)
            ));
            // Exponential error rate increase above 70% memory
            return memUsage > 70 ? 
                   Math.min(100, Math.pow(memUsage - 70, 1.5) + random(0, 5)) : 
                   random(0, 2);
        });
        
        // Build the complete mock data object
        return {
            timestamp: now.toISOString(),
            overall_status: Math.max(memoryUsage, cpuUsage) > 80 ? 'critical' : 
                          (Math.max(memoryUsage, cpuUsage) > 60 ? 'warning' : 'healthy'),
            components: {
                memory: {
                    status: memoryStatus,
                    metrics: {
                        usage_percent: memoryUsage,
                        total_mb: 8192,
                        used_mb: Math.round(8192 * memoryUsage / 100),
                        free_mb: Math.round(8192 * (100 - memoryUsage) / 100)
                    }
                },
                browser: {
                    status: browserStatus,
                    metrics: {
                        driver_status: browserStatus,
                        instance_count: random(1, 3),
                        pages_loaded: random(10, 100),
                        error_count: browserStatus === 'healthy' ? random(0, 2) : random(3, 10)
                    }
                },
                database: {
                    status: dbStatus,
                    metrics: {
                        connection_count: random(5, 20),
                        query_time_avg_ms: random(10, 50),
                        active_transactions: random(0, 5),
                        pool_size: random(10, 30),
                        pool_used: random(1, 9)
                    }
                },
                ai: {
                    status: Math.random() > 0.7 ? 'warning' : 'healthy',
                    platforms: {
                        gpt: aiPlatformStatus('gpt'),
                        claude: aiPlatformStatus('claude'),
                        gemini: aiPlatformStatus('gemini'),
                        grok: aiPlatformStatus('grok'),
                        deepseek: aiPlatformStatus('deepseek')
                    },
                    metrics: {
                        total_requests: random(100, 1000),
                        success_rate: random(70, 99),
                        avg_response_time_ms: random(500, 3000)
                    }
                },
                system: {
                    status: Math.max(cpuStatus, memoryStatus) === 'critical' ? 'critical' : 
                           (Math.max(cpuStatus, memoryStatus) === 'warning' ? 'warning' : 'healthy'),
                    metrics: {
                        cpu_usage_percent: cpuUsage,
                        load_avg_1m: (cpuUsage / 100 * 4).toFixed(2),
                        load_avg_5m: ((cpuUsage - 10) / 100 * 4).toFixed(2),
                        load_avg_15m: ((cpuUsage - 15) / 100 * 4).toFixed(2),
                        uptime_seconds: 3600 * random(1, 72)
                    }
                }
            },
            logs: logEntries,
            performance_history: {
                timestamps: timePoints,
                response_time_ms: responseTime,
                error_rate_percent: errorRate
            }
        };
    }
    
    /**
     * Update the dashboard with new data
     */
    updateDashboard(data) {
        // Update component status
        this.updateComponentStatus('memory', data.components.memory);
        this.updateComponentStatus('browser', data.components.browser);
        this.updateComponentStatus('database', data.components.database);
        this.updateComponentStatus('ai', data.components.ai);
        this.updateComponentStatus('system', data.components.system);
        
        // Update overall system status
        this.updateOverallStatus(data.overall_status);
        
        // Update AI platform statuses
        this.updateAIPlatforms(data.components.ai.platforms);
        
        // Update charts
        this.updateCharts(data);
        
        // Update logs
        this.updateActivityLog(data.logs);
        
        // Store data for history tracking
        this.storePerformanceHistory(data);
        
        // Log update
        this.logActivity('info', 'Dashboard updated with latest metrics');
    }
    
    /**
     * Update a component's status display
     */
    updateComponentStatus(componentName, data) {
        const componentElement = this.container.querySelector(`.health-component.${componentName}`);
        if (!componentElement) return;
        
        const statusIndicator = componentElement.querySelector('.status-indicator');
        if (!statusIndicator) return;
        
        // Remove all status classes
        statusIndicator.classList.remove('healthy', 'warning', 'critical', 'unknown');
        
        // Add the current status class
        statusIndicator.classList.add(data.status);
        
        // Store the component status
        this.componentStatus[componentName] = data;
        
        // Update tooltip content if applicable
        if (componentElement.hasAttribute('data-tooltip-description')) {
            let tooltipContent = '';
            switch (componentName) {
                case 'memory':
                    tooltipContent = `Memory Usage: ${data.metrics.usage_percent}%<br>`;
                    tooltipContent += `Used: ${data.metrics.used_mb}MB / Total: ${data.metrics.total_mb}MB`;
                    break;
                case 'browser':
                    tooltipContent = `Driver Status: ${data.metrics.driver_status}<br>`;
                    tooltipContent += `Instances: ${data.metrics.instance_count}, Errors: ${data.metrics.error_count}`;
                    break;
                case 'database':
                    tooltipContent = `Connections: ${data.metrics.connection_count}<br>`;
                    tooltipContent += `Avg Query Time: ${data.metrics.query_time_avg_ms}ms`;
                    break;
                case 'ai':
                    tooltipContent = `Success Rate: ${data.metrics.success_rate}%<br>`;
                    tooltipContent += `Avg Response: ${data.metrics.avg_response_time_ms}ms`;
                    break;
                case 'system':
                    tooltipContent = `CPU: ${data.metrics.cpu_usage_percent}%<br>`;
                    tooltipContent += `Load Avg: ${data.metrics.load_avg_1m}`;
                    break;
            }
            
            if (tooltipContent) {
                componentElement.setAttribute('data-tooltip-description', tooltipContent);
            }
        }
    }
    
    /**
     * Update the overall system status
     */
    updateOverallStatus(status) {
        const statusElement = this.container.querySelector('.overall-health-indicator .status-indicator');
        const statusTextElement = this.container.querySelector('.overall-health-indicator .status-text');
        
        if (!statusElement || !statusTextElement) return;
        
        // Remove all status classes
        statusElement.classList.remove('healthy', 'warning', 'critical', 'unknown');
        
        // Add the current status class
        statusElement.classList.add(status);
        
        // Update the status text
        const statusMap = {
            'healthy': 'Healthy',
            'warning': 'Warning',
            'critical': 'Critical',
            'unknown': 'Unknown'
        };
        
        statusTextElement.textContent = statusMap[status] || 'Unknown';
    }
    
    /**
     * Update AI platform statuses
     */
    updateAIPlatforms(platforms) {
        for (const [platform, data] of Object.entries(platforms)) {
            const platformElement = this.container.querySelector(`.platform-status[data-platform="${platform}"]`);
            if (!platformElement) continue;
            
            const statusIndicator = platformElement.querySelector('.status-indicator');
            const lastSuccessElement = platformElement.querySelector('.last-success');
            
            if (!statusIndicator || !lastSuccessElement) continue;
            
            // Update status indicator
            statusIndicator.classList.remove('healthy', 'warning', 'critical', 'unknown');
            statusIndicator.classList.add(data.status);
            
            // Update last success time
            if (data.last_success) {
                const lastSuccess = new Date(data.last_success);
                const timeAgo = this.getTimeAgo(lastSuccess);
                lastSuccessElement.textContent = `Last success: ${timeAgo}`;
            } else {
                lastSuccessElement.textContent = 'No successful connections';
            }
        }
    }
    
    /**
     * Update the performance and resource charts
     */
    updateCharts(data) {
        // Update performance chart
        if (this.charts.performance && data.performance_history) {
            const chart = this.charts.performance;
            
            // Update labels
            chart.data.labels = data.performance_history.timestamps;
            
            // Update datasets
            chart.data.datasets[0].data = data.performance_history.response_time_ms;
            chart.data.datasets[1].data = data.performance_history.error_rate_percent;
            
            // Update chart
            chart.update();
        }
        
        // Update resource chart
        if (this.charts.resource && data.components) {
            const chart = this.charts.resource;
            
            const memoryUsage = data.components.memory.metrics.usage_percent;
            const cpuUsage = data.components.system.metrics.cpu_usage_percent;
            
            // Update datasets
            chart.data.datasets[0].data = [
                memoryUsage,                 // Memory Used
                100 - memoryUsage,          // Memory Free
                cpuUsage,                    // CPU Usage
                100 - cpuUsage               // CPU Idle
            ];
            
            // Update chart
            chart.update();
        }
    }
    
    /**
     * Update the activity log with new entries
     */
    updateActivityLog(logs) {
        const logContainer = this.container.querySelector('.activity-log');
        if (!logContainer) return;
        
        // Clear existing logs if there are too many
        if (logContainer.children.length > 50) {
            logContainer.innerHTML = '';
        }
        
        // Add new log entries
        logs.forEach(log => {
            // Check if this log entry already exists (based on timestamp and message)
            const existingLogs = Array.from(logContainer.querySelectorAll('.log-entry')).filter(entry => {
                const timestamp = entry.querySelector('.timestamp')?.textContent;
                const message = entry.querySelector('.log-message')?.textContent;
                
                // Format the incoming timestamp for comparison
                const logTime = new Date(log.timestamp);
                const formattedTime = logTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                
                return timestamp === formattedTime && message === log.message;
            });
            
            if (existingLogs.length === 0) {
                this.addLogEntry(logContainer, log);
            }
        });
    }
    
    /**
     * Add a single log entry to the activity log
     */
    addLogEntry(container, log) {
        const logTime = new Date(log.timestamp);
        const formattedTime = logTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="timestamp">${formattedTime}</span>
            <span class="log-type ${log.type}">${log.type.toUpperCase()}</span>
            <span class="log-message">${log.message}</span>
        `;
        
        // Add to container at the top
        container.insertBefore(logEntry, container.firstChild);
        
        // Limit number of visible log entries
        while (container.children.length > 100) {
            container.removeChild(container.lastChild);
        }
    }
    
    /**
     * Log activity internally and to the activity log
     */
    logActivity(type, message) {
        // Add to internal log
        const now = new Date();
        
        const logEntry = {
            type: type,
            message: message,
            timestamp: now.toISOString()
        };
        
        // Add to UI if container exists
        const logContainer = this.container.querySelector('.activity-log');
        if (logContainer) {
            this.addLogEntry(logContainer, logEntry);
        }
        
        // Log to console as well
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    /**
     * Store performance history for trend analysis
     */
    storePerformanceHistory(data) {
        // Get the latest timestamp
        const latestTimestamp = data.performance_history.timestamps[data.performance_history.timestamps.length - 1];
        
        // Check if we already have this timestamp
        if (this.performanceHistory.timestamps.includes(latestTimestamp)) {
            return; // Already stored this data point
        }
        
        // Add latest data point to history
        this.performanceHistory.timestamps.push(latestTimestamp);
        
        // Add latest memory usage
        this.performanceHistory.memory.push(data.components.memory.metrics.usage_percent);
        
        // Add latest CPU usage
        this.performanceHistory.cpu.push(data.components.system.metrics.cpu_usage_percent);
        
        // Add latest response time (last element of the array)
        const latestResponseTime = data.performance_history.response_time_ms[data.performance_history.response_time_ms.length - 1];
        this.performanceHistory.requests.push(latestResponseTime);
        
        // Add latest error rate (last element of the array)
        const latestErrorRate = data.performance_history.error_rate_percent[data.performance_history.error_rate_percent.length - 1];
        this.performanceHistory.errors.push(latestErrorRate);
        
        // Limit history size
        const maxHistoryPoints = 100;
        if (this.performanceHistory.timestamps.length > maxHistoryPoints) {
            this.performanceHistory.timestamps = this.performanceHistory.timestamps.slice(-maxHistoryPoints);
            this.performanceHistory.memory = this.performanceHistory.memory.slice(-maxHistoryPoints);
            this.performanceHistory.cpu = this.performanceHistory.cpu.slice(-maxHistoryPoints);
            this.performanceHistory.requests = this.performanceHistory.requests.slice(-maxHistoryPoints);
            this.performanceHistory.errors = this.performanceHistory.errors.slice(-maxHistoryPoints);
        }
    }
    
    /**
     * Show detailed information about a specific component
     */
    showComponentDetails(componentType) {
        const data = this.componentStatus[componentType];
        if (!data) return;
        
        let detailsHTML = '<div class="component-details">';
        
        // Component title
        detailsHTML += `<h5 class="details-title">${componentType.charAt(0).toUpperCase() + componentType.slice(1)} Details</h5>`;
        
        // Status indicator
        detailsHTML += `<div class="details-status mb-3">
            <span class="status-indicator ${data.status}"></span>
            <span class="status-text">${data.status.charAt(0).toUpperCase() + data.status.slice(1)}</span>
        </div>`;
        
        // Metrics table
        detailsHTML += '<table class="table table-sm">';
        detailsHTML += '<tbody>';
        
        for (const [key, value] of Object.entries(data.metrics)) {
            const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            
            let formattedValue = value;
            if (typeof value === 'number') {
                if (key.includes('percent')) {
                    formattedValue = `${value}%`;
                } else if (key.includes('time_ms')) {
                    formattedValue = `${value} ms`;
                } else if (key.includes('_mb')) {
                    formattedValue = `${value} MB`;
                }
            }
            
            detailsHTML += `<tr>
                <td>${formattedKey}</td>
                <td>${formattedValue}</td>
            </tr>`;
        }
        
        detailsHTML += '</tbody></table>';
        
        // Additional component-specific information
        if (componentType === 'ai') {
            detailsHTML += '<h6 class="mt-3">Platform Status</h6>';
            detailsHTML += '<div class="platforms-details">';
            
            for (const [platform, platformData] of Object.entries(data.platforms)) {
                const platformName = platform.charAt(0).toUpperCase() + platform.slice(1);
                let lastSuccessText = 'Unknown';
                
                if (platformData.last_success) {
                    const lastSuccess = new Date(platformData.last_success);
                    const timeAgo = this.getTimeAgo(lastSuccess);
                    lastSuccessText = timeAgo;
                }
                
                detailsHTML += `<div class="platform-detail-item">
                    <div class="platform-detail-name">${platformName}</div>
                    <div class="platform-detail-status">
                        <span class="status-indicator ${platformData.status}"></span>
                        <span>${platformData.status}</span>
                    </div>
                    <div class="platform-detail-metric">Success: ${platformData.success_rate}%</div>
                    <div class="platform-detail-metric">Last: ${lastSuccessText}</div>
                </div>`;
            }
            
            detailsHTML += '</div>';
        } else if (componentType === 'system') {
            // Add uptime in human-readable form
            const uptime = this.formatUptime(data.metrics.uptime_seconds);
            detailsHTML += `<div class="uptime-info mt-3">
                <strong>System Uptime:</strong> ${uptime}
            </div>`;
        }
        
        detailsHTML += '</div>';
        
        // Create modal with the details
        const modalId = `${componentType}-details-modal`;
        
        // Remove any existing modal
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create new modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = modalId;
        modal.tabIndex = -1;
        modal.setAttribute('aria-labelledby', `${modalId}-label`);
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${modalId}-label">${componentType.charAt(0).toUpperCase() + componentType.slice(1)} Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${detailsHTML}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
        
        // Initialize and show the modal using Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            console.warn('Bootstrap is required for the modal component');
        }
    }
    
    /**
     * Get a human-readable time ago string
     */
    getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        
        if (diffSec < 60) {
            return 'just now';
        }
        
        const diffMin = Math.floor(diffSec / 60);
        if (diffMin < 60) {
            return `${diffMin}m ago`;
        }
        
        const diffHour = Math.floor(diffMin / 60);
        if (diffHour < 24) {
            return `${diffHour}h ago`;
        }
        
        const diffDay = Math.floor(diffHour / 24);
        return `${diffDay}d ago`;
    }
    
    /**
     * Format uptime seconds into a human-readable string
     */
    formatUptime(seconds) {
        const days = Math.floor(seconds / (24 * 60 * 60));
        seconds -= days * 24 * 60 * 60;
        
        const hours = Math.floor(seconds / (60 * 60));
        seconds -= hours * 60 * 60;
        
        const minutes = Math.floor(seconds / 60);
        seconds -= minutes * 60;
        
        let uptime = '';
        if (days > 0) uptime += `${days}d `;
        if (hours > 0 || days > 0) uptime += `${hours}h `;
        if (minutes > 0 || hours > 0 || days > 0) uptime += `${minutes}m `;
        uptime += `${seconds}s`;
        
        return uptime;
    }
    
    /**
     * Clean up when the dashboard is destroyed
     */
    destroy() {
        // Clear update interval
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Destroy charts
        for (const chartName in this.charts) {
            if (this.charts[chartName]) {
                this.charts[chartName].destroy();
            }
        }
        
        // Clear container
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// If module exports are supported, export the class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemHealthDashboard;
}