/**
 * Synapse Chamber - Graceful Error Handling
 * Provides elegant user-friendly error handling and fault recovery
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseErrorHandler {
    constructor(options = {}) {
        // Configuration
        this.config = {
            container: options.container || document.body,
            errorContainerClass: options.errorContainerClass || 'error-container',
            errorToastClass: options.errorToastClass || 'error-toast',
            errorBannerClass: options.errorBannerClass || 'error-banner',
            autoHide: options.autoHide !== undefined ? options.autoHide : true,
            autoHideDelay: options.autoHideDelay || 5000,
            dismissible: options.dismissible !== undefined ? options.dismissible : true,
            animateIn: options.animateIn !== undefined ? options.animateIn : true,
            animateOut: options.animateOut !== undefined ? options.animateOut : true,
            logToConsole: options.logToConsole !== undefined ? options.logToConsole : true,
            maxErrors: options.maxErrors || 5,
            groupSimilarErrors: options.groupSimilarErrors !== undefined ? options.groupSimilarErrors : true,
            fallbackMessages: {
                default: "An unexpected error occurred. Please try again later.",
                network: "Network error. Please check your connection and try again.",
                auth: "Authentication error. Please log in again.",
                permission: "You don't have permission to perform this action.",
                validation: "Please check your input and try again.",
                server: "Server error. Our team has been notified.",
                timeout: "The request timed out. Please try again.",
                browser: "Browser error. Please try refreshing the page.",
                component: "A component failed to load properly. Please refresh the page."
            },
            errorCategories: {
                network: ["network error", "failed to fetch", "cannot connect", "offline", "timeout"],
                auth: ["unauthorized", "unauthenticated", "not logged in", "login required", "session expired"],
                permission: ["forbidden", "access denied", "not allowed", "permission denied"],
                validation: ["invalid", "required field", "validation failed", "constraint violation"],
                server: ["server error", "internal error", "500", "503", "502"],
                timeout: ["timeout", "timed out", "too long", "slow response"],
                browser: ["browser", "javascript error", "rendering error", "layout error"],
                component: ["component", "failed to load", "module error", "initialization failed"]
            }
        };
        
        // State
        this.activeErrors = []; // Currently displayed errors
        this.errorCounter = {}; // Count similar errors
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize error handler
     */
    init() {
        // Add CSS styles
        this.addStyles();
        
        // Create error container if it doesn't exist
        this.ensureErrorContainer();
        
        // Set up global error handlers
        this.setupGlobalHandlers();
    }
    
    /**
     * Add CSS styles for error displays
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Error container for toast notifications */
            .error-container {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 400px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            /* Error toast notification */
            .error-toast {
                background-color: #fff;
                color: #721c24;
                border-left: 4px solid #dc3545;
                border-radius: 4px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 16px;
                margin-bottom: 10px;
                font-size: 14px;
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                max-width: 100%;
                min-width: 300px;
                position: relative;
                transition: all 0.3s ease;
                overflow: hidden;
            }
            
            .error-toast.animate-in {
                animation: slideInRight 0.3s forwards;
            }
            
            .error-toast.animate-out {
                animation: slideOutRight 0.3s forwards;
            }
            
            .error-toast-icon {
                color: #dc3545;
                font-size: 20px;
                margin-right: 12px;
                flex-shrink: 0;
            }
            
            .error-toast-content {
                flex-grow: 1;
            }
            
            .error-toast-title {
                font-weight: bold;
                margin-bottom: 5px;
                display: flex;
                align-items: center;
            }
            
            .error-toast-message {
                margin-bottom: 5px;
            }
            
            .error-toast-details {
                font-size: 12px;
                color: #6c757d;
                cursor: pointer;
            }
            
            .error-toast-detail-text {
                display: none;
                background-color: rgba(0, 0, 0, 0.05);
                padding: 8px;
                border-radius: 4px;
                margin-top: 8px;
                overflow-x: auto;
                font-family: monospace;
                font-size: 11px;
                white-space: pre-wrap;
                word-break: break-all;
            }
            
            .error-toast-actions {
                margin-top: 10px;
                display: flex;
                gap: 8px;
            }
            
            .error-toast-action {
                padding: 4px 8px;
                background-color: rgba(220, 53, 69, 0.1);
                border: none;
                border-radius: 4px;
                color: #dc3545;
                font-size: 12px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .error-toast-action:hover {
                background-color: rgba(220, 53, 69, 0.2);
            }
            
            .error-toast-close {
                color: #6c757d;
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                padding: 0 4px;
                margin-left: 8px;
                flex-shrink: 0;
            }
            
            .error-toast-close:hover {
                color: #343a40;
            }
            
            .error-toast-counter {
                background-color: #dc3545;
                color: white;
                border-radius: 12px;
                padding: 1px 6px;
                font-size: 11px;
                margin-left: 8px;
            }
            
            .error-toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background-color: #dc3545;
                opacity: 0.7;
            }
            
            /* Error banner for critical errors */
            .error-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background-color: #dc3545;
                color: white;
                padding: 12px 16px;
                z-index: 10000;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
                transform: translateY(-100%);
                transition: transform 0.3s ease;
            }
            
            .error-banner.active {
                transform: translateY(0);
            }
            
            .error-banner-icon {
                font-size: 20px;
            }
            
            .error-banner-content {
                flex-grow: 1;
            }
            
            .error-banner-message {
                margin-bottom: 0;
            }
            
            .error-banner-close {
                background: none;
                border: none;
                color: white;
                opacity: 0.8;
                cursor: pointer;
                font-size: 20px;
                line-height: 1;
                padding: 0 4px;
            }
            
            .error-banner-close:hover {
                opacity: 1;
            }
            
            .error-banner-action {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 13px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .error-banner-action:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            
            /* Error page for fatal errors */
            .error-page {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #f8f9fa;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 10001;
                padding: 20px;
                text-align: center;
            }
            
            .error-page-icon {
                font-size: 64px;
                color: #dc3545;
                margin-bottom: 20px;
            }
            
            .error-page-title {
                font-size: 24px;
                margin-bottom: 16px;
                color: #343a40;
            }
            
            .error-page-message {
                font-size: 16px;
                margin-bottom: 20px;
                max-width: 600px;
                color: #6c757d;
            }
            
            .error-page-actions {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            .error-page-action {
                padding: 8px 16px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .error-page-action:hover {
                background-color: #c82333;
            }
            
            .error-page-action.secondary {
                background-color: #6c757d;
            }
            
            .error-page-action.secondary:hover {
                background-color: #5a6268;
            }
            
            .error-page-details {
                margin-top: 30px;
                padding: 16px;
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
                max-width: 800px;
                width: 100%;
                text-align: left;
                overflow: auto;
                max-height: 200px;
            }
            
            .error-page-detail-text {
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
            }
            
            .error-inline {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background-color: rgba(220, 53, 69, 0.1);
                border-left: 3px solid #dc3545;
                border-radius: 4px;
                margin: 10px 0;
                font-size: 14px;
                color: #721c24;
            }
            
            .error-inline-icon {
                color: #dc3545;
                font-size: 16px;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            @media (max-width: 768px) {
                .error-container {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: 100%;
                }
                
                .error-toast {
                    min-width: auto;
                    width: 100%;
                    font-size: 13px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Ensure error container exists
     */
    ensureErrorContainer() {
        if (!document.querySelector(`.${this.config.errorContainerClass}`)) {
            const container = document.createElement('div');
            container.className = this.config.errorContainerClass;
            this.config.container.appendChild(container);
        }
    }
    
    /**
     * Set up global error handlers
     */
    setupGlobalHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            const error = event.reason;
            const message = error?.message || 'Unhandled Promise Rejection';
            const stack = error?.stack || '';
            
            this.showError({
                title: 'Promise Error',
                message: message,
                type: 'error',
                details: stack,
                category: this.categorizeError(message)
            });
            
            // Log to console
            if (this.config.logToConsole) {
                console.error('Unhandled Promise Rejection:', error);
            }
        });
        
        // Handle global errors
        window.addEventListener('error', (event) => {
            // Don't handle script and resource loading errors here
            if (event.target && (event.target.tagName === 'SCRIPT' || event.target.tagName === 'LINK' || event.target.tagName === 'IMG')) {
                return;
            }
            
            const error = event.error;
            const message = error?.message || event.message || 'JavaScript Error';
            const stack = error?.stack || `${event.filename || 'unknown'}: ${event.lineno || 0}:${event.colno || 0}`;
            
            this.showError({
                title: 'JavaScript Error',
                message: message,
                type: 'error',
                details: stack,
                category: this.categorizeError(message)
            });
            
            // Log to console
            if (this.config.logToConsole) {
                console.error('Global Error:', error || event);
            }
        });
        
        // Handle resource errors (scripts, stylesheets, images)
        document.addEventListener('error', (event) => {
            const target = event.target;
            
            // Only handle resource loading errors
            if (target.tagName === 'SCRIPT' || target.tagName === 'LINK' || target.tagName === 'IMG') {
                const resource = target.src || target.href || 'unknown resource';
                const tagName = target.tagName.toLowerCase();
                
                this.showError({
                    title: `Failed to Load ${tagName}`,
                    message: `Could not load ${tagName}: ${resource}`,
                    type: 'warning',
                    category: 'network'
                });
                
                // Log to console
                if (this.config.logToConsole) {
                    console.warn(`Resource Error: Failed to load ${tagName}`, resource);
                }
            }
        }, true); // Use capture phase
        
        // Add custom fetch error handling
        if (window.fetch) {
            const originalFetch = window.fetch;
            window.fetch = async (input, init) => {
                try {
                    const response = await originalFetch(input, init);
                    
                    // Handle HTTP error status
                    if (!response.ok) {
                        const errorInfo = {
                            url: typeof input === 'string' ? input : input.url,
                            status: response.status,
                            statusText: response.statusText
                        };
                        
                        // Try to parse response as JSON
                        try {
                            const clonedResponse = response.clone();
                            const data = await clonedResponse.json();
                            errorInfo.data = data;
                        } catch (e) {
                            // Ignore parsing errors
                        }
                        
                        // Don't show error UI for 401/403 responses - they might be handled by the app
                        if (response.status !== 401 && response.status !== 403) {
                            this.handleFetchError(errorInfo);
                        }
                    }
                    
                    return response;
                } catch (error) {
                    // Network or other fetch errors
                    this.handleFetchError({
                        error: error,
                        url: typeof input === 'string' ? input : input.url
                    });
                    
                    throw error; // Re-throw to allow caller to handle
                }
            };
        }
    }
    
    /**
     * Handle fetch errors
     */
    handleFetchError(errorInfo) {
        const { url, status, statusText, error, data } = errorInfo;
        
        // Get error message
        let message = '';
        let category = 'network';
        
        if (error) {
            // Network error
            message = error.message || 'Network error occurred';
        } else {
            // HTTP error
            message = `${status}: ${statusText}`;
            
            // Categorize based on status code
            if (status >= 400 && status < 500) {
                if (status === 401 || status === 403) {
                    category = 'auth';
                } else if (status === 422) {
                    category = 'validation';
                } else {
                    category = 'client';
                }
            } else if (status >= 500) {
                category = 'server';
            }
        }
        
        // Show the error
        this.showError({
            title: 'API Error',
            message: message,
            type: 'error',
            details: JSON.stringify({ url, ...data }, null, 2),
            category: category,
            actions: [
                {
                    label: 'Retry',
                    onClick: () => {
                        // Get the page the error occurred on
                        const urlObj = new URL(url, window.location.origin);
                        
                        // If it's the current page, reload
                        if (urlObj.pathname === window.location.pathname) {
                            window.location.reload();
                        } else {
                            // Otherwise, just make a new request
                            fetch(url).catch(() => {}); // Ignore errors from this fetch
                        }
                    }
                }
            ]
        });
    }
    
    /**
     * Show an error message
     */
    showError(options) {
        // Default options
        const defaults = {
            title: 'Error',
            message: this.config.fallbackMessages.default,
            type: 'error', // error, warning, info
            duration: this.config.autoHideDelay,
            autoHide: this.config.autoHide,
            dismissible: this.config.dismissible,
            details: null,
            category: 'default',
            actions: [],
            position: 'toast', // toast, banner, inline, page
            container: null, // for inline errors
            onClose: null,
            id: null
        };
        
        // Merge options
        const settings = { ...defaults, ...options };
        
        // Generate unique error ID if not provided
        if (!settings.id) {
            settings.id = this.generateErrorId(settings);
        }
        
        // Check if this is a similar error to one already showing
        if (this.config.groupSimilarErrors) {
            const similarError = this.findSimilarError(settings);
            
            if (similarError) {
                // Increment counter
                this.errorCounter[similarError.id] = (this.errorCounter[similarError.id] || 1) + 1;
                
                // Update the counter in the UI
                const errorEl = document.getElementById(similarError.id);
                
                if (errorEl) {
                    const counterEl = errorEl.querySelector('.error-toast-counter');
                    if (counterEl) {
                        counterEl.textContent = this.errorCounter[similarError.id];
                    } else {
                        const titleEl = errorEl.querySelector('.error-toast-title');
                        if (titleEl) {
                            const counter = document.createElement('span');
                            counter.className = 'error-toast-counter';
                            counter.textContent = this.errorCounter[similarError.id];
                            titleEl.appendChild(counter);
                        }
                    }
                    
                    // Highlight the error briefly
                    errorEl.style.animation = 'none';
                    setTimeout(() => {
                        errorEl.style.animation = '';
                        errorEl.classList.add('animate-in');
                        setTimeout(() => {
                            errorEl.classList.remove('animate-in');
                        }, 300);
                    }, 10);
                    
                    // Reset auto-hide timer if applicable
                    if (settings.autoHide) {
                        const progressBar = errorEl.querySelector('.error-toast-progress');
                        if (progressBar && progressBar.animate) {
                            const animation = progressBar.animate(
                                [
                                    { width: '100%' },
                                    { width: '0%' }
                                ],
                                {
                                    duration: settings.duration,
                                    fill: 'forwards',
                                    easing: 'linear'
                                }
                            );
                            
                            animation.onfinish = () => this.hideError(similarError.id);
                        }
                    }
                }
                
                return similarError.id;
            }
        }
        
        // Check if we've reached the maximum number of errors
        if (this.activeErrors.length >= this.config.maxErrors) {
            // Remove the oldest error
            this.hideError(this.activeErrors[0].id);
        }
        
        // Get or generate fallback message if needed
        if (!settings.message || settings.message.trim() === '') {
            settings.message = this.getFallbackMessage(settings.category);
        }
        
        // Create error element based on position
        let errorElement;
        
        switch (settings.position) {
            case 'banner':
                errorElement = this.createErrorBanner(settings);
                break;
            case 'inline':
                errorElement = this.createInlineError(settings);
                break;
            case 'page':
                errorElement = this.createErrorPage(settings);
                break;
            default: // toast
                errorElement = this.createErrorToast(settings);
        }
        
        // Add error to active errors list
        this.activeErrors.push({
            id: settings.id,
            type: settings.type,
            message: settings.message,
            category: settings.category,
            element: errorElement
        });
        
        // Initialize error counter
        this.errorCounter[settings.id] = 1;
        
        // Return the error ID
        return settings.id;
    }
    
    /**
     * Create an error toast notification
     */
    createErrorToast(settings) {
        // Find or create error container
        const container = document.querySelector(`.${this.config.errorContainerClass}`);
        if (!container) return null;
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `${this.config.errorToastClass}`;
        toast.id = settings.id;
        
        if (this.config.animateIn) {
            toast.classList.add('animate-in');
        }
        
        // Get icon based on type
        let iconClass = 'fas fa-exclamation-circle';
        if (settings.type === 'warning') {
            iconClass = 'fas fa-exclamation-triangle';
        } else if (settings.type === 'info') {
            iconClass = 'fas fa-info-circle';
        }
        
        // Set inner HTML
        toast.innerHTML = `
            <div class="error-toast-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="error-toast-content">
                <div class="error-toast-title">${settings.title}</div>
                <div class="error-toast-message">${settings.message}</div>
                ${settings.details ? '<div class="error-toast-details">Show details</div><div class="error-toast-detail-text"></div>' : ''}
                ${settings.actions.length > 0 ? '<div class="error-toast-actions"></div>' : ''}
                ${settings.autoHide ? '<div class="error-toast-progress" style="width: 100%"></div>' : ''}
            </div>
            ${settings.dismissible ? '<button class="error-toast-close">&times;</button>' : ''}
        `;
        
        // Add details if provided
        if (settings.details) {
            const detailsToggle = toast.querySelector('.error-toast-details');
            const detailsText = toast.querySelector('.error-toast-detail-text');
            
            if (detailsToggle && detailsText) {
                detailsText.textContent = settings.details;
                
                detailsToggle.addEventListener('click', () => {
                    if (detailsText.style.display === 'block') {
                        detailsText.style.display = 'none';
                        detailsToggle.textContent = 'Show details';
                    } else {
                        detailsText.style.display = 'block';
                        detailsToggle.textContent = 'Hide details';
                    }
                });
            }
        }
        
        // Add actions if provided
        if (settings.actions.length > 0) {
            const actionsContainer = toast.querySelector('.error-toast-actions');
            
            if (actionsContainer) {
                settings.actions.forEach(action => {
                    const actionButton = document.createElement('button');
                    actionButton.className = 'error-toast-action';
                    actionButton.textContent = action.label;
                    
                    if (action.onClick) {
                        actionButton.addEventListener('click', () => {
                            action.onClick();
                            if (action.closeOnClick !== false) {
                                this.hideError(settings.id);
                            }
                        });
                    }
                    
                    actionsContainer.appendChild(actionButton);
                });
            }
        }
        
        // Add close handler
        if (settings.dismissible) {
            const closeButton = toast.querySelector('.error-toast-close');
            
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    this.hideError(settings.id);
                    
                    // Call onClose callback if provided
                    if (typeof settings.onClose === 'function') {
                        settings.onClose();
                    }
                });
            }
        }
        
        // Add auto-hide functionality
        if (settings.autoHide) {
            const progressBar = toast.querySelector('.error-toast-progress');
            
            if (progressBar && progressBar.animate) {
                const animation = progressBar.animate(
                    [
                        { width: '100%' },
                        { width: '0%' }
                    ],
                    {
                        duration: settings.duration,
                        fill: 'forwards',
                        easing: 'linear'
                    }
                );
                
                animation.onfinish = () => this.hideError(settings.id);
            } else {
                // Fallback for browsers that don't support Web Animations API
                setTimeout(() => {
                    this.hideError(settings.id);
                }, settings.duration);
            }
        }
        
        // Add to container
        container.appendChild(toast);
        
        // Remove animate-in class after animation completes
        setTimeout(() => {
            toast.classList.remove('animate-in');
        }, 300);
        
        return toast;
    }
    
    /**
     * Create an error banner
     */
    createErrorBanner(settings) {
        // Create banner element
        const banner = document.createElement('div');
        banner.className = `${this.config.errorBannerClass}`;
        banner.id = settings.id;
        
        // Set inner HTML
        banner.innerHTML = `
            <div class="error-banner-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="error-banner-content">
                <div class="error-banner-message">${settings.message}</div>
            </div>
            ${settings.actions.length > 0 ? '<div class="error-banner-actions"></div>' : ''}
            ${settings.dismissible ? '<button class="error-banner-close">&times;</button>' : ''}
        `;
        
        // Add actions if provided
        if (settings.actions.length > 0) {
            const actionsContainer = banner.querySelector('.error-banner-actions');
            
            if (actionsContainer) {
                settings.actions.forEach(action => {
                    const actionButton = document.createElement('button');
                    actionButton.className = 'error-banner-action';
                    actionButton.textContent = action.label;
                    
                    if (action.onClick) {
                        actionButton.addEventListener('click', () => {
                            action.onClick();
                            if (action.closeOnClick !== false) {
                                this.hideError(settings.id);
                            }
                        });
                    }
                    
                    actionsContainer.appendChild(actionButton);
                });
            }
        }
        
        // Add close handler
        if (settings.dismissible) {
            const closeButton = banner.querySelector('.error-banner-close');
            
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    this.hideError(settings.id);
                    
                    // Call onClose callback if provided
                    if (typeof settings.onClose === 'function') {
                        settings.onClose();
                    }
                });
            }
        }
        
        // Add to document
        document.body.appendChild(banner);
        
        // Trigger layout and then add active class
        banner.offsetHeight; // Force reflow
        banner.classList.add('active');
        
        // Add auto-hide functionality
        if (settings.autoHide) {
            setTimeout(() => {
                this.hideError(settings.id);
            }, settings.duration);
        }
        
        return banner;
    }
    
    /**
     * Create an inline error
     */
    createInlineError(settings) {
        // Get container element
        const container = settings.container instanceof Element ? 
                        settings.container : 
                        document.querySelector(settings.container);
        
        if (!container) return null;
        
        // Create inline error element
        const inlineError = document.createElement('div');
        inlineError.className = 'error-inline';
        inlineError.id = settings.id;
        
        // Set inner HTML
        inlineError.innerHTML = `
            <div class="error-inline-icon">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="error-inline-message">${settings.message}</div>
            ${settings.dismissible ? '<button class="error-toast-close">&times;</button>' : ''}
        `;
        
        // Add close handler
        if (settings.dismissible) {
            const closeButton = inlineError.querySelector('.error-toast-close');
            
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    this.hideError(settings.id);
                    
                    // Call onClose callback if provided
                    if (typeof settings.onClose === 'function') {
                        settings.onClose();
                    }
                });
            }
        }
        
        // Add to container
        container.appendChild(inlineError);
        
        // Add auto-hide functionality
        if (settings.autoHide) {
            setTimeout(() => {
                this.hideError(settings.id);
            }, settings.duration);
        }
        
        return inlineError;
    }
    
    /**
     * Create an error page for fatal errors
     */
    createErrorPage(settings) {
        // Create error page element
        const errorPage = document.createElement('div');
        errorPage.className = 'error-page';
        errorPage.id = settings.id;
        
        // Set inner HTML
        errorPage.innerHTML = `
            <div class="error-page-icon">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <h1 class="error-page-title">${settings.title}</h1>
            <div class="error-page-message">${settings.message}</div>
            <div class="error-page-actions">
                <button class="error-page-action reload">Reload Page</button>
                <button class="error-page-action secondary home">Go to Home</button>
            </div>
            ${settings.details ? '<div class="error-page-details"><div class="error-page-detail-text"></div></div>' : ''}
        `;
        
        // Add details if provided
        if (settings.details) {
            const detailsText = errorPage.querySelector('.error-page-detail-text');
            
            if (detailsText) {
                detailsText.textContent = settings.details;
            }
        }
        
        // Add action handlers
        const reloadButton = errorPage.querySelector('.error-page-action.reload');
        if (reloadButton) {
            reloadButton.addEventListener('click', () => {
                window.location.reload();
            });
        }
        
        const homeButton = errorPage.querySelector('.error-page-action.home');
        if (homeButton) {
            homeButton.addEventListener('click', () => {
                window.location.href = '/';
            });
        }
        
        // Add to document
        document.body.appendChild(errorPage);
        
        return errorPage;
    }
    
    /**
     * Hide an error by ID
     */
    hideError(errorId) {
        // Find error in active errors
        const errorIndex = this.activeErrors.findIndex(error => error.id === errorId);
        
        if (errorIndex === -1) return;
        
        const error = this.activeErrors[errorIndex];
        const element = error.element;
        
        if (!element) {
            // If element not found, just remove from active errors
            this.activeErrors.splice(errorIndex, 1);
            delete this.errorCounter[errorId];
            return;
        }
        
        // Remove error with animation if enabled
        if (this.config.animateOut && element.classList.contains(this.config.errorToastClass)) {
            element.classList.add('animate-out');
            
            // Wait for animation to complete
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
                
                // Remove from active errors
                this.activeErrors.splice(errorIndex, 1);
                delete this.errorCounter[errorId];
            }, 300);
        } else if (element.classList.contains(this.config.errorBannerClass)) {
            // Remove banner
            element.classList.remove('active');
            
            // Wait for transition to complete
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
                
                // Remove from active errors
                this.activeErrors.splice(errorIndex, 1);
                delete this.errorCounter[errorId];
            }, 300);
        } else {
            // Remove immediately
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            
            // Remove from active errors
            this.activeErrors.splice(errorIndex, 1);
            delete this.errorCounter[errorId];
        }
    }
    
    /**
     * Hide all errors
     */
    hideAllErrors() {
        // Get a copy of active errors
        const activeErrorsCopy = [...this.activeErrors];
        
        // Hide each error
        activeErrorsCopy.forEach(error => {
            this.hideError(error.id);
        });
    }
    
    /**
     * Find a similar error to group with
     */
    findSimilarError(errorSettings) {
        return this.activeErrors.find(error => {
            // Check if same category and similar message
            return error.category === errorSettings.category && 
                   this.isSimilarMessage(error.message, errorSettings.message);
        });
    }
    
    /**
     * Check if two error messages are similar
     */
    isSimilarMessage(message1, message2) {
        // Simple string similarity check - could be improved
        if (message1 === message2) return true;
        
        // Convert to lowercase and remove punctuation
        const normalize = (str) => str.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "");
        
        const norm1 = normalize(message1);
        const norm2 = normalize(message2);
        
        // Check if one is contained in the other
        return norm1.includes(norm2) || norm2.includes(norm1);
    }
    
    /**
     * Generate a unique error ID
     */
    generateErrorId(settings) {
        const timestamp = Date.now();
        const randomPart = Math.floor(Math.random() * 10000);
        const categoryPart = settings.category || 'default';
        
        return `error-${categoryPart}-${timestamp}-${randomPart}`;
    }
    
    /**
     * Categorize an error based on its message
     */
    categorizeError(message) {
        if (!message) return 'default';
        
        const lowerMessage = message.toLowerCase();
        
        for (const [category, keywords] of Object.entries(this.config.errorCategories)) {
            for (const keyword of keywords) {
                if (lowerMessage.includes(keyword)) {
                    return category;
                }
            }
        }
        
        return 'default';
    }
    
    /**
     * Get a fallback error message based on category
     */
    getFallbackMessage(category) {
        return this.config.fallbackMessages[category] || this.config.fallbackMessages.default;
    }
    
    /**
     * Show a network error
     */
    showNetworkError(message, details = null) {
        return this.showError({
            title: 'Network Error',
            message: message || this.config.fallbackMessages.network,
            type: 'error',
            details: details,
            category: 'network',
            actions: [
                {
                    label: 'Retry',
                    onClick: () => window.location.reload()
                }
            ]
        });
    }
    
    /**
     * Show an authentication error
     */
    showAuthError(message, details = null) {
        return this.showError({
            title: 'Authentication Error',
            message: message || this.config.fallbackMessages.auth,
            type: 'error',
            details: details,
            category: 'auth',
            actions: [
                {
                    label: 'Login',
                    onClick: () => window.location.href = '/login'
                }
            ]
        });
    }
    
    /**
     * Show a validation error
     */
    showValidationError(message, container, details = null) {
        return this.showError({
            title: 'Validation Error',
            message: message || this.config.fallbackMessages.validation,
            type: 'warning',
            details: details,
            category: 'validation',
            position: 'inline',
            container: container,
            autoHide: false
        });
    }
    
    /**
     * Show a server error
     */
    showServerError(message, details = null) {
        return this.showError({
            title: 'Server Error',
            message: message || this.config.fallbackMessages.server,
            type: 'error',
            details: details,
            category: 'server',
            actions: [
                {
                    label: 'Retry',
                    onClick: () => window.location.reload()
                }
            ]
        });
    }
    
    /**
     * Show a fatal error (error page)
     */
    showFatalError(message, details = null) {
        return this.showError({
            title: 'Fatal Error',
            message: message || 'The application encountered a critical error and cannot continue.',
            type: 'error',
            details: details,
            category: 'fatal',
            position: 'page',
            autoHide: false,
            dismissible: false
        });
    }
}

// Initialize error handler
const synapseErrors = new SynapseErrorHandler();

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SynapseErrorHandler;
}