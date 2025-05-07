/**
 * Synapse Chamber - Loading Spinners
 * Provides animated indicators for loading states
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseSpinners {
    constructor(options = {}) {
        this.options = Object.assign({
            defaultType: 'circle',
            defaultColor: 'primary',
            defaultSize: 'md'
        }, options);
    }

    /**
     * Initialize the spinners system
     */
    init() {
        // Add event handlers for buttons with spinners
        this.initButtonSpinners();
        
        // Make available globally
        window.SynapseSpinners = this;
        
        console.log('Synapse Spinners initialized');
    }
    
    /**
     * Initialize spinners for buttons
     */
    initButtonSpinners() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('[data-spinner-button]');
            if (button) {
                // Check if the button should show a spinner on click
                const shouldSpin = button.getAttribute('data-spinner-button') !== 'false';
                if (shouldSpin && !button.classList.contains('btn--loading')) {
                    // Create a spinner element
                    const spinnerType = button.getAttribute('data-spinner-type') || this.options.defaultType;
                    const spinnerColor = button.getAttribute('data-spinner-color') || this.options.defaultColor;
                    const spinnerSize = button.getAttribute('data-spinner-size') || 'sm';
                    
                    // Add spinner to button
                    this.addSpinnerToButton(button, spinnerType, spinnerColor, spinnerSize);
                    
                    // Add loading class to button
                    button.classList.add('btn--loading');
                    
                    // Get loading delay
                    const delay = parseInt(button.getAttribute('data-spinner-delay') || '0', 10);
                    
                    // Auto-remove after delay if specified
                    const autoRemove = button.getAttribute('data-spinner-auto-remove');
                    if (autoRemove) {
                        setTimeout(() => {
                            this.removeSpinnerFromButton(button);
                        }, parseInt(autoRemove, 10));
                    }
                }
            }
        });
    }
    
    /**
     * Add a spinner to a button
     */
    addSpinnerToButton(button, type, color, size) {
        // Create the spinner element
        const spinner = this.createSpinner(type, color, size);
        
        // Store the button's original content
        button._originalContent = button.innerHTML;
        
        // Insert the spinner at the beginning of the button
        button.insertBefore(spinner, button.firstChild);
    }
    
    /**
     * Remove spinner from a button
     */
    removeSpinnerFromButton(button) {
        // Remove the loading state class
        button.classList.remove('btn--loading');
        
        // Restore the original content if saved
        if (button._originalContent) {
            button.innerHTML = button._originalContent;
            delete button._originalContent;
        } else {
            // Otherwise, just remove the first child if it's a spinner
            const spinnerElement = button.querySelector('.synapse-spinner');
            if (spinnerElement) {
                spinnerElement.remove();
            }
        }
    }
    
    /**
     * Create a spinner element
     */
    createSpinner(type = 'circle', color = 'primary', size = 'md') {
        // Create the base spinner element
        const spinner = document.createElement('div');
        spinner.className = `synapse-spinner synapse-spinner--${type} synapse-spinner--${color} synapse-spinner--${size}`;
        
        // Add additional elements based on spinner type
        switch (type) {
            case 'wave':
                // Wave spinner needs 5 bar elements
                for (let i = 0; i < 5; i++) {
                    const bar = document.createElement('div');
                    bar.className = 'synapse-spinner__bar';
                    spinner.appendChild(bar);
                }
                break;
                
            case 'grid':
                // Grid spinner needs 9 cell elements
                for (let i = 0; i < 9; i++) {
                    const cell = document.createElement('div');
                    cell.className = 'synapse-spinner__cell';
                    spinner.appendChild(cell);
                }
                break;
                
            case 'progress':
                // SVG based progress indicator
                spinner.innerHTML = `
                    <svg viewBox="0 0 100 100">
                        <circle class="synapse-progress__track" cx="50" cy="50" r="45" />
                        <circle class="synapse-progress__indicator" cx="50" cy="50" r="45" stroke-dasharray="283" stroke-dashoffset="283" />
                        <text class="synapse-progress__label" x="50" y="50" text-anchor="middle" dominant-baseline="middle">0%</text>
                    </svg>
                `;
                break;
        }
        
        return spinner;
    }
    
    /**
     * Create a spinner with a loading message
     */
    createSpinnerWithMessage(message, type = 'circle', color = 'primary', size = 'md', isBlock = false) {
        // Create container
        const container = document.createElement('div');
        container.className = `synapse-spinner-container ${isBlock ? 'synapse-spinner-container--block' : ''}`;
        
        // Add the spinner
        const spinner = this.createSpinner(type, color, size);
        container.appendChild(spinner);
        
        // Add the message
        if (message) {
            const messageElement = document.createElement('div');
            messageElement.className = 'synapse-spinner-container__message';
            messageElement.textContent = message;
            container.appendChild(messageElement);
        }
        
        return container;
    }
    
    /**
     * Show a full-page loading overlay
     */
    showOverlay(message = 'Loading...', type = 'circle', color = 'light', size = 'xl') {
        // Remove existing overlay if any
        this.hideOverlay();
        
        // Create overlay container
        const overlay = document.createElement('div');
        overlay.className = 'synapse-spinner-overlay';
        overlay.id = 'synapse-spinner-overlay';
        
        // Create spinner
        const spinner = this.createSpinner(type, color, size);
        overlay.appendChild(spinner);
        
        // Add message if provided
        if (message) {
            const messageElement = document.createElement('div');
            messageElement.className = 'synapse-spinner-overlay__message';
            messageElement.textContent = message;
            overlay.appendChild(messageElement);
        }
        
        // Add to document
        document.body.appendChild(overlay);
        
        // Prevent scrolling
        document.body.style.overflow = 'hidden';
        
        return overlay;
    }
    
    /**
     * Hide the loading overlay
     */
    hideOverlay() {
        const overlay = document.getElementById('synapse-spinner-overlay');
        if (overlay) {
            overlay.remove();
            
            // Restore scrolling
            document.body.style.overflow = '';
        }
    }
    
    /**
     * Show a loading state for a specific element
     */
    showLoadingState(element, type = 'circle', color = 'primary', size = 'md', message = null) {
        // Save the original content
        element._originalContent = element.innerHTML;
        
        // Clear the element
        element.innerHTML = '';
        
        // Create spinner with optional message
        const spinnerContainer = this.createSpinnerWithMessage(message, type, color, size, true);
        
        // Add loading class
        element.classList.add('synapse-loading');
        
        // Insert the spinner
        element.appendChild(spinnerContainer);
        
        return spinnerContainer;
    }
    
    /**
     * Hide loading state and restore original content
     */
    hideLoadingState(element) {
        // Remove loading class
        element.classList.remove('synapse-loading');
        
        // Restore original content if available
        if (element._originalContent) {
            element.innerHTML = element._originalContent;
            delete element._originalContent;
        } else {
            // Just remove the spinner
            const spinner = element.querySelector('.synapse-spinner-container');
            if (spinner) {
                spinner.remove();
            }
        }
    }
    
    /**
     * Update a progress spinner
     */
    updateProgress(spinnerElement, progress) {
        // Ensure the element is a progress spinner
        if (!spinnerElement.classList.contains('synapse-spinner--progress')) {
            console.error('Element is not a progress spinner');
            return;
        }
        
        // Find the indicator and label
        const indicator = spinnerElement.querySelector('.synapse-progress__indicator');
        const label = spinnerElement.querySelector('.synapse-progress__label');
        
        if (indicator && label) {
            // Clamp progress between 0 and 100
            const clampedProgress = Math.max(0, Math.min(100, progress));
            
            // Calculate the dash offset (283 is the circumference of the circle with r=45)
            const circumference = 283;
            const dashOffset = circumference - (circumference * clampedProgress / 100);
            
            // Update the indicator
            indicator.style.strokeDashoffset = dashOffset;
            
            // Update the label
            label.textContent = `${Math.round(clampedProgress)}%`;
        }
    }
}

// Initialize spinners if script is loaded after DOM is ready
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