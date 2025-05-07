/**
 * Synapse Chamber - Quick Start Onboarding Wizard
 * Provides a step-by-step guide for new users to get started with the system
 * Part of the Synapse Chamber UX enhancement project
 */

class OnboardingWizard {
    constructor(options = {}) {
        // Configuration
        this.config = {
            showOnFirstVisit: options.showOnFirstVisit !== undefined ? options.showOnFirstVisit : true,
            storageKey: options.storageKey || 'synapse_onboarding_completed',
            steps: options.steps || this.getDefaultSteps(),
            onComplete: options.onComplete || null,
            onSkip: options.onSkip || null,
            autoStart: options.autoStart !== undefined ? options.autoStart : false,
            theme: options.theme || 'dark',
            showSkip: options.showSkip !== undefined ? options.showSkip : true,
            showProgress: options.showProgress !== undefined ? options.showProgress : true,
            animateTransitions: options.animateTransitions !== undefined ? options.animateTransitions : true,
            overlayOpacity: options.overlayOpacity || 0.7,
            zIndex: options.zIndex || 10000,
            onBeforeStep: options.onBeforeStep || null,
            onAfterStep: options.onAfterStep || null
        };
        
        // State
        this.currentStep = 0;
        this.totalSteps = this.config.steps.length;
        this.isActive = false;
        this.highlightedElement = null;
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize onboarding wizard
     */
    init() {
        // Add CSS styles
        this.addStyles();
        
        // Automatically start on first visit if configured
        if (this.config.showOnFirstVisit && this.isFirstVisit() && !this.isPermanentlyHidden()) {
            // Start on a slight delay to ensure page is fully loaded
            setTimeout(() => {
                this.start();
            }, 1000);
        } else if (this.config.autoStart && !this.isPermanentlyHidden()) {
            // Auto-start if configured
            setTimeout(() => {
                this.start();
            }, 1000);
        }
    }
    
    /**
     * Add CSS styles
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .onboarding-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, ${this.config.overlayOpacity});
                z-index: ${this.config.zIndex};
                display: ${this.isActive ? 'block' : 'none'};
            }
            
            .onboarding-spotlight {
                position: absolute;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, ${this.config.overlayOpacity});
                border-radius: 4px;
                z-index: ${this.config.zIndex + 1};
                pointer-events: none;
                transition: all 0.3s ease;
            }
            
            .onboarding-tooltip {
                position: absolute;
                background-color: ${this.config.theme === 'dark' ? '#2d2d2d' : '#ffffff'};
                color: ${this.config.theme === 'dark' ? '#ffffff' : '#333333'};
                border-radius: 8px;
                padding: 20px;
                width: 300px;
                max-width: 90vw;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                z-index: ${this.config.zIndex + 2};
                font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            
            .onboarding-tooltip-arrow {
                position: absolute;
                width: 16px;
                height: 16px;
                background-color: ${this.config.theme === 'dark' ? '#2d2d2d' : '#ffffff'};
                transform: rotate(45deg);
                z-index: ${this.config.zIndex + 1};
            }
            
            .onboarding-tooltip-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: ${this.config.theme === 'dark' ? '#ffffff' : '#333333'};
            }
            
            .onboarding-tooltip-content {
                font-size: 14px;
                line-height: 1.5;
                margin-bottom: 20px;
                color: ${this.config.theme === 'dark' ? '#dddddd' : '#666666'};
            }
            
            .onboarding-tooltip-buttons {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .onboarding-tooltip-button {
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                border: none;
                transition: background-color 0.2s;
            }
            
            .onboarding-tooltip-button-next {
                background-color: #0d6efd;
                color: white;
            }
            
            .onboarding-tooltip-button-next:hover {
                background-color: #0b5ed7;
            }
            
            .onboarding-tooltip-button-prev {
                background-color: ${this.config.theme === 'dark' ? '#444444' : '#e9ecef'};
                color: ${this.config.theme === 'dark' ? '#ffffff' : '#333333'};
                margin-right: 10px;
            }
            
            .onboarding-tooltip-button-prev:hover {
                background-color: ${this.config.theme === 'dark' ? '#555555' : '#dee2e6'};
            }
            
            .onboarding-tooltip-button-skip {
                background-color: transparent;
                color: ${this.config.theme === 'dark' ? '#aaaaaa' : '#6c757d'};
                text-decoration: underline;
                padding: 8px;
            }
            
            .onboarding-tooltip-button-skip:hover {
                color: ${this.config.theme === 'dark' ? '#ffffff' : '#5a6268'};
            }
            
            .onboarding-tooltip-progress {
                display: flex;
                justify-content: center;
                margin-top: 15px;
                gap: 6px;
            }
            
            .onboarding-tooltip-progress-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: ${this.config.theme === 'dark' ? '#555555' : '#dee2e6'};
            }
            
            .onboarding-tooltip-progress-dot.active {
                background-color: #0d6efd;
            }
            
            .onboarding-tooltip-image {
                width: 100%;
                max-height: 150px;
                object-fit: contain;
                margin-bottom: 15px;
                border-radius: 4px;
            }
            
            /* Animation classes */
            .onboarding-fadein {
                animation: onboardingFadeIn 0.3s forwards;
            }
            
            .onboarding-fadeout {
                animation: onboardingFadeOut 0.3s forwards;
            }
            
            @keyframes onboardingFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes onboardingFadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
            
            /* Mobile responsive adjustments */
            @media (max-width: 768px) {
                .onboarding-tooltip {
                    width: 85vw;
                    font-size: 14px;
                    padding: 15px;
                }
                
                .onboarding-tooltip-title {
                    font-size: 16px;
                }
                
                .onboarding-tooltip-content {
                    font-size: 13px;
                }
                
                .onboarding-tooltip-button {
                    padding: 6px 12px;
                    font-size: 13px;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * Start the onboarding wizard
     */
    start() {
        if (this.isActive || this.isPermanentlyHidden()) return;
        
        this.isActive = true;
        this.currentStep = 0;
        
        // Create overlay
        this.createOverlay();
        
        // Show first step
        this.showStep(0);
    }
    
    /**
     * Show a specific step
     */
    showStep(stepIndex) {
        // Validate step index
        if (stepIndex < 0 || stepIndex >= this.totalSteps) return;
        
        // Update current step
        this.currentStep = stepIndex;
        
        // Get step configuration
        const step = this.config.steps[stepIndex];
        
        // Call before step callback if defined
        if (typeof this.config.onBeforeStep === 'function') {
            this.config.onBeforeStep(step, stepIndex);
        }
        
        // Create or update tooltip
        this.createOrUpdateTooltip(step);
        
        // Highlight target element if provided
        if (step.target) {
            this.highlightElement(step.target);
        } else {
            this.removeHighlight();
        }
        
        // Call after step callback if defined
        if (typeof this.config.onAfterStep === 'function') {
            this.config.onAfterStep(step, stepIndex);
        }
    }
    
    /**
     * Create overlay element
     */
    createOverlay() {
        // Check if overlay already exists
        let overlay = document.querySelector('.onboarding-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'onboarding-overlay';
            
            // Add animation if enabled
            if (this.config.animateTransitions) {
                overlay.classList.add('onboarding-fadein');
            }
            
            document.body.appendChild(overlay);
            
            // Add click handler to close when clicking on overlay if allowed
            if (this.config.showSkip) {
                overlay.addEventListener('click', (e) => {
                    if (e.target === overlay) {
                        this.skip();
                    }
                });
            }
        } else {
            overlay.style.display = 'block';
        }
    }
    
    /**
     * Create or update tooltip
     */
    createOrUpdateTooltip(step) {
        // Check if tooltip already exists
        let tooltip = document.querySelector('.onboarding-tooltip');
        let isNew = false;
        
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.className = 'onboarding-tooltip';
            
            // Add animation if enabled
            if (this.config.animateTransitions) {
                tooltip.classList.add('onboarding-fadein');
            }
            
            document.body.appendChild(tooltip);
            isNew = true;
        }
        
        // Create tooltip content
        let tooltipContent = `
            ${step.title ? `<div class="onboarding-tooltip-title">${step.title}</div>` : ''}
            ${step.image ? `<img src="${step.image}" alt="${step.title || 'Onboarding'}" class="onboarding-tooltip-image">` : ''}
            <div class="onboarding-tooltip-content">${step.content}</div>
            <div class="onboarding-tooltip-buttons">
                <div>
                    ${this.currentStep > 0 ? `<button class="onboarding-tooltip-button onboarding-tooltip-button-prev">Previous</button>` : ''}
                    ${this.config.showSkip ? `<button class="onboarding-tooltip-button onboarding-tooltip-button-skip">${this.currentStep === this.totalSteps - 1 ? 'Close' : 'Skip'}</button>` : ''}
                </div>
                <button class="onboarding-tooltip-button onboarding-tooltip-button-next">${this.currentStep === this.totalSteps - 1 ? 'Finish' : 'Next'}</button>
            </div>
            ${this.config.showProgress && this.totalSteps > 1 ? this.createProgressDots() : ''}
        `;
        
        tooltip.innerHTML = tooltipContent;
        
        // Position tooltip
        this.positionTooltip(tooltip, step);
        
        // Add event listeners if this is a new tooltip
        if (isNew) {
            tooltip.addEventListener('click', (e) => {
                const target = e.target;
                
                if (target.classList.contains('onboarding-tooltip-button-next')) {
                    this.nextStep();
                } else if (target.classList.contains('onboarding-tooltip-button-prev')) {
                    this.prevStep();
                } else if (target.classList.contains('onboarding-tooltip-button-skip')) {
                    this.skip();
                }
            });
        }
    }
    
    /**
     * Position tooltip relative to target element
     */
    positionTooltip(tooltip, step) {
        // Default position (center of screen) if no target
        let position = { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
        
        // Create arrow element
        let arrow = document.querySelector('.onboarding-tooltip-arrow');
        if (!arrow) {
            arrow = document.createElement('div');
            arrow.className = 'onboarding-tooltip-arrow';
            document.body.appendChild(arrow);
        }
        
        // Hide arrow by default
        arrow.style.display = 'none';
        
        if (step.target) {
            const targetEl = this.getTargetElement(step.target);
            
            if (targetEl) {
                const targetRect = targetEl.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                
                // Calculate tooltip position based on placement
                const placement = step.placement || 'bottom';
                
                // Calculate position
                switch (placement) {
                    case 'top':
                        position = {
                            top: `${targetRect.top - tooltipRect.height - 15}px`,
                            left: `${targetRect.left + targetRect.width / 2 - tooltipRect.width / 2}px`,
                            transform: 'none'
                        };
                        break;
                    case 'bottom':
                        position = {
                            top: `${targetRect.bottom + 15}px`,
                            left: `${targetRect.left + targetRect.width / 2 - tooltipRect.width / 2}px`,
                            transform: 'none'
                        };
                        break;
                    case 'left':
                        position = {
                            top: `${targetRect.top + targetRect.height / 2 - tooltipRect.height / 2}px`,
                            left: `${targetRect.left - tooltipRect.width - 15}px`,
                            transform: 'none'
                        };
                        break;
                    case 'right':
                        position = {
                            top: `${targetRect.top + targetRect.height / 2 - tooltipRect.height / 2}px`,
                            left: `${targetRect.right + 15}px`,
                            transform: 'none'
                        };
                        break;
                }
                
                // Adjust for viewport boundaries
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;
                
                // Ensure tooltip doesn't go off screen horizontally
                if (parseFloat(position.left) < 10) {
                    position.left = '10px';
                } else if (parseFloat(position.left) + tooltipRect.width > viewportWidth - 10) {
                    position.left = `${viewportWidth - tooltipRect.width - 10}px`;
                }
                
                // Ensure tooltip doesn't go off screen vertically
                if (parseFloat(position.top) < 10) {
                    position.top = '10px';
                } else if (parseFloat(position.top) + tooltipRect.height > viewportHeight - 10) {
                    position.top = `${viewportHeight - tooltipRect.height - 10}px`;
                }
                
                // Position arrow
                arrow.style.display = 'block';
                
                switch (placement) {
                    case 'top':
                        arrow.style.top = `${targetRect.top - 8}px`;
                        arrow.style.left = `${targetRect.left + targetRect.width / 2 - 8}px`;
                        break;
                    case 'bottom':
                        arrow.style.top = `${targetRect.bottom - 8}px`;
                        arrow.style.left = `${targetRect.left + targetRect.width / 2 - 8}px`;
                        break;
                    case 'left':
                        arrow.style.top = `${targetRect.top + targetRect.height / 2 - 8}px`;
                        arrow.style.left = `${targetRect.left - 8}px`;
                        break;
                    case 'right':
                        arrow.style.top = `${targetRect.top + targetRect.height / 2 - 8}px`;
                        arrow.style.left = `${targetRect.right - 8}px`;
                        break;
                }
            }
        }
        
        // Apply position to tooltip
        Object.assign(tooltip.style, position);
    }
    
    /**
     * Highlight a target element
     */
    highlightElement(target) {
        const targetEl = this.getTargetElement(target);
        
        if (!targetEl) {
            this.removeHighlight();
            return;
        }
        
        const targetRect = targetEl.getBoundingClientRect();
        
        // Create or update spotlight
        let spotlight = document.querySelector('.onboarding-spotlight');
        
        if (!spotlight) {
            spotlight = document.createElement('div');
            spotlight.className = 'onboarding-spotlight';
            document.body.appendChild(spotlight);
        }
        
        // Position spotlight
        spotlight.style.top = `${targetRect.top - 5}px`;
        spotlight.style.left = `${targetRect.left - 5}px`;
        spotlight.style.width = `${targetRect.width + 10}px`;
        spotlight.style.height = `${targetRect.height + 10}px`;
        
        // Store reference to highlighted element
        this.highlightedElement = targetEl;
        
        // Make target clickable
        targetEl.style.position = 'relative';
        targetEl.style.zIndex = this.config.zIndex + 3;
    }
    
    /**
     * Remove highlight from element
     */
    removeHighlight() {
        // Remove spotlight
        const spotlight = document.querySelector('.onboarding-spotlight');
        if (spotlight) {
            spotlight.remove();
        }
        
        // Reset highlighted element z-index
        if (this.highlightedElement) {
            this.highlightedElement.style.zIndex = '';
            this.highlightedElement = null;
        }
    }
    
    /**
     * Create progress dots HTML
     */
    createProgressDots() {
        let dotsHtml = '<div class="onboarding-tooltip-progress">';
        
        for (let i = 0; i < this.totalSteps; i++) {
            dotsHtml += `<div class="onboarding-tooltip-progress-dot ${i === this.currentStep ? 'active' : ''}"></div>`;
        }
        
        dotsHtml += '</div>';
        
        return dotsHtml;
    }
    
    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep === this.totalSteps - 1) {
            this.complete();
        } else {
            this.showStep(this.currentStep + 1);
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
        // Add fadeout animation if enabled
        if (this.config.animateTransitions) {
            const overlay = document.querySelector('.onboarding-overlay');
            const tooltip = document.querySelector('.onboarding-tooltip');
            const arrow = document.querySelector('.onboarding-tooltip-arrow');
            
            if (overlay) overlay.classList.add('onboarding-fadeout');
            if (tooltip) tooltip.classList.add('onboarding-fadeout');
            if (arrow) arrow.classList.add('onboarding-fadeout');
            
            // Wait for animation to complete
            setTimeout(() => {
                this.cleanup();
            }, 300);
        } else {
            this.cleanup();
        }
        
        // Mark as completed
        this.markAsCompleted();
        
        // Call onSkip callback if defined
        if (typeof this.config.onSkip === 'function') {
            this.config.onSkip();
        }
    }
    
    /**
     * Complete the onboarding wizard
     */
    complete() {
        // Add fadeout animation if enabled
        if (this.config.animateTransitions) {
            const overlay = document.querySelector('.onboarding-overlay');
            const tooltip = document.querySelector('.onboarding-tooltip');
            const arrow = document.querySelector('.onboarding-tooltip-arrow');
            
            if (overlay) overlay.classList.add('onboarding-fadeout');
            if (tooltip) tooltip.classList.add('onboarding-fadeout');
            if (arrow) arrow.classList.add('onboarding-fadeout');
            
            // Wait for animation to complete
            setTimeout(() => {
                this.cleanup();
            }, 300);
        } else {
            this.cleanup();
        }
        
        // Mark as completed
        this.markAsCompleted();
        
        // Call onComplete callback if defined
        if (typeof this.config.onComplete === 'function') {
            this.config.onComplete();
        }
    }
    
    /**
     * Clean up DOM elements
     */
    cleanup() {
        // Remove highlight
        this.removeHighlight();
        
        // Remove overlay
        const overlay = document.querySelector('.onboarding-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Remove tooltip
        const tooltip = document.querySelector('.onboarding-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
        
        // Remove arrow
        const arrow = document.querySelector('.onboarding-tooltip-arrow');
        if (arrow) {
            arrow.remove();
        }
        
        // Reset state
        this.isActive = false;
    }
    
    /**
     * Mark onboarding as completed
     */
    markAsCompleted() {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(this.config.storageKey, 'true');
        }
    }
    
    /**
     * Check if this is the first visit
     */
    isFirstVisit() {
        if (typeof localStorage !== 'undefined') {
            return !localStorage.getItem(this.config.storageKey);
        }
        return true;
    }
    
    /**
     * Check if onboarding is permanently hidden
     */
    isPermanentlyHidden() {
        if (typeof localStorage !== 'undefined') {
            return localStorage.getItem(this.config.storageKey + '_hidden') === 'true';
        }
        return false;
    }
    
    /**
     * Permanently hide onboarding
     */
    permanentlyHide() {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(this.config.storageKey + '_hidden', 'true');
        }
    }
    
    /**
     * Reset onboarding (clear completed status)
     */
    reset() {
        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem(this.config.storageKey);
            localStorage.removeItem(this.config.storageKey + '_hidden');
        }
    }
    
    /**
     * Get target element from selector or element
     */
    getTargetElement(target) {
        if (target instanceof Element) {
            return target;
        } else if (typeof target === 'string') {
            return document.querySelector(target);
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
                content: "This guided tour will introduce you to the key features of Synapse Chamber, your AI agent training environment. Let's get started!",
                placement: "center"
            },
            {
                title: "AI Platform Integration",
                content: "Synapse Chamber connects with multiple AI platforms including ChatGPT, Claude, Gemini, Grok, and DeepSeek. Use the platform selector to choose which AIs to train with.",
                target: ".platform-selector",
                placement: "bottom"
            },
            {
                title: "Training System",
                content: "The training interface allows you to create structured learning experiences for your AI agent. Select topics, create prompts, and review AI responses to build your agent's knowledge.",
                target: "#training-tab",
                placement: "bottom"
            },
            {
                title: "Memory System",
                content: "The memory explorer provides access to stored conversations and knowledge. Use semantic search to find specific information and visualize connections between concepts.",
                target: "#memory-tab",
                placement: "bottom"
            },
            {
                title: "Development Environment",
                content: "The built-in development environment includes file management, code editing, and terminal access - everything you need to refine your agent's capabilities.",
                target: "#dev-tab",
                placement: "bottom"
            },
            {
                title: "System Health Dashboard",
                content: "Monitor the performance and status of all Synapse Chamber components through the System Health Dashboard. Get real-time metrics and address issues before they impact your work.",
                target: "#system-health-dashboard",
                placement: "top"
            },
            {
                title: "You're Ready to Go!",
                content: "You now have a basic understanding of Synapse Chamber. Explore each section to discover more features and capabilities. Happy training!",
                placement: "center"
            }
        ];
    }
}

// Initialize with default options
const synapseOnboarding = new OnboardingWizard();

// Make available globally
window.synapseOnboarding = synapseOnboarding;

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OnboardingWizard;
}