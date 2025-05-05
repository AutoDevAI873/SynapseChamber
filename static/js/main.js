// Main JavaScript for Synapse Chamber

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize any charts
    initializeCharts();
    
    // Set up navigation events
    setupNavigation();
    
    // Set up resize handlers
    setupResizeHandlers();
    
    // Initialize dark mode
    initializeDarkMode();
    
    // Set up clipboard actions
    setupClipboardActions();
    
    // Initialize any dynamic content loaders
    initializeDynamicContent();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
}

// Initialize chart elements
function initializeCharts() {
    // This function will be expanded as needed for specific charts
    // It provides a central place to initialize any Chart.js instances
}

// Set up navigation and routing
function setupNavigation() {
    // Handle active navigation states
    const currentPath = window.location.pathname;
    
    // Update active state in navbar
    document.querySelectorAll('.navbar .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent && !mainContent.classList.contains('page-transition')) {
        mainContent.classList.add('page-transition');
    }
}

// Set up handlers for window resize events
function setupResizeHandlers() {
    // Handle responsive adjustments
    const handleResize = () => {
        // Adjust UI for small screens
        if (window.innerWidth < 768) {
            document.body.classList.add('small-screen');
        } else {
            document.body.classList.remove('small-screen');
        }
        
        // Trigger resize for any charts
        if (window.Chart) {
            Chart.instances.forEach(chart => {
                chart.resize();
            });
        }
    };
    
    // Initial call
    handleResize();
    
    // Add event listener
    window.addEventListener('resize', handleResize);
}

// Initialize dark mode toggle
function initializeDarkMode() {
    // Synapse Chamber is primarily dark mode, but this function
    // could be expanded to support light mode as an option
    
    // Make sure the theme attribute is set
    document.documentElement.setAttribute('data-bs-theme', 'dark');
}

// Set up clipboard copy functionality
function setupClipboardActions() {
    document.querySelectorAll('.copy-to-clipboard').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-copy-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const textToCopy = targetElement.innerText || targetElement.value;
                
                // Copy to clipboard
                navigator.clipboard.writeText(textToCopy)
                    .then(() => {
                        // Visual feedback
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        
                        // Reset after 2 seconds
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy text: ', err);
                    });
            }
        });
    });
}

// Initialize dynamic content loading
function initializeDynamicContent() {
    document.querySelectorAll('[data-load-url]').forEach(container => {
        const url = container.getAttribute('data-load-url');
        if (url) {
            loadContent(container, url);
        }
    });
}

// Load content from a URL into a container
function loadContent(container, url) {
    // Show loading state
    container.innerHTML = `
        <div class="text-center p-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading content...</p>
        </div>
    `;
    
    // Fetch the content
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            container.innerHTML = html;
            
            // Initialize any new components
            initializeComponents(container);
        })
        .catch(error => {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading content: ${error.message}
                    <button class="btn btn-sm btn-outline-danger ms-3" onclick="loadContent(this.closest('[data-load-url]'), '${url}')">Retry</button>
                </div>
            `;
        });
}

// Initialize components within a container (used after loading dynamic content)
function initializeComponents(container) {
    // Tooltips
    const tooltipTriggerList = container.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Popovers
    const popoverTriggerList = container.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Other component initializations can be added as needed
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Utility function for API calls
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const jsonResponse = await response.json();
        
        if (!response.ok) {
            throw new Error(jsonResponse.message || 'API call failed');
        }
        
        return jsonResponse;
    } catch (error) {
        console.error(`API call to ${url} failed:`, error);
        throw error;
    }
}

// Global notification function
function showNotification(type, message, duration = 5000) {
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
        delay: duration
    });
    
    // Remove from DOM when hidden
    notification.addEventListener('hidden.bs.toast', function() {
        container.removeChild(notification);
    });
}

// Function to detect if we're in a headless environment (for browser automation)
function isHeadless() {
    // Check for common headless browser characteristics
    return !window.matchMedia('(display-mode: browser)').matches || 
           navigator.userAgent.includes('Headless') ||
           navigator.webdriver ||
           window.callPhantom ||
           window._phantom;
}

// Update UI based on environment
function updateUIForEnvironment() {
    if (isHeadless()) {
        document.body.classList.add('headless-environment');
        
        // Add a subtle indicator that we're in a headless environment
        const indicator = document.createElement('div');
        indicator.className = 'headless-indicator';
        indicator.innerHTML = '<i class="fas fa-robot"></i> Automated Session';
        document.body.appendChild(indicator);
    }
}

// Call environment check
updateUIForEnvironment();