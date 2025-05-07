/**
 * Synapse Chamber - Graceful Error Handling
 * Provides elegant user-friendly error handling and fault recovery
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseErrorHandler {
    constructor(options = {}) {
        this.options = Object.assign({
            containerSelector: 'body',
            defaultErrorTitle: 'An error occurred',
            defaultErrorMessage: 'We encountered a problem while processing your request. Please try again.',
            errorTimeout: 10000,
            groupSimilarErrors: true,
            maxErrors: 3,
            enableAutoHiding: true,
            errorIdPrefix: 'error-',
            errorClass: 'synapse-error',
            errorToastClass: 'synapse-error-toast',
            errorBannerClass: 'synapse-error-banner',
            errorPageClass: 'synapse-error-page'
        }, options);
        
        this.activeErrors = [];
        this.errorCounter = 0;
    }
    
    /**
     * Initialize error handler
     */
    init() {
        this.addStyles();
        this.ensureErrorContainer();
        this.setupGlobalHandlers();
        
        // Make the class accessible statically
        SynapseErrorHandler.instance = this;
        SynapseErrorHandler.showError = this.showError.bind(this);
        
        console.log("Synapse Error Handler initialized");
    }
    
    /**
     * Add CSS styles for error displays
     */
    addStyles() {
        if (document.getElementById('synapse-error-styles')) {
            return;
        }
        
        const styleElement = document.createElement('style');
        styleElement.id = 'synapse-error-styles';
        styleElement.textContent = `
            .synapse-error-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 100%;
                box-sizing: border-box;
                padding: 0 10px;
            }
            
            .synapse-error {
                margin-bottom: 10px;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
            }
            
            .synapse-error-toast {
                width: 350px;
                max-width: 100%;
                background-color: var(--bs-dark);
                border-left: 4px solid var(--bs-danger);
                opacity: 0;
                transform: translateX(40px);
                animation: slideInError 0.3s forwards;
            }
            
            .synapse-error-banner {
                width: 100%;
                background-color: var(--bs-danger);
                color: white;
                text-align: center;
                padding: 10px 15px;
                position: fixed;
                top: 0;
                left: 0;
                z-index: 9999;
                opacity: 0;
                transform: translateY(-100%);
                animation: slideDownError 0.3s forwards;
            }
            
            .synapse-error-inline {
                border-radius: 4px;
                background-color: rgba(var(--bs-danger-rgb), 0.1);
                border: 1px solid var(--bs-danger);
                padding: 10px 15px;
                margin: 10px 0;
                color: var(--bs-danger);
            }
            
            .synapse-error-page {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: var(--bs-dark);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                text-align: center;
                padding: 20px;
                opacity: 0;
                animation: fadeInError 0.5s forwards;
            }
            
            .synapse-error-icon {
                font-size: 50px;
                color: var(--bs-danger);
                margin-bottom: 20px;
            }
            
            .synapse-error-title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .synapse-error-message {
                font-size: 16px;
                margin-bottom: 20px;
                max-width: 600px;
            }
            
            .synapse-error-details {
                background-color: rgba(0, 0, 0, 0.1);
                padding: 10px;
                border-radius: 4px;
                max-width: 100%;
                overflow-x: auto;
                font-size: 12px;
                margin-top: 10px;
                text-align: left;
                color: rgba(255, 255, 255, 0.7);
            }
            
            .synapse-error-close {
                color: white;
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                margin-left: 10px;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            
            .synapse-error-close:hover {
                opacity: 1;
            }
            
            .synapse-error-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 15px;
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            .synapse-error-body {
                padding: 10px 15px;
            }
            
            .synapse-error-actions {
                margin-top: 15px;
            }
            
            @keyframes slideInError {
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideDownError {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes fadeInError {
                to {
                    opacity: 1;
                }
            }
            
            .synapse-error-help-link {
                color: var(--bs-primary);
                cursor: pointer;
                text-decoration: underline;
            }
            
            .synapse-error-count {
                display: inline-block;
                background-color: rgba(0, 0, 0, 0.2);
                color: white;
                border-radius: 10px;
                padding: 0 8px;
                font-size: 12px;
                margin-left: 5px;
            }
        `;
        
        document.head.appendChild(styleElement);
    }
    
    /**
     * Ensure error container exists
     */
    ensureErrorContainer() {
        if (!document.getElementById('synapse-error-container')) {
            const container = document.createElement('div');
            container.id = 'synapse-error-container';
            container.className = 'synapse-error-container';
            document.body.appendChild(container);
        }
    }
    
    /**
     * Set up global handlers
     */
    setupGlobalHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled Promise Rejection:', event.reason);
            this.showError({
                type: 'error',
                title: 'Promise Error',
                message: 'An async operation failed unexpectedly',
                details: event.reason.stack || event.reason.message || String(event.reason),
                display: 'toast'
            });
            
            event.preventDefault();
        });
        
        // Handle global errors
        window.addEventListener('error', (event) => {
            console.error('Global Error:', event.error);
            
            // Avoid showing errors for script and resource loading issues
            if (event.filename && (event.filename.includes('.js') || event.filename.includes('.css'))) {
                // Only show resource errors if they're from our domain
                if (event.filename.includes(window.location.hostname)) {
                    this.showError({
                        type: 'warning',
                        title: 'Resource Error',
                        message: `Failed to load ${event.filename.split('/').pop()}`,
                        details: `${event.message} at line ${event.lineno}:${event.colno}`,
                        display: 'toast'
                    });
                }
            } else {
                this.showError({
                    type: 'error',
                    title: 'Runtime Error',
                    message: event.message,
                    details: event.error ? (event.error.stack || String(event.error)) : `at ${event.filename}:${event.lineno}:${event.colno}`,
                    display: 'toast'
                });
            }
            
            event.preventDefault();
        });
        
        // Intercept fetch errors
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            return originalFetch(...args)
                .then(response => {
                    if (!response.ok) {
                        this.handleFetchError({
                            url: args[0],
                            status: response.status,
                            statusText: response.statusText,
                            response: response.clone()
                        });
                    }
                    return response;
                })
                .catch(error => {
                    this.handleFetchError({
                        url: args[0],
                        error: error
                    });
                    throw error;
                });
        };
    }
    
    /**
     * Handle fetch errors
     */
    handleFetchError(errorInfo) {
        let errorMessage = 'Failed to connect to the server';
        let errorTitle = 'Connection Error';
        let errorType = 'error';
        let errorDisplay = 'toast';
        let errorDetails = '';
        
        if (errorInfo.status) {
            switch (errorInfo.status) {
                case 401:
                case 403:
                    errorTitle = 'Authentication Error';
                    errorMessage = 'You do not have permission to access this resource';
                    break;
                case 404:
                    errorTitle = 'Resource Not Found';
                    errorMessage = 'The requested resource does not exist';
                    errorType = 'warning';
                    break;
                case 500:
                    errorTitle = 'Server Error';
                    errorMessage = 'The server encountered an error while processing your request';
                    break;
                case 503:
                    errorTitle = 'Service Unavailable';
                    errorMessage = 'The service is temporarily unavailable';
                    break;
                default:
                    errorTitle = `HTTP Error ${errorInfo.status}`;
                    errorMessage = errorInfo.statusText || 'An error occurred while communicating with the server';
            }
            
            // For critical API errors, show a more prominent error
            if (errorInfo.url.toString().includes('/api/') && [500, 502, 503, 504].includes(errorInfo.status)) {
                errorDisplay = 'banner';
            }
            
            // Try to get more error details from the response
            if (errorInfo.response) {
                errorInfo.response.text().then(text => {
                    try {
                        const data = JSON.parse(text);
                        if (data.message || data.error) {
                            errorDetails = data.message || data.error;
                            this.updateErrorWithDetails(errorTitle, errorDetails);
                        }
                    } catch (e) {
                        // If the response isn't JSON, use the text as details
                        if (text && text.length < 100) {
                            errorDetails = text;
                            this.updateErrorWithDetails(errorTitle, errorDetails);
                        }
                    }
                }).catch(() => {
                    // Ignore errors parsing the response
                });
            }
        } else if (errorInfo.error) {
            // Network level errors
            if (errorInfo.error.name === 'AbortError') {
                errorTitle = 'Request Timeout';
                errorMessage = 'The request was cancelled because it took too long';
                errorType = 'warning';
            } else {
                errorMessage = 'Could not connect to the server. Please check your internet connection.';
                errorDetails = errorInfo.error.message;
            }
        }
        
        this.showError({
            type: errorType,
            title: errorTitle,
            message: errorMessage,
            details: errorDetails,
            display: errorDisplay,
            url: errorInfo.url.toString()
        });
    }
    
    /**
     * Update an existing error with new details
     */
    updateErrorWithDetails(errorTitle, details) {
        // Find the most recent error with this title
        const error = this.activeErrors.find(e => e.title === errorTitle);
        if (error) {
            const detailsElement = document.getElementById(`${error.id}-details`);
            if (detailsElement) {
                detailsElement.textContent = details;
            }
        }
    }
    
    /**
     * Show an error message
     */
    showError(options) {
        const settings = Object.assign({
            type: 'error',
            title: this.options.defaultErrorTitle,
            message: this.options.defaultErrorMessage,
            details: null,
            display: 'toast',
            timeout: this.options.errorTimeout,
            container: null,
            autoHide: this.options.enableAutoHiding,
            url: null
        }, options);
        
        // If we're grouping similar errors, check if there's already an error with the same message
        if (this.options.groupSimilarErrors) {
            const similarError = this.findSimilarError(settings);
            if (similarError) {
                // Update count for similar error
                const countElement = document.getElementById(`${similarError.id}-count`);
                if (countElement) {
                    similarError.count++;
                    countElement.textContent = similarError.count;
                    
                    // Reset timeout if autoHide is enabled
                    if (settings.autoHide && similarError.timeoutId) {
                        clearTimeout(similarError.timeoutId);
                        similarError.timeoutId = setTimeout(() => this.hideError(similarError.id), settings.timeout);
                    }
                }
                return similarError.id;
            }
        }
        
        // Limit the number of simultaneously displayed errors
        if (this.activeErrors.length >= this.options.maxErrors && settings.display === 'toast') {
            const oldestError = this.activeErrors[0];
            this.hideError(oldestError.id);
        }
        
        // Generate a unique ID for this error
        const errorId = this.generateErrorId(settings);
        
        // Create the error element based on display type
        let errorElement;
        switch (settings.display) {
            case 'toast':
                errorElement = this.createErrorToast(settings);
                break;
            case 'banner':
                errorElement = this.createErrorBanner(settings);
                break;
            case 'inline':
                errorElement = this.createInlineError(settings);
                break;
            case 'page':
                errorElement = this.createErrorPage(settings);
                break;
            default:
                errorElement = this.createErrorToast(settings);
        }
        
        // Store the error reference
        const errorRef = {
            id: errorId,
            element: errorElement,
            title: settings.title,
            message: settings.message,
            type: settings.type,
            display: settings.display,
            count: 1,
            timeoutId: null
        };
        
        this.activeErrors.push(errorRef);
        
        // Set up auto-hide if enabled
        if (settings.autoHide && settings.display !== 'page') {
            errorRef.timeoutId = setTimeout(() => this.hideError(errorId), settings.timeout);
        }
        
        console.log(`Error displayed: ${settings.message}`);
        return errorId;
    }
    
    /**
     * Create an error toast notification
     */
    createErrorToast(settings) {
        const errorElement = document.createElement('div');
        errorElement.id = settings.id;
        errorElement.className = `${this.options.errorClass} ${this.options.errorToastClass}`;
        
        // Create inner content
        const headerColor = settings.type === 'error' ? 'var(--bs-danger)' : 
                           settings.type === 'warning' ? 'var(--bs-warning)' : 
                           'var(--bs-primary)';
        
        errorElement.innerHTML = `
            <div class="synapse-error-header" style="background-color: ${headerColor};">
                <div>
                    <i class="fas ${settings.type === 'error' ? 'fa-exclamation-circle' : 
                                  settings.type === 'warning' ? 'fa-exclamation-triangle' : 
                                  'fa-info-circle'}"></i>
                    <strong>${settings.title}</strong>
                    <span id="${settings.id}-count" class="synapse-error-count">1</span>
                </div>
                <button class="synapse-error-close" onclick="document.getElementById('${settings.id}').remove();">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="synapse-error-body">
                <div>${settings.message}</div>
                ${settings.details ? `<div id="${settings.id}-details" class="synapse-error-details">${settings.details}</div>` : ''}
                ${settings.type === 'error' ? `
                    <div class="synapse-error-actions">
                        <a href="#" class="synapse-error-help-link" onclick="window.location.reload(); return false;">
                            <i class="fas fa-sync-alt"></i> Reload Page
                        </a>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Add to container
        document.getElementById('synapse-error-container').appendChild(errorElement);
        
        return errorElement;
    }
    
    /**
     * Create an error banner
     */
    createErrorBanner(settings) {
        const errorElement = document.createElement('div');
        errorElement.id = settings.id;
        errorElement.className = `${this.options.errorClass} ${this.options.errorBannerClass}`;
        
        errorElement.innerHTML = `
            <div class="container d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas ${settings.type === 'error' ? 'fa-exclamation-circle' : 
                                  settings.type === 'warning' ? 'fa-exclamation-triangle' : 
                                  'fa-info-circle'}"></i>
                    <strong>${settings.title}:</strong> ${settings.message}
                    ${settings.type === 'error' ? `
                        <a href="#" class="text-white ms-3" onclick="window.location.reload(); return false;">
                            <i class="fas fa-sync-alt"></i> Reload Page
                        </a>
                    ` : ''}
                </div>
                <button class="synapse-error-close" onclick="document.getElementById('${settings.id}').remove();">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.prepend(errorElement);
        document.body.style.paddingTop = `${errorElement.offsetHeight}px`;
        
        // When the banner is removed, reset the body padding
        const bannerRemoveObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && Array.from(mutation.removedNodes).includes(errorElement)) {
                    document.body.style.paddingTop = '0';
                    bannerRemoveObserver.disconnect();
                }
            });
        });
        
        bannerRemoveObserver.observe(document.body, { childList: true });
        
        return errorElement;
    }
    
    /**
     * Create an inline error
     */
    createInlineError(settings) {
        const errorElement = document.createElement('div');
        errorElement.id = settings.id;
        errorElement.className = `${this.options.errorClass} synapse-error-inline`;
        
        errorElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas ${settings.type === 'error' ? 'fa-exclamation-circle' : 
                                  settings.type === 'warning' ? 'fa-exclamation-triangle' : 
                                  'fa-info-circle'}"></i>
                    <strong>${settings.title}:</strong> ${settings.message}
                </div>
                <button class="synapse-error-close" style="color: var(--bs-danger);" onclick="document.getElementById('${settings.id}').remove();">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            ${settings.details ? `<div id="${settings.id}-details" class="synapse-error-details mt-2">${settings.details}</div>` : ''}
        `;
        
        const container = settings.container || document.querySelector(this.options.containerSelector);
        container.insertAdjacentElement('afterbegin', errorElement);
        
        return errorElement;
    }
    
    /**
     * Create an error page for fatal errors
     */
    createErrorPage(settings) {
        const errorElement = document.createElement('div');
        errorElement.id = settings.id;
        errorElement.className = `${this.options.errorClass} ${this.options.errorPageClass}`;
        
        errorElement.innerHTML = `
            <div class="synapse-error-icon">
                <i class="fas ${settings.type === 'error' ? 'fa-exclamation-circle' : 
                              settings.type === 'warning' ? 'fa-exclamation-triangle' : 
                              'fa-info-circle'}"></i>
            </div>
            <h1 class="synapse-error-title">${settings.title}</h1>
            <div class="synapse-error-message">${settings.message}</div>
            ${settings.details ? `<div id="${settings.id}-details" class="synapse-error-details">${settings.details}</div>` : ''}
            <div class="synapse-error-actions mt-4">
                <button class="btn btn-primary me-2" onclick="window.location.reload();">
                    <i class="fas fa-sync-alt"></i> Reload Page
                </button>
                <button class="btn btn-outline-secondary" onclick="window.history.back();">
                    <i class="fas fa-arrow-left"></i> Go Back
                </button>
            </div>
        `;
        
        document.body.appendChild(errorElement);
        
        return errorElement;
    }
    
    /**
     * Hide an error by ID
     */
    hideError(errorId) {
        const errorIndex = this.activeErrors.findIndex(e => e.id === errorId);
        if (errorIndex !== -1) {
            const error = this.activeErrors[errorIndex];
            
            // Clear the timeout if it exists
            if (error.timeoutId) {
                clearTimeout(error.timeoutId);
            }
            
            // Remove the element
            if (error.element && error.element.parentNode) {
                error.element.parentNode.removeChild(error.element);
            }
            
            // Remove from the active errors array
            this.activeErrors.splice(errorIndex, 1);
        }
    }
    
    /**
     * Hide all errors
     */
    hideAllErrors() {
        while (this.activeErrors.length > 0) {
            this.hideError(this.activeErrors[0].id);
        }
    }
    
    /**
     * Find a similar error to group with
     */
    findSimilarError(errorSettings) {
        return this.activeErrors.find(error => 
            error.display === errorSettings.display && 
            error.type === errorSettings.type &&
            this.isSimilarMessage(error.message, errorSettings.message)
        );
    }
    
    /**
     * Check if two error messages are similar
     */
    isSimilarMessage(message1, message2) {
        // Exact match
        if (message1 === message2) return true;
        
        // Simple similarity check - compare the first 20 characters
        if (message1.substring(0, 20) === message2.substring(0, 20)) return true;
        
        return false;
    }
    
    /**
     * Generate a unique error ID
     */
    generateErrorId(settings) {
        const category = this.categorizeError(settings.message);
        this.errorCounter++;
        return `${this.options.errorIdPrefix}${category}-${this.errorCounter}`;
    }
    
    /**
     * Categorize an error based on its message
     */
    categorizeError(message) {
        if (!message) return 'general';
        
        message = message.toLowerCase();
        
        if (message.includes('network') || message.includes('connection') || message.includes('offline')) {
            return 'network';
        } else if (message.includes('permission') || message.includes('access') || message.includes('unauthorized') || message.includes('auth')) {
            return 'auth';
        } else if (message.includes('server') || message.includes('500')) {
            return 'server';
        } else if (message.includes('not found') || message.includes('404')) {
            return 'notfound';
        } else if (message.includes('timeout') || message.includes('timed out')) {
            return 'timeout';
        } else if (message.includes('invalid') || message.includes('validation')) {
            return 'validation';
        } else {
            return 'general';
        }
    }
    
    /**
     * Get a fallback error message based on category
     */
    getFallbackMessage(category) {
        switch (category) {
            case 'network':
                return 'There seems to be a problem with your internet connection. Please check and try again.';
            case 'auth':
                return 'You do not have permission to access this resource or your session has expired.';
            case 'server':
                return 'The server encountered an error while processing your request. Please try again later.';
            case 'notfound':
                return 'The requested resource could not be found.';
            case 'timeout':
                return 'The operation timed out. Please try again later.';
            case 'validation':
                return 'There was an error validating your input. Please check and try again.';
            default:
                return this.options.defaultErrorMessage;
        }
    }
    
    /**
     * Show a network error
     */
    showNetworkError(message, details = null) {
        return this.showError({
            type: 'error',
            title: 'Network Error',
            message: message || 'Could not connect to the server. Please check your internet connection.',
            details: details,
            display: 'toast'
        });
    }
    
    /**
     * Show an authentication error
     */
    showAuthError(message, details = null) {
        return this.showError({
            type: 'error',
            title: 'Authentication Error',
            message: message || 'You are not authorized to perform this action.',
            details: details,
            display: 'toast'
        });
    }
    
    /**
     * Show a validation error
     */
    showValidationError(message, container, details = null) {
        return this.showError({
            type: 'warning',
            title: 'Validation Error',
            message: message || 'Please check your input and try again.',
            details: details,
            display: 'inline',
            container: container
        });
    }
    
    /**
     * Show a server error
     */
    showServerError(message, details = null) {
        return this.showError({
            type: 'error',
            title: 'Server Error',
            message: message || 'The server encountered an error while processing your request.',
            details: details,
            display: 'toast'
        });
    }
    
    /**
     * Show a fatal error (error page)
     */
    showFatalError(message, details = null) {
        return this.showError({
            type: 'error',
            title: 'Fatal Error',
            message: message || 'A critical error has occurred and the application cannot continue.',
            details: details,
            display: 'page',
            autoHide: false
        });
    }
}

// Initialize the error handler if script is loaded after DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(() => {
        new SynapseErrorHandler().init();
    }, 0);
} else {
    document.addEventListener('DOMContentLoaded', () => {
        new SynapseErrorHandler().init();
    });
}