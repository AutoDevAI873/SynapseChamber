/**
 * Synapse Chamber - Animated Loading Spinners
 * Provides dynamic loading indicators throughout the application
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseSpinners {
    constructor() {
        // Configuration
        this.config = {
            defaultType: 'border',
            defaultSize: 'md',
            defaultTheme: 'primary',
            autoDetect: true, // Auto-detect and initialize spinners
            showText: true, // Show loading text by default
            spinnerZIndex: 1000, // z-index for spinners
            defaultMessages: {
                loading: 'Loading...',
                processing: 'Processing...',
                connecting: 'Connecting...',
                analyzing: 'Analyzing...',
                generating: 'Generating...',
                training: 'Training...',
                thinking: 'Thinking...'
            },
            animateMessages: true, // Animate dots in messages
            platformMessages: {
                gpt: 'Connecting to ChatGPT...',
                claude: 'Connecting to Claude...',
                gemini: 'Connecting to Gemini...',
                grok: 'Connecting to Grok...',
                deepseek: 'Connecting to DeepSeek...'
            }
        };
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize spinners
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
     * Set up spinner functionality
     */
    setup() {
        // Auto-detect and initialize spinners if enabled
        if (this.config.autoDetect) {
            this.autoInitSpinners();
        }
        
        // Set up mutation observer to detect new spinners
        this.setupMutationObserver();
    }
    
    /**
     * Auto-initialize spinners from markup
     */
    autoInitSpinners() {
        // Find spinner elements
        const spinnerElements = document.querySelectorAll('[data-spinner]');
        
        // Initialize each spinner
        spinnerElements.forEach(element => {
            this.initializeSpinner(element);
        });
    }
    
    /**
     * Initialize a spinner element
     */
    initializeSpinner(element) {
        // Get spinner configuration from data attributes
        const type = element.getAttribute('data-spinner-type') || this.config.defaultType;
        const size = element.getAttribute('data-spinner-size') || this.config.defaultSize;
        const theme = element.getAttribute('data-spinner-theme') || this.config.defaultTheme;
        const message = element.getAttribute('data-spinner-message') || this.config.defaultMessages.loading;
        const showText = element.hasAttribute('data-spinner-text') ? 
                        element.getAttribute('data-spinner-text') !== 'false' : 
                        this.config.showText;
        
        // Create spinner based on type
        let spinnerHTML = '';
        
        switch (type) {
            case 'border':
                spinnerHTML = this.createBorderSpinner(size, theme);
                break;
            case 'dots':
                spinnerHTML = this.createDotsSpinner(size, theme);
                break;
            case 'pulse':
                spinnerHTML = this.createPulseSpinner(size, theme);
                break;
            case 'dual':
                spinnerHTML = this.createDualSpinner(size, theme);
                break;
            case 'connection':
                spinnerHTML = this.createConnectionSpinner(size, theme);
                break;
            case 'progress':
                const progress = element.getAttribute('data-spinner-progress') || '0';
                spinnerHTML = this.createProgressSpinner(size, theme, progress);
                break;
            default:
                spinnerHTML = this.createBorderSpinner(size, theme);
        }
        
        // Add text if enabled
        if (showText && message) {
            const textHTML = `<div class="spinner-text" data-spinner-message-container>${message}</div>`;
            spinnerHTML = `<div class="spinner-with-text">${spinnerHTML}${textHTML}</div>`;
        }
        
        // Set spinner HTML
        element.innerHTML = spinnerHTML;
        
        // If spinner should animate its message, start animation
        if (this.config.animateMessages && showText && message) {
            this.animateSpinnerMessage(element);
        }
    }
    
    /**
     * Create a border spinner
     */
    createBorderSpinner(size, theme) {
        const sizeClass = size !== 'md' ? `spinner-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        
        return `<div class="spinner ${sizeClass} ${themeClass}"></div>`;
    }
    
    /**
     * Create a dots spinner
     */
    createDotsSpinner(size, theme) {
        const sizeClass = size !== 'md' ? `spinner-dots-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        
        return `
            <div class="spinner-dots ${sizeClass} ${themeClass}">
                <div class="spinner-dot"></div>
                <div class="spinner-dot"></div>
                <div class="spinner-dot"></div>
            </div>
        `;
    }
    
    /**
     * Create a pulse spinner
     */
    createPulseSpinner(size, theme) {
        const sizeClass = size !== 'md' ? `spinner-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        
        return `<div class="spinner-pulse ${sizeClass} ${themeClass}"></div>`;
    }
    
    /**
     * Create a dual spinner
     */
    createDualSpinner(size, theme) {
        const sizeClass = size !== 'md' ? `spinner-dual-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        
        return `<div class="spinner-dual ${sizeClass} ${themeClass}"></div>`;
    }
    
    /**
     * Create a connection spinner
     */
    createConnectionSpinner(size, theme) {
        const sizeClass = size !== 'md' ? `spinner-connection-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        
        return `
            <div class="spinner-connection ${sizeClass} ${themeClass}">
                <div class="spinner-connection-dot"></div>
                <div class="spinner-connection-dot"></div>
                <div class="spinner-connection-dot"></div>
            </div>
        `;
    }
    
    /**
     * Create a progress spinner
     */
    createProgressSpinner(size, theme, progress) {
        const sizeClass = size !== 'md' ? `spinner-progress-${size}` : '';
        const themeClass = theme !== 'primary' ? `spinner-${theme}` : '';
        const progressValue = parseInt(progress) || 0;
        
        return `
            <div class="spinner-progress ${sizeClass} ${themeClass}" data-progress="${progressValue}">
                <div class="spinner-progress-circle"></div>
                <div class="spinner-progress-value">${progressValue}%</div>
            </div>
        `;
    }
    
    /**
     * Animate spinner message with dots
     */
    animateSpinnerMessage(element) {
        const messageContainer = element.querySelector('[data-spinner-message-container]');
        if (!messageContainer) return;
        
        const originalMessage = messageContainer.textContent;
        
        // If the message already ends with dots, don't add more
        if (originalMessage.endsWith('...')) {
            return;
        }
        
        let dotCount = 0;
        const maxDots = 3;
        
        // Set interval to animate dots
        const interval = setInterval(() => {
            // Check if the element is still in the DOM
            if (!document.body.contains(element)) {
                clearInterval(interval);
                return;
            }
            
            dotCount = (dotCount + 1) % (maxDots + 1);
            const dots = '.'.repeat(dotCount);
            
            // Get base message without dots
            const baseMessage = originalMessage.replace(/\.+$/, '');
            
            // Update message with current number of dots
            messageContainer.textContent = `${baseMessage}${dots}`;
        }, 500);
        
        // Store interval ID on the element to clear it later
        element.dataset.spinnerInterval = interval;
    }
    
    /**
     * Set up mutation observer to detect new spinners
     */
    setupMutationObserver() {
        // Create mutation observer
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // Check for added nodes with spinner attributes
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        // Check if node is an element
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Process if it has a spinner attribute
                            if (node.hasAttribute && node.hasAttribute('data-spinner')) {
                                this.initializeSpinner(node);
                            }
                            
                            // Check children for spinner attributes
                            const childSpinners = node.querySelectorAll('[data-spinner]');
                            childSpinners.forEach(element => {
                                this.initializeSpinner(element);
                            });
                        }
                    });
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Show a spinner on a target element
     */
    showSpinner(targetElement, options = {}) {
        // Default options
        const defaults = {
            type: this.config.defaultType,
            size: this.config.defaultSize,
            theme: this.config.defaultTheme,
            message: this.config.defaultMessages.loading,
            showText: this.config.showText,
            overlay: false,
            replaceContent: true
        };
        
        // Merge options
        const settings = { ...defaults, ...options };
        
        // Get target element
        let target = null;
        if (typeof targetElement === 'string') {
            target = document.querySelector(targetElement);
        } else if (targetElement instanceof Element) {
            target = targetElement;
        }
        
        if (!target) {
            console.error('Invalid target element for spinner');
            return;
        }
        
        // Create spinner container
        const spinnerContainer = document.createElement('div');
        spinnerContainer.className = settings.overlay ? 'spinner-overlay' : 'spinner-container';
        
        // Create spinner element based on type
        let spinnerHTML = '';
        
        switch (settings.type) {
            case 'border':
                spinnerHTML = this.createBorderSpinner(settings.size, settings.theme);
                break;
            case 'dots':
                spinnerHTML = this.createDotsSpinner(settings.size, settings.theme);
                break;
            case 'pulse':
                spinnerHTML = this.createPulseSpinner(settings.size, settings.theme);
                break;
            case 'dual':
                spinnerHTML = this.createDualSpinner(settings.size, settings.theme);
                break;
            case 'connection':
                spinnerHTML = this.createConnectionSpinner(settings.size, settings.theme);
                break;
            case 'progress':
                const progress = settings.progress || '0';
                spinnerHTML = this.createProgressSpinner(settings.size, settings.theme, progress);
                break;
            default:
                spinnerHTML = this.createBorderSpinner(settings.size, settings.theme);
        }
        
        // Add text if enabled
        if (settings.showText && settings.message) {
            const textHTML = `<div class="spinner-text" data-spinner-message-container>${settings.message}</div>`;
            spinnerHTML = `<div class="spinner-with-text">${spinnerHTML}${textHTML}</div>`;
        }
        
        // Set spinner HTML
        spinnerContainer.innerHTML = spinnerHTML;
        
        // Store original content if replacing
        if (settings.replaceContent) {
            spinnerContainer.dataset.originalContent = target.innerHTML;
        }
        
        // If using overlay, add to document body
        if (settings.overlay) {
            document.body.appendChild(spinnerContainer);
        } else {
            // If replacing content, clear target first
            if (settings.replaceContent) {
                target.innerHTML = '';
            }
            
            // Add spinner to target
            target.appendChild(spinnerContainer);
        }
        
        // If spinner should animate its message, start animation
        if (this.config.animateMessages && settings.showText && settings.message) {
            this.animateSpinnerMessage(spinnerContainer);
        }
        
        // Return the spinner container for later reference
        return spinnerContainer;
    }
    
    /**
     * Hide spinner and restore original content
     */
    hideSpinner(spinnerElement, removeOverlay = true) {
        // Handle different input types
        let spinner = null;
        
        if (typeof spinnerElement === 'string') {
            // If string, treat as selector
            spinner = document.querySelector(spinnerElement);
        } else if (spinnerElement instanceof Element) {
            // If element, use directly
            spinner = spinnerElement;
        }
        
        if (!spinner) {
            console.error('Invalid spinner element');
            return;
        }
        
        // Clear animation interval if exists
        if (spinner.dataset.spinnerInterval) {
            clearInterval(parseInt(spinner.dataset.spinnerInterval));
        }
        
        // Check if it's an overlay spinner
        const isOverlay = spinner.classList.contains('spinner-overlay');
        
        // If it's an overlay and we should remove it
        if (isOverlay && removeOverlay) {
            // Remove the overlay element
            if (spinner.parentNode) {
                spinner.parentNode.removeChild(spinner);
            }
            return;
        }
        
        // Check if we have original content to restore
        if (spinner.dataset.originalContent) {
            // Get parent element
            const parent = spinner.parentNode;
            if (parent) {
                // Restore original content
                parent.innerHTML = spinner.dataset.originalContent;
            }
        } else {
            // Just remove the spinner
            if (spinner.parentNode) {
                spinner.parentNode.removeChild(spinner);
            }
        }
    }
    
    /**
     * Show a full-screen overlay spinner
     */
    showOverlay(message = null, options = {}) {
        const overlayOptions = {
            ...options,
            overlay: true,
            message: message || this.config.defaultMessages.loading
        };
        
        return this.showSpinner(document.body, overlayOptions);
    }
    
    /**
     * Hide overlay spinner
     */
    hideOverlay() {
        const overlays = document.querySelectorAll('.spinner-overlay');
        overlays.forEach(overlay => {
            this.hideSpinner(overlay, true);
        });
    }
    
    /**
     * Update progress spinner value
     */
    updateProgress(spinnerElement, progress) {
        // Handle different input types
        let spinner = null;
        
        if (typeof spinnerElement === 'string') {
            // If string, treat as selector
            spinner = document.querySelector(spinnerElement);
        } else if (spinnerElement instanceof Element) {
            // If element, use directly
            spinner = spinnerElement;
        }
        
        if (!spinner) {
            console.error('Invalid spinner element');
            return;
        }
        
        // Find progress spinner
        const progressSpinner = spinner.querySelector('.spinner-progress');
        
        if (!progressSpinner) {
            console.error('No progress spinner found');
            return;
        }
        
        // Find progress value element
        const progressValue = progressSpinner.querySelector('.spinner-progress-value');
        
        if (!progressValue) {
            console.error('No progress value element found');
            return;
        }
        
        // Update progress value
        const progressInt = parseInt(progress) || 0;
        progressSpinner.dataset.progress = progressInt;
        progressValue.textContent = `${progressInt}%`;
        
        // Update progress circle with CSS
        progressSpinner.style.background = `conic-gradient(var(--bs-info) ${progressInt}%, transparent 0)`;
    }
    
    /**
     * Show platform-specific spinner
     */
    showPlatformSpinner(platform, targetElement, options = {}) {
        // Default message for platform
        const platformMessage = this.config.platformMessages[platform] || `Connecting to ${platform}...`;
        
        // Platform-specific theme
        const platformTheme = platform;
        
        // Merge options
        const settings = {
            ...options,
            theme: platformTheme,
            message: options.message || platformMessage
        };
        
        // Show spinner
        return this.showSpinner(targetElement, settings);
    }
    
    /**
     * Create inline spinner HTML (for inserting into buttons, etc.)
     */
    getInlineSpinnerHTML(theme = 'light') {
        return `<span class="spinner spinner-sm spinner-inline spinner-${theme}"></span>`;
    }
    
    /**
     * Make a button show loading state
     */
    buttonLoading(button, loadingText = null) {
        // Get button element
        let btnElement = null;
        
        if (typeof button === 'string') {
            btnElement = document.querySelector(button);
        } else if (button instanceof Element) {
            btnElement = button;
        }
        
        if (!btnElement) {
            console.error('Invalid button element');
            return;
        }
        
        // Store original button text
        const originalText = btnElement.innerHTML;
        btnElement.dataset.originalHtml = originalText;
        
        // Determine theme based on button class
        let theme = 'light';
        
        if (btnElement.classList.contains('btn-outline-dark') || 
            btnElement.classList.contains('btn-outline-light') ||
            btnElement.classList.contains('btn-light')) {
            theme = 'dark';
        }
        
        // Create loading indicator
        const spinner = this.getInlineSpinnerHTML(theme);
        
        // Set loading text
        const text = loadingText || 'Loading...';
        
        // Update button
        btnElement.innerHTML = `${spinner}${text}`;
        
        // Disable button
        btnElement.disabled = true;
        
        // Return original state restoration function
        return () => {
            btnElement.innerHTML = btnElement.dataset.originalHtml;
            btnElement.disabled = false;
        };
    }
    
    /**
     * Reset button to its original state
     */
    buttonReset(button) {
        // Get button element
        let btnElement = null;
        
        if (typeof button === 'string') {
            btnElement = document.querySelector(button);
        } else if (button instanceof Element) {
            btnElement = button;
        }
        
        if (!btnElement) {
            console.error('Invalid button element');
            return;
        }
        
        // Check if we have original HTML
        if (btnElement.dataset.originalHtml) {
            btnElement.innerHTML = btnElement.dataset.originalHtml;
        }
        
        // Enable button
        btnElement.disabled = false;
    }
}

// Initialize spinners system
const synapseSpinners = new SynapseSpinners();

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SynapseSpinners;
}