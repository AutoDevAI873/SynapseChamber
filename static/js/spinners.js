/**
 * Synapse Chamber - Animated Loading Spinners
 * Provides a collection of configurable, dynamic loading indicators
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseSpinners {
    constructor(options = {}) {
        this.options = Object.assign({
            containerClass: 'synapse-spinner-container',
            spinnerClass: 'synapse-spinner',
            overlayClass: 'synapse-spinner-overlay',
            textClass: 'synapse-spinner-text',
            defaultType: 'circle',
            defaultSize: 'medium',
            defaultColor: 'primary',
            zIndex: 9500,
            globalSpinner: true,
            globalSpinnerDelay: 300 // ms to wait before showing global spinner
        }, options);
        
        this.activeSpinners = [];
        this.spinnerIdCounter = 0;
        this.globalSpinnerTimeoutId = null;
        this.globalSpinner = null;
        this.ajaxRequestCount = 0;
        
        // Create spinner type templates
        this.spinnerTemplates = {
            circle: `
                <div class="synapse-spinner-circle">
                    <div></div><div></div><div></div><div></div>
                </div>
            `,
            dots: `
                <div class="synapse-spinner-dots">
                    <div></div><div></div><div></div>
                </div>
            `,
            pulse: `
                <div class="synapse-spinner-pulse">
                    <div></div>
                </div>
            `,
            bars: `
                <div class="synapse-spinner-bars">
                    <div></div><div></div><div></div><div></div><div></div>
                </div>
            `,
            grid: `
                <div class="synapse-spinner-grid">
                    <div></div><div></div><div></div>
                    <div></div><div></div><div></div>
                    <div></div><div></div><div></div>
                </div>
            `,
            ripple: `
                <div class="synapse-spinner-ripple">
                    <div></div><div></div>
                </div>
            `,
            ring: `
                <div class="synapse-spinner-ring">
                    <div></div><div></div><div></div><div></div>
                </div>
            `
        };
    }
    
    /**
     * Initialize spinners
     */
    init() {
        this.addStyles();
        
        if (this.options.globalSpinner) {
            this.setupGlobalSpinner();
        }
        
        console.log('Synapse Spinners initialized');
        
        // Make the class accessible globally
        window.SynapseSpinners = this;
    }
    
    /**
     * Add CSS styles for spinners
     */
    addStyles() {
        if (document.getElementById('synapse-spinner-styles')) {
            return;
        }
        
        const styleEl = document.createElement('style');
        styleEl.id = 'synapse-spinner-styles';
        styleEl.textContent = `
            .${this.options.containerClass} {
                display: inline-block;
                position: relative;
                line-height: 0;
            }
            
            .${this.options.overlayClass} {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: ${this.options.zIndex};
                border-radius: 4px;
            }
            
            .global-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                background-color: rgba(0, 0, 0, 0.7);
                z-index: ${this.options.zIndex + 100};
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.3s, visibility 0.3s;
            }
            
            .global-overlay.visible {
                opacity: 1;
                visibility: visible;
            }
            
            .${this.options.textClass} {
                margin-top: 15px;
                color: white;
                font-size: 1rem;
                text-align: center;
            }
            
            /* Spinner size variations */
            .${this.options.spinnerClass}--small {
                transform: scale(0.75);
            }
            
            .${this.options.spinnerClass}--medium {
                transform: scale(1);
            }
            
            .${this.options.spinnerClass}--large {
                transform: scale(1.5);
            }
            
            .${this.options.spinnerClass}--extra-large {
                transform: scale(2.5);
            }
            
            /* Spinner color variations */
            .${this.options.spinnerClass}--primary {
                --spinner-color: var(--bs-primary);
            }
            
            .${this.options.spinnerClass}--secondary {
                --spinner-color: var(--bs-secondary);
            }
            
            .${this.options.spinnerClass}--success {
                --spinner-color: var(--bs-success);
            }
            
            .${this.options.spinnerClass}--danger {
                --spinner-color: var(--bs-danger);
            }
            
            .${this.options.spinnerClass}--warning {
                --spinner-color: var(--bs-warning);
            }
            
            .${this.options.spinnerClass}--info {
                --spinner-color: var(--bs-info);
            }
            
            .${this.options.spinnerClass}--light {
                --spinner-color: var(--bs-light);
            }
            
            .${this.options.spinnerClass}--dark {
                --spinner-color: var(--bs-dark);
            }
            
            .${this.options.spinnerClass}--white {
                --spinner-color: white;
            }
            
            /* Circle spinner */
            .synapse-spinner-circle {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-circle div {
                position: absolute;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: var(--spinner-color, white);
                animation: synapse-circle 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
            }
            
            .synapse-spinner-circle div:nth-child(1) {
                animation-delay: 0s;
                top: 16px;
                left: 0;
            }
            
            .synapse-spinner-circle div:nth-child(2) {
                animation-delay: -0.3s;
                top: 8px;
                left: 8px;
            }
            
            .synapse-spinner-circle div:nth-child(3) {
                animation-delay: -0.6s;
                top: 0;
                left: 16px;
            }
            
            .synapse-spinner-circle div:nth-child(4) {
                animation-delay: -0.9s;
                top: 8px;
                left: 24px;
            }
            
            @keyframes synapse-circle {
                0% {
                    transform: scale(1);
                    opacity: 1;
                }
                100% {
                    transform: scale(0);
                    opacity: 0;
                }
            }
            
            /* Dots spinner */
            .synapse-spinner-dots {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 20px;
            }
            
            .synapse-spinner-dots div {
                position: absolute;
                width: 10px;
                height: 10px;
                background-color: var(--spinner-color, white);
                border-radius: 50%;
                animation: synapse-dots 1.4s ease-in-out infinite;
            }
            
            .synapse-spinner-dots div:nth-child(1) {
                left: 0;
                animation-delay: -0.32s;
            }
            
            .synapse-spinner-dots div:nth-child(2) {
                left: 15px;
                animation-delay: -0.16s;
            }
            
            .synapse-spinner-dots div:nth-child(3) {
                left: 30px;
                animation-delay: 0s;
            }
            
            @keyframes synapse-dots {
                0%, 80%, 100% {
                    transform: scale(0);
                }
                40% {
                    transform: scale(1);
                }
            }
            
            /* Pulse spinner */
            .synapse-spinner-pulse {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-pulse div {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background-color: var(--spinner-color, white);
                animation: synapse-pulse 1.2s cubic-bezier(0, 0.2, 0.8, 1) infinite;
            }
            
            @keyframes synapse-pulse {
                0% {
                    transform: scale(0);
                    opacity: 1;
                }
                100% {
                    transform: scale(1);
                    opacity: 0;
                }
            }
            
            /* Bars spinner */
            .synapse-spinner-bars {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-bars div {
                display: inline-block;
                position: absolute;
                left: 4px;
                width: 6px;
                background-color: var(--spinner-color, white);
                animation: synapse-bars 1.2s cubic-bezier(0, 0.5, 0.5, 1) infinite;
            }
            
            .synapse-spinner-bars div:nth-child(1) {
                left: 0;
                animation-delay: -0.24s;
            }
            
            .synapse-spinner-bars div:nth-child(2) {
                left: 10px;
                animation-delay: -0.12s;
            }
            
            .synapse-spinner-bars div:nth-child(3) {
                left: 20px;
                animation-delay: 0s;
            }
            
            .synapse-spinner-bars div:nth-child(4) {
                left: 30px;
                animation-delay: 0.12s;
            }
            
            .synapse-spinner-bars div:nth-child(5) {
                left: 40px;
                animation-delay: 0.24s;
            }
            
            @keyframes synapse-bars {
                0% {
                    top: 4px;
                    height: 32px;
                }
                50%, 100% {
                    top: 12px;
                    height: 16px;
                }
            }
            
            /* Grid spinner */
            .synapse-spinner-grid {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-grid div {
                position: absolute;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: var(--spinner-color, white);
                animation: synapse-grid 1.2s linear infinite;
            }
            
            .synapse-spinner-grid div:nth-child(1) {
                top: 6px;
                left: 6px;
                animation-delay: 0s;
            }
            
            .synapse-spinner-grid div:nth-child(2) {
                top: 6px;
                left: 16px;
                animation-delay: -0.4s;
            }
            
            .synapse-spinner-grid div:nth-child(3) {
                top: 6px;
                left: 26px;
                animation-delay: -0.8s;
            }
            
            .synapse-spinner-grid div:nth-child(4) {
                top: 16px;
                left: 6px;
                animation-delay: -0.4s;
            }
            
            .synapse-spinner-grid div:nth-child(5) {
                top: 16px;
                left: 16px;
                animation-delay: -0.8s;
            }
            
            .synapse-spinner-grid div:nth-child(6) {
                top: 16px;
                left: 26px;
                animation-delay: -1.2s;
            }
            
            .synapse-spinner-grid div:nth-child(7) {
                top: 26px;
                left: 6px;
                animation-delay: -0.8s;
            }
            
            .synapse-spinner-grid div:nth-child(8) {
                top: 26px;
                left: 16px;
                animation-delay: -1.2s;
            }
            
            .synapse-spinner-grid div:nth-child(9) {
                top: 26px;
                left: 26px;
                animation-delay: -1.6s;
            }
            
            @keyframes synapse-grid {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.5;
                }
            }
            
            /* Ripple spinner */
            .synapse-spinner-ripple {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-ripple div {
                position: absolute;
                border: 2px solid var(--spinner-color, white);
                opacity: 1;
                border-radius: 50%;
                animation: synapse-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
            }
            
            .synapse-spinner-ripple div:nth-child(2) {
                animation-delay: -0.5s;
            }
            
            @keyframes synapse-ripple {
                0% {
                    top: 20px;
                    left: 20px;
                    width: 0;
                    height: 0;
                    opacity: 1;
                }
                100% {
                    top: 0;
                    left: 0;
                    width: 40px;
                    height: 40px;
                    opacity: 0;
                }
            }
            
            /* Ring spinner */
            .synapse-spinner-ring {
                display: inline-block;
                position: relative;
                width: 40px;
                height: 40px;
            }
            
            .synapse-spinner-ring div {
                box-sizing: border-box;
                display: block;
                position: absolute;
                width: 32px;
                height: 32px;
                margin: 4px;
                border: 4px solid var(--spinner-color, white);
                border-radius: 50%;
                animation: synapse-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
                border-color: var(--spinner-color, white) transparent transparent transparent;
            }
            
            .synapse-spinner-ring div:nth-child(1) {
                animation-delay: -0.45s;
            }
            
            .synapse-spinner-ring div:nth-child(2) {
                animation-delay: -0.3s;
            }
            
            .synapse-spinner-ring div:nth-child(3) {
                animation-delay: -0.15s;
            }
            
            @keyframes synapse-ring {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }
        `;
        
        document.head.appendChild(styleEl);
    }
    
    /**
     * Set up the global spinner
     */
    setupGlobalSpinner() {
        // Create the global spinner overlay
        const overlay = document.createElement('div');
        overlay.className = 'global-overlay';
        overlay.id = 'synapse-global-spinner';
        
        // Create the spinner
        const spinner = document.createElement('div');
        spinner.className = `${this.options.spinnerClass} ${this.options.spinnerClass}--${this.options.defaultColor} ${this.options.spinnerClass}--extra-large`;
        spinner.innerHTML = this.spinnerTemplates['ring'];
        
        // Create the text element
        const text = document.createElement('div');
        text.className = this.options.textClass;
        text.textContent = 'Loading...';
        
        // Add to document
        overlay.appendChild(spinner);
        overlay.appendChild(text);
        document.body.appendChild(overlay);
        
        this.globalSpinner = overlay;
        
        // Intercept AJAX calls to show/hide global spinner
        this.interceptAjaxCalls();
    }
    
    /**
     * Intercept AJAX calls to automatically show/hide global spinner
     */
    interceptAjaxCalls() {
        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            this.incrementAjaxCounter();
            
            return originalFetch(...args)
                .then(response => {
                    this.decrementAjaxCounter();
                    return response;
                })
                .catch(error => {
                    this.decrementAjaxCounter();
                    throw error;
                });
        };
        
        // Intercept XHR requests
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(...args) {
            this._synapseSentTime = Date.now();
            return originalOpen.apply(this, args);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            this.addEventListener('readystatechange', function() {
                if (this.readyState === 1) {
                    // Request started
                    window.SynapseSpinners.incrementAjaxCounter();
                }
                if (this.readyState === 4) {
                    // Request completed
                    window.SynapseSpinners.decrementAjaxCounter();
                }
            });
            return originalSend.apply(this, args);
        };
    }
    
    /**
     * Increment the AJAX request counter
     */
    incrementAjaxCounter() {
        this.ajaxRequestCount++;
        
        // Show the global spinner if not already visible
        if (this.ajaxRequestCount === 1) {
            // Use a delay to prevent flickering for very fast requests
            clearTimeout(this.globalSpinnerTimeoutId);
            this.globalSpinnerTimeoutId = setTimeout(() => {
                if (this.ajaxRequestCount > 0) {
                    this.showGlobalSpinner();
                }
            }, this.options.globalSpinnerDelay);
        }
    }
    
    /**
     * Decrement the AJAX request counter
     */
    decrementAjaxCounter() {
        if (this.ajaxRequestCount > 0) {
            this.ajaxRequestCount--;
        }
        
        // Hide the global spinner if no more requests are pending
        if (this.ajaxRequestCount === 0) {
            clearTimeout(this.globalSpinnerTimeoutId);
            this.hideGlobalSpinner();
        }
    }
    
    /**
     * Show the global spinner
     */
    showGlobalSpinner(text = 'Loading...') {
        if (this.globalSpinner) {
            const textEl = this.globalSpinner.querySelector(`.${this.options.textClass}`);
            if (textEl) {
                textEl.textContent = text;
            }
            
            this.globalSpinner.classList.add('visible');
        }
    }
    
    /**
     * Hide the global spinner
     */
    hideGlobalSpinner() {
        if (this.globalSpinner) {
            this.globalSpinner.classList.remove('visible');
        }
    }
    
    /**
     * Create a spinner container
     */
    createSpinner(options = {}) {
        const settings = Object.assign({
            type: this.options.defaultType,
            size: this.options.defaultSize,
            color: this.options.defaultColor,
            target: null,
            text: null,
            overlay: false,
            id: null
        }, options);
        
        // Generate an ID if not provided
        const spinnerId = settings.id || `synapse-spinner-${++this.spinnerIdCounter}`;
        
        // Create the spinner component
        const spinnerComponent = document.createElement('div');
        spinnerComponent.className = `${this.options.spinnerClass} ${this.options.spinnerClass}--${settings.size} ${this.options.spinnerClass}--${settings.color}`;
        spinnerComponent.id = spinnerId;
        
        // Add the spinner template HTML
        if (this.spinnerTemplates[settings.type]) {
            spinnerComponent.innerHTML = this.spinnerTemplates[settings.type];
        } else {
            spinnerComponent.innerHTML = this.spinnerTemplates[this.options.defaultType];
        }
        
        // Add text if provided
        if (settings.text) {
            const textElement = document.createElement('div');
            textElement.className = this.options.textClass;
            textElement.textContent = settings.text;
            spinnerComponent.appendChild(textElement);
        }
        
        // If a target is provided, add the spinner to it
        if (settings.target) {
            const targetElement = typeof settings.target === 'string' ? document.querySelector(settings.target) : settings.target;
            
            if (targetElement) {
                // Remember the original position if needed
                if (getComputedStyle(targetElement).position === 'static') {
                    targetElement.style.position = 'relative';
                }
                
                if (settings.overlay) {
                    // Create an overlay on the target
                    const overlay = document.createElement('div');
                    overlay.className = this.options.overlayClass;
                    overlay.id = `${spinnerId}-overlay`;
                    overlay.appendChild(spinnerComponent);
                    
                    targetElement.appendChild(overlay);
                } else {
                    // If not an overlay, position depends on the target's style
                    const container = document.createElement('div');
                    container.className = this.options.containerClass;
                    container.id = `${spinnerId}-container`;
                    container.appendChild(spinnerComponent);
                    
                    targetElement.appendChild(container);
                }
                
                // Store spinner reference for later removal
                this.activeSpinners.push({
                    id: spinnerId,
                    element: spinnerComponent,
                    target: targetElement,
                    overlay: settings.overlay
                });
            }
        }
        
        return spinnerId;
    }
    
    /**
     * Remove a spinner by ID
     */
    removeSpinner(spinnerId) {
        const spinnerIndex = this.activeSpinners.findIndex(spinner => spinner.id === spinnerId);
        
        if (spinnerIndex !== -1) {
            const spinner = this.activeSpinners[spinnerIndex];
            
            if (spinner.overlay) {
                // Remove overlay element
                const overlay = document.getElementById(`${spinnerId}-overlay`);
                if (overlay && overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            } else {
                // Remove container element
                const container = document.getElementById(`${spinnerId}-container`);
                if (container && container.parentNode) {
                    container.parentNode.removeChild(container);
                }
            }
            
            // Remove from active spinners array
            this.activeSpinners.splice(spinnerIndex, 1);
            
            return true;
        }
        
        return false;
    }
    
    /**
     * Remove all spinners
     */
    removeAllSpinners() {
        while (this.activeSpinners.length > 0) {
            this.removeSpinner(this.activeSpinners[0].id);
        }
    }
    
    /**
     * Add a spinner overlay to an element
     */
    addSpinnerOverlay(target, text = 'Loading...', options = {}) {
        return this.createSpinner({
            target: target,
            text: text,
            overlay: true,
            ...options
        });
    }
    
    /**
     * Replace an element's content with a spinner
     */
    replaceWithSpinner(target, text = 'Loading...', options = {}) {
        const targetElement = typeof target === 'string' ? document.querySelector(target) : target;
        
        if (targetElement) {
            // Store the original content
            targetElement._originalHTML = targetElement.innerHTML;
            
            // Clear the content
            targetElement.innerHTML = '';
            
            // Add the spinner
            const spinnerId = this.createSpinner({
                target: targetElement,
                text: text,
                ...options
            });
            
            return {
                id: spinnerId,
                restore: () => {
                    // Restore the original content
                    if (targetElement._originalHTML !== undefined) {
                        targetElement.innerHTML = targetElement._originalHTML;
                        delete targetElement._originalHTML;
                    }
                    
                    // Remove the spinner
                    this.removeSpinner(spinnerId);
                }
            };
        }
        
        return null;
    }
    
    /**
     * Replace a button with a spinner
     */
    replaceButtonWithSpinner(button, text = 'Processing...') {
        const buttonElement = typeof button === 'string' ? document.querySelector(button) : button;
        
        if (buttonElement && buttonElement.tagName === 'BUTTON') {
            // Store original content and disabled state
            buttonElement._originalHTML = buttonElement.innerHTML;
            buttonElement._originalDisabled = buttonElement.disabled;
            
            // Disable the button
            buttonElement.disabled = true;
            
            // Clear content and add spinner
            buttonElement.innerHTML = `
                <span class="d-flex align-items-center">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    ${text}
                </span>
            `;
            
            // Return a restore function
            return () => {
                if (buttonElement._originalHTML !== undefined) {
                    buttonElement.innerHTML = buttonElement._originalHTML;
                    buttonElement.disabled = buttonElement._originalDisabled;
                    
                    delete buttonElement._originalHTML;
                    delete buttonElement._originalDisabled;
                }
            };
        }
        
        return null;
    }
}

// Initialize the spinners if script is loaded after DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(() => {
        window.synapseSpinners = new SynapseSpinners();
        window.synapseSpinners.init();
    }, 0);
} else {
    document.addEventListener('DOMContentLoaded', () => {
        window.synapseSpinners = new SynapseSpinners();
        window.synapseSpinners.init();
    });
}