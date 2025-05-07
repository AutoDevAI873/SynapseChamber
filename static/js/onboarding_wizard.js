/**
 * Synapse Chamber - Quick Start Onboarding Wizard
 * Provides a step-by-step guide for new users to get started with the system
 * Part of the Synapse Chamber UX enhancement project
 */

class OnboardingWizard {
    constructor(options = {}) {
        this.options = Object.assign({
            storageKey: 'synapse_chamber_onboarding_completed',
            permanentHideKey: 'synapse_chamber_onboarding_hidden',
            enableAnimation: true,
            enableProgressDots: true,
            zIndex: 9998,
            outlineWidth: 4,
            animationDuration: 300,
            tooltipOffset: 10,
            backdropOpacity: 0.35,
            tooltipWidth: 300,
            tooltipClassName: 'onboarding-tooltip',
            highlightClassName: 'onboarding-highlight',
            backdropClassName: 'onboarding-backdrop',
            completeOnLastStep: true,
            steps: null
        }, options);
        
        this.currentStep = 0;
        this.overlay = null;
        this.tooltip = null;
        this.highlight = null;
        this.steps = this.options.steps || this.getDefaultSteps();
    }
    
    /**
     * Initialize onboarding wizard
     */
    init() {
        this.addStyles();
        
        // Check if this is the user's first visit
        if (this.isFirstVisit() && !this.isPermanentlyHidden()) {
            // Wait for the DOM to be fully loaded
            if (document.readyState === 'complete') {
                this.start();
            } else {
                window.addEventListener('load', () => this.start());
            }
        }
        
        // Make the wizard accessible globally
        window.OnboardingWizard = this;
        
        console.log("Synapse Chamber Onboarding Wizard initialized");
    }
    
    /**
     * Add CSS styles
     */
    addStyles() {
        if (document.getElementById('onboarding-wizard-styles')) {
            return;
        }
        
        const styleElement = document.createElement('style');
        styleElement.id = 'onboarding-wizard-styles';
        styleElement.textContent = `
            .${this.options.backdropClassName} {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, ${this.options.backdropOpacity});
                z-index: ${this.options.zIndex};
                pointer-events: auto;
            }
            
            .${this.options.tooltipClassName} {
                position: absolute;
                width: ${this.options.tooltipWidth}px;
                max-width: 90vw;
                background-color: var(--bs-dark);
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                z-index: ${this.options.zIndex + 2};
                color: white;
                animation: onboardingFadeIn ${this.options.animationDuration}ms ease;
            }
            
            .onboarding-tooltip-arrow {
                position: absolute;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 8px;
            }
            
            .onboarding-tooltip-arrow--top {
                bottom: 100%;
                border-color: transparent transparent var(--bs-dark) transparent;
            }
            
            .onboarding-tooltip-arrow--bottom {
                top: 100%;
                border-color: var(--bs-dark) transparent transparent transparent;
            }
            
            .onboarding-tooltip-arrow--left {
                right: 100%;
                border-color: transparent var(--bs-dark) transparent transparent;
            }
            
            .onboarding-tooltip-arrow--right {
                left: 100%;
                border-color: transparent transparent transparent var(--bs-dark);
            }
            
            .${this.options.highlightClassName} {
                position: absolute;
                border: ${this.options.outlineWidth}px solid var(--bs-primary);
                border-radius: 4px;
                box-shadow: 0 0 0 5000px rgba(0, 0, 0, ${this.options.backdropOpacity});
                z-index: ${this.options.zIndex + 1};
                pointer-events: none;
                box-sizing: content-box;
                transition: all ${this.options.animationDuration}ms ease;
            }
            
            .onboarding-title {
                font-size: 1.25rem;
                font-weight: bold;
                margin-bottom: 10px;
                color: var(--bs-primary);
            }
            
            .onboarding-content {
                margin-bottom: 20px;
                line-height: 1.5;
            }
            
            .onboarding-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
            }
            
            .onboarding-skip {
                color: var(--bs-secondary);
                text-decoration: underline;
                cursor: pointer;
                background: none;
                border: none;
                font-size: 0.85rem;
                padding: 5px;
            }
            
            .onboarding-nav {
                display: flex;
                gap: 10px;
            }
            
            .onboarding-button {
                background-color: var(--bs-primary);
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .onboarding-button:hover {
                background-color: var(--bs-primary-dark, #0056b3);
            }
            
            .onboarding-button--secondary {
                background-color: var(--bs-secondary);
            }
            
            .onboarding-button--secondary:hover {
                background-color: var(--bs-secondary-dark, #5a6268);
            }
            
            .onboarding-dots {
                display: flex;
                justify-content: center;
                gap: 8px;
                margin-top: 15px;
            }
            
            .onboarding-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.3);
                transition: all 0.2s ease;
            }
            
            .onboarding-dot--active {
                background-color: var(--bs-primary);
                transform: scale(1.2);
            }
            
            @keyframes onboardingFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        
        document.head.appendChild(styleElement);
    }
    
    /**
     * Start the onboarding wizard
     */
    start() {
        if (this.steps.length === 0) return;
        
        this.createOverlay();
        this.showStep(0);
        
        // Add global event listener for escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.skip();
            }
        });
    }
    
    /**
     * Show a specific step
     */
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) return;
        
        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];
        
        // Try to find the target element
        const targetElement = this.getTargetElement(step.target);
        
        if (!targetElement && step.required) {
            // If the element doesn't exist and is required, skip to next step
            console.warn(`Onboarding: Target element "${step.target}" not found. Skipping to next step.`);
            if (stepIndex < this.steps.length - 1) {
                this.showStep(stepIndex + 1);
            } else {
                this.complete();
            }
            return;
        }
        
        // Remove existing highlight
        this.removeHighlight();
        
        // Create or update tooltip
        this.createOrUpdateTooltip(step);
        
        // Highlight target element if it exists
        if (targetElement) {
            // call the highlightElement method defined in this class
            this.highlightElement(targetElement);
        }
    }
    
    /**
     * Create overlay element
     */
    createOverlay() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = this.options.backdropClassName;
        document.body.appendChild(this.overlay);
        
        // Prevent scrolling
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Create or update tooltip
     */
    createOrUpdateTooltip(step) {
        if (!this.tooltip) {
            this.tooltip = document.createElement('div');
            this.tooltip.className = this.options.tooltipClassName;
            document.body.appendChild(this.tooltip);
        }
        
        const arrowElement = document.createElement('div');
        arrowElement.className = 'onboarding-tooltip-arrow';
        
        this.tooltip.innerHTML = `
            <div class="onboarding-title">${step.title}</div>
            <div class="onboarding-content">${step.content}</div>
            ${this.options.enableProgressDots ? this.createProgressDots() : ''}
            <div class="onboarding-actions">
                <button class="onboarding-skip" id="onboarding-skip">Skip tutorial</button>
                <div class="onboarding-nav">
                    ${this.currentStep > 0 ? '<button class="onboarding-button onboarding-button--secondary" id="onboarding-prev">Previous</button>' : ''}
                    <button class="onboarding-button" id="onboarding-next">
                        ${this.currentStep < this.steps.length - 1 ? 'Next' : 'Finish'}
                    </button>
                </div>
            </div>
        `;
        
        // Add arrow to tooltip
        this.tooltip.appendChild(arrowElement);
        
        // Position tooltip
        this.positionTooltip(this.tooltip, step);
        
        // Add event listeners
        document.getElementById('onboarding-skip').addEventListener('click', () => this.skip());
        document.getElementById('onboarding-next').addEventListener('click', () => this.nextStep());
        
        if (this.currentStep > 0) {
            document.getElementById('onboarding-prev').addEventListener('click', () => this.prevStep());
        }
    }
    
    /**
     * Position tooltip relative to target element
     */
    positionTooltip(tooltip, step) {
        const targetElement = this.getTargetElement(step.target);
        
        if (!targetElement) {
            // If there's no target, center the tooltip
            tooltip.style.top = '50%';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translate(-50%, -50%)';
            return;
        }
        
        const targetRect = targetElement.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        const arrow = tooltip.querySelector('.onboarding-tooltip-arrow');
        arrow.className = 'onboarding-tooltip-arrow';
        
        // Default position (right of target)
        let position = step.position || 'right';
        
        // Auto-detect position if needed
        if (position === 'auto') {
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            
            // Calculate available space in each direction
            const spaceRight = windowWidth - (targetRect.right + this.options.tooltipOffset);
            const spaceLeft = targetRect.left - this.options.tooltipOffset;
            const spaceBelow = windowHeight - (targetRect.bottom + this.options.tooltipOffset);
            const spaceAbove = targetRect.top - this.options.tooltipOffset;
            
            // Find the direction with the most space
            const spaces = [
                { position: 'right', space: spaceRight },
                { position: 'left', space: spaceLeft },
                { position: 'bottom', space: spaceBelow },
                { position: 'top', space: spaceAbove }
            ];
            
            const bestPosition = spaces.sort((a, b) => b.space - a.space)[0];
            position = bestPosition.space > tooltipRect.width ? bestPosition.position : 'center';
        }
        
        // Calculate tooltip position
        switch (position) {
            case 'top':
                tooltip.style.left = `${targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)}px`;
                tooltip.style.top = `${targetRect.top - tooltipRect.height - this.options.tooltipOffset}px`;
                arrow.classList.add('onboarding-tooltip-arrow--bottom');
                arrow.style.left = '50%';
                arrow.style.marginLeft = '-8px';
                arrow.style.top = '100%';
                break;
                
            case 'bottom':
                tooltip.style.left = `${targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)}px`;
                tooltip.style.top = `${targetRect.bottom + this.options.tooltipOffset}px`;
                arrow.classList.add('onboarding-tooltip-arrow--top');
                arrow.style.left = '50%';
                arrow.style.marginLeft = '-8px';
                arrow.style.bottom = '100%';
                break;
                
            case 'left':
                tooltip.style.right = `${window.innerWidth - targetRect.left + this.options.tooltipOffset}px`;
                tooltip.style.top = `${targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2)}px`;
                tooltip.style.left = 'auto';
                arrow.classList.add('onboarding-tooltip-arrow--right');
                arrow.style.top = '50%';
                arrow.style.marginTop = '-8px';
                arrow.style.left = '100%';
                break;
                
            case 'right':
                tooltip.style.left = `${targetRect.right + this.options.tooltipOffset}px`;
                tooltip.style.top = `${targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2)}px`;
                arrow.classList.add('onboarding-tooltip-arrow--left');
                arrow.style.top = '50%';
                arrow.style.marginTop = '-8px';
                arrow.style.right = '100%';
                break;
                
            case 'center':
                tooltip.style.top = '50%';
                tooltip.style.left = '50%';
                tooltip.style.transform = 'translate(-50%, -50%)';
                arrow.style.display = 'none';
                break;
        }
        
        // Make sure the tooltip is within the viewport with better positioning
        const updatedTooltipRect = tooltip.getBoundingClientRect();
        const safeMargin = 20; // Ensure this much space from the edges
        
        // Check horizontal positioning
        if (updatedTooltipRect.left < safeMargin) {
            // Too close to left edge
            tooltip.style.left = `${safeMargin}px`;
            tooltip.style.right = 'auto';
            
            // Adjust arrow if we have one
            const arrow = tooltip.querySelector('.onboarding-tooltip-arrow');
            if (arrow && arrow.classList.contains('onboarding-tooltip-arrow--left')) {
                // Recalculate arrow position
                const targetCenter = targetElement ? targetElement.getBoundingClientRect().left + (targetElement.getBoundingClientRect().width / 2) : 0;
                const tooltipLeft = safeMargin;
                arrow.style.left = `${Math.max(10, targetCenter - tooltipLeft)}px`;
            }
        }
        
        if (updatedTooltipRect.right > window.innerWidth - safeMargin) {
            // Too close to right edge
            tooltip.style.right = `${safeMargin}px`;
            tooltip.style.left = 'auto';
            
            // Adjust arrow if we have one
            const arrow = tooltip.querySelector('.onboarding-tooltip-arrow');
            if (arrow && arrow.classList.contains('onboarding-tooltip-arrow--right')) {
                // Recalculate arrow position
                const targetCenter = targetElement ? targetElement.getBoundingClientRect().right - (targetElement.getBoundingClientRect().width / 2) : 0;
                const tooltipRight = window.innerWidth - safeMargin;
                arrow.style.right = `${Math.max(10, tooltipRight - targetCenter)}px`;
            }
        }
        
        // Check vertical positioning
        if (updatedTooltipRect.top < safeMargin) {
            // Too close to top edge
            tooltip.style.top = `${safeMargin}px`;
            
            // Adjust arrow if we have one
            const arrow = tooltip.querySelector('.onboarding-tooltip-arrow');
            if (arrow && arrow.classList.contains('onboarding-tooltip-arrow--top')) {
                // Recalculate arrow position
                const targetCenter = targetElement ? targetElement.getBoundingClientRect().top + (targetElement.getBoundingClientRect().height / 2) : 0;
                const tooltipTop = safeMargin;
                arrow.style.top = `${Math.max(10, targetCenter - tooltipTop)}px`;
            }
        }
        
        if (updatedTooltipRect.bottom > window.innerHeight - safeMargin) {
            // Too close to bottom edge
            tooltip.style.top = `${window.innerHeight - updatedTooltipRect.height - safeMargin}px`;
            
            // Adjust arrow if we have one
            const arrow = tooltip.querySelector('.onboarding-tooltip-arrow');
            if (arrow && arrow.classList.contains('onboarding-tooltip-arrow--bottom')) {
                // Recalculate arrow position
                const targetCenter = targetElement ? targetElement.getBoundingClientRect().bottom - (targetElement.getBoundingClientRect().height / 2) : 0;
                const tooltipBottom = window.innerHeight - safeMargin - updatedTooltipRect.height;
                arrow.style.bottom = `${Math.max(10, tooltipBottom - targetCenter)}px`;
            }
        }
    }
    
    /**
     * Highlight a target element
     */
    highlightElement(target) {
        const rect = target.getBoundingClientRect();
        
        this.highlight = document.createElement('div');
        this.highlight.className = this.options.highlightClassName;
        this.highlight.style.top = `${rect.top - this.options.outlineWidth}px`;
        this.highlight.style.left = `${rect.left - this.options.outlineWidth}px`;
        this.highlight.style.width = `${rect.width}px`;
        this.highlight.style.height = `${rect.height}px`;
        
        document.body.appendChild(this.highlight);
        
        // Make the highlighted element clickable
        if (this.options.clickableHighlight) {
            target.style.position = 'relative';
            target.style.zIndex = this.options.zIndex + 3;
        }
    }
    
    /**
     * Remove highlight from element
     */
    removeHighlight() {
        if (this.highlight) {
            this.highlight.remove();
            this.highlight = null;
        }
    }
    
    /**
     * Create progress dots HTML
     */
    createProgressDots() {
        let dotsHTML = '<div class="onboarding-dots">';
        
        for (let i = 0; i < this.steps.length; i++) {
            dotsHTML += `<div class="onboarding-dot ${i === this.currentStep ? 'onboarding-dot--active' : ''}"></div>`;
        }
        
        dotsHTML += '</div>';
        return dotsHTML;
    }
    
    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        } else {
            if (this.options.completeOnLastStep) {
                this.complete();
            }
        }
    }
    
    /**
     * Go to previous step
     */
    prevStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    /**
     * Skip the onboarding wizard
     */
    skip() {
        if (confirm('Are you sure you want to skip the onboarding tutorial? You can access it again from the help menu.')) {
            this.cleanup();
            
            // Offer to permanently hide
            if (confirm('Would you like to permanently hide the onboarding tutorial?')) {
                this.permanentlyHide();
            } else {
                // Mark as completed but allow it to be shown again later
                this.markAsCompleted();
            }
        }
    }
    
    /**
     * Complete the onboarding wizard
     */
    complete() {
        this.cleanup();
        this.markAsCompleted();
        
        // Show completion message
        alert('Onboarding complete! You can access the tutorial again from the help menu if needed.');
    }
    
    /**
     * Clean up DOM elements
     */
    cleanup() {
        // Remove overlay
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
        
        // Remove tooltip
        if (this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
        }
        
        // Remove highlight
        this.removeHighlight();
        
        // Restore scrolling
        document.body.style.overflow = '';
        
        // Remove event handlers
        document.removeEventListener('keydown', this.escHandler);
    }
    
    /**
     * Mark onboarding as completed
     */
    markAsCompleted() {
        localStorage.setItem(this.options.storageKey, 'true');
    }
    
    /**
     * Check if this is the first visit
     */
    isFirstVisit() {
        return !localStorage.getItem(this.options.storageKey);
    }
    
    /**
     * Check if onboarding is permanently hidden
     */
    isPermanentlyHidden() {
        return localStorage.getItem(this.options.permanentHideKey) === 'true';
    }
    
    /**
     * Permanently hide onboarding
     */
    permanentlyHide() {
        localStorage.setItem(this.options.permanentHideKey, 'true');
    }
    
    /**
     * Reset onboarding (clear completed status)
     */
    reset() {
        localStorage.removeItem(this.options.storageKey);
        localStorage.removeItem(this.options.permanentHideKey);
    }
    
    /**
     * Get target element from selector or element
     */
    getTargetElement(target) {
        if (!target) return null;
        
        // If target is already a DOM element, return it
        if (target instanceof Element || target instanceof HTMLElement) {
            return target;
        }
        
        // If target is a string selector, query the DOM
        if (typeof target === 'string') {
            try {
                return document.querySelector(target);
            } catch (error) {
                console.error('Invalid selector:', target, error);
                return null;
            }
        }
        
        return null;
    }
    
    /**
     * Get default onboarding steps
     */
    getDefaultSteps() {
        return [
            {
                title: "Welcome to Synapse Chamber",
                content: "This guided tour will help you understand the key features of the Synapse Chamber platform. Let's get started!",
                target: null,
                position: "center"
            },
            {
                title: "Navigation Panel",
                content: "The main navigation panel gives you access to all the major features of the platform including AI Interaction, Training, Analytics, and various tools.",
                target: ".navbar",
                position: "bottom"
            },
            {
                title: "AI Interaction",
                content: "Interact with multiple AI platforms simultaneously. Compare responses and train your agent with the best practices.",
                target: "a[href='/ai_interaction']",
                position: "right"
            },
            {
                title: "System Health Dashboard",
                content: "Monitor the status and performance of all system components, including browser automation, database connections, and AI platform status.",
                target: "a[href='/system-health']",
                position: "right"
            },
            {
                title: "Terminal",
                content: "Access the interactive terminal for direct command-line interactions with the system.",
                target: "a[href='/terminal']",
                position: "right"
            },
            {
                title: "Let's Get Started!",
                content: "You're now ready to use the Synapse Chamber. Remember, you can access this tutorial again from the help menu at any time.",
                target: null,
                position: "center"
            }
        ];
    }
}

// Initialize the onboarding wizard if script is loaded after DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(() => {
        new OnboardingWizard().init();
    }, 1000); // Slight delay to make sure everything else has loaded
} else {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            new OnboardingWizard().init();
        }, 1000);
    });
}