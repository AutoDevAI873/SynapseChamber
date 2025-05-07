/**
 * Synapse Chamber - Contextual Tooltips
 * Provides rich, context-aware tooltips for UI elements
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseTooltips {
    constructor(options = {}) {
        this.options = Object.assign({
            selector: '[data-tooltip]',
            containerClass: 'synapse-tooltip-container',
            tooltipClass: 'synapse-tooltip',
            arrowClass: 'synapse-tooltip-arrow',
            animationDuration: 200,
            showDelay: 300,
            hideDelay: 200,
            offset: 10,
            followMouse: false,
            maxWidth: 250,
            zIndex: 9000,
            allowHTML: false
        }, options);
        
        this.activeTooltips = [];
        this.tooltipContainer = null;
        this.hoverTimeoutId = null;
        this.leaveTimeoutId = null;
    }
    
    /**
     * Initialize tooltips
     */
    init() {
        this.createStyles();
        this.createTooltipContainer();
        this.bindEvents();
        
        console.log('Synapse Tooltips initialized');
    }
    
    /**
     * Create CSS styles for tooltips
     */
    createStyles() {
        if (document.getElementById('synapse-tooltip-styles')) {
            return;
        }
        
        const styleEl = document.createElement('style');
        styleEl.id = 'synapse-tooltip-styles';
        styleEl.textContent = `
            .${this.options.containerClass} {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 0;
                pointer-events: none;
                z-index: ${this.options.zIndex};
            }
            
            .${this.options.tooltipClass} {
                position: absolute;
                background-color: var(--bs-dark);
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 0.875rem;
                max-width: ${this.options.maxWidth}px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                pointer-events: none;
                transition: opacity ${this.options.animationDuration}ms ease, 
                            transform ${this.options.animationDuration}ms ease;
                opacity: 0;
                transform: translateY(5px);
                z-index: ${this.options.zIndex};
            }
            
            .${this.options.tooltipClass}--visible {
                opacity: 1;
                transform: translateY(0);
            }
            
            .${this.options.tooltipClass}--info {
                border-left: 3px solid var(--bs-info);
            }
            
            .${this.options.tooltipClass}--warning {
                border-left: 3px solid var(--bs-warning);
            }
            
            .${this.options.tooltipClass}--error {
                border-left: 3px solid var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--success {
                border-left: 3px solid var(--bs-success);
            }
            
            .${this.options.tooltipClass}--critical {
                border-left: 3px solid var(--bs-danger);
                background-color: rgba(var(--bs-danger-rgb), 0.9);
                font-weight: bold;
            }
            
            .${this.options.arrowClass} {
                position: absolute;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 6px;
            }
            
            .${this.options.arrowClass}--top {
                bottom: 100%;
                border-color: transparent transparent var(--bs-dark) transparent;
            }
            
            .${this.options.arrowClass}--bottom {
                top: 100%;
                border-color: var(--bs-dark) transparent transparent transparent;
            }
            
            .${this.options.arrowClass}--left {
                right: 100%;
                border-color: transparent var(--bs-dark) transparent transparent;
            }
            
            .${this.options.arrowClass}--right {
                left: 100%;
                border-color: transparent transparent transparent var(--bs-dark);
            }
            
            .${this.options.tooltipClass}--info .${this.options.arrowClass}--top {
                border-bottom-color: var(--bs-info);
            }
            
            .${this.options.tooltipClass}--warning .${this.options.arrowClass}--top {
                border-bottom-color: var(--bs-warning);
            }
            
            .${this.options.tooltipClass}--error .${this.options.arrowClass}--top {
                border-bottom-color: var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--success .${this.options.arrowClass}--top {
                border-bottom-color: var(--bs-success);
            }
            
            .${this.options.tooltipClass}--critical .${this.options.arrowClass}--top {
                border-bottom-color: var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--info .${this.options.arrowClass}--bottom {
                border-top-color: var(--bs-info);
            }
            
            .${this.options.tooltipClass}--warning .${this.options.arrowClass}--bottom {
                border-top-color: var(--bs-warning);
            }
            
            .${this.options.tooltipClass}--error .${this.options.arrowClass}--bottom {
                border-top-color: var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--success .${this.options.arrowClass}--bottom {
                border-top-color: var(--bs-success);
            }
            
            .${this.options.tooltipClass}--critical .${this.options.arrowClass}--bottom {
                border-top-color: var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--has-title .tooltip-title {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 5px;
            }
        `;
        
        document.head.appendChild(styleEl);
    }
    
    /**
     * Create tooltip container
     */
    createTooltipContainer() {
        this.tooltipContainer = document.createElement('div');
        this.tooltipContainer.className = this.options.containerClass;
        document.body.appendChild(this.tooltipContainer);
    }
    
    /**
     * Bind events
     */
    bindEvents() {
        // Define the element event handlers
        const handleMouseEnter = (e) => {
            clearTimeout(this.leaveTimeoutId);
            
            const target = e.currentTarget;
            
            this.hoverTimeoutId = setTimeout(() => {
                this.showTooltip(target, e);
            }, this.options.showDelay);
        };
        
        const handleMouseLeave = () => {
            clearTimeout(this.hoverTimeoutId);
            
            this.leaveTimeoutId = setTimeout(() => {
                this.hideAllTooltips();
            }, this.options.hideDelay);
        };
        
        const handleMouseMove = (e) => {
            if (this.options.followMouse && this.activeTooltips.length > 0) {
                // Get the last created tooltip
                const activeTooltip = this.activeTooltips[this.activeTooltips.length - 1];
                
                if (activeTooltip && activeTooltip.target === e.currentTarget) {
                    this.positionTooltipForMouse(activeTooltip.element, e);
                }
            }
        };
        
        // Add event listeners to all matching elements
        const tooltipElements = document.querySelectorAll(this.options.selector);
        tooltipElements.forEach(el => {
            el.addEventListener('mouseenter', handleMouseEnter);
            el.addEventListener('mouseleave', handleMouseLeave);
            if (this.options.followMouse) {
                el.addEventListener('mousemove', handleMouseMove);
            }
            
            // For mobile/touch devices
            el.addEventListener('touchstart', handleMouseEnter, { passive: true });
            document.addEventListener('touchend', handleMouseLeave, { passive: true });
        });
        
        // Handle dynamic elements with a global delegated event
        document.addEventListener('mouseover', (e) => {
            // Check if the target or any parent matches the selector
            const matchingElement = e.target.closest(this.options.selector);
            
            if (matchingElement && !matchingElement._tooltipInitialized) {
                matchingElement._tooltipInitialized = true;
                matchingElement.addEventListener('mouseenter', handleMouseEnter);
                matchingElement.addEventListener('mouseleave', handleMouseLeave);
                if (this.options.followMouse) {
                    matchingElement.addEventListener('mousemove', handleMouseMove);
                }
                
                // For mobile/touch devices
                matchingElement.addEventListener('touchstart', handleMouseEnter, { passive: true });
            }
        });
        
        // Handle tooltip container mouseover/mouseout to prevent flicker
        this.tooltipContainer.addEventListener('mouseenter', () => {
            clearTimeout(this.leaveTimeoutId);
        });
        
        this.tooltipContainer.addEventListener('mouseleave', () => {
            this.leaveTimeoutId = setTimeout(() => {
                this.hideAllTooltips();
            }, this.options.hideDelay);
        });
        
        // Handle scroll and resize events
        window.addEventListener('scroll', () => {
            this.updateTooltipPositions();
        }, { passive: true });
        
        window.addEventListener('resize', () => {
            this.updateTooltipPositions();
        });
    }
    
    /**
     * Show tooltip for an element
     */
    showTooltip(target, event) {
        // Get tooltip content
        const content = target.getAttribute('data-tooltip');
        if (!content) return;
        
        // Check if there's already a tooltip for this target
        const existingTooltip = this.activeTooltips.find(tooltip => tooltip.target === target);
        if (existingTooltip) return;
        
        // Create tooltip element
        const tooltipEl = document.createElement('div');
        tooltipEl.className = this.options.tooltipClass;
        
        // Get tooltip type if specified
        const tooltipType = target.getAttribute('data-tooltip-type');
        if (tooltipType) {
            tooltipEl.classList.add(`${this.options.tooltipClass}--${tooltipType}`);
        }
        
        // Get tooltip title if specified
        const tooltipTitle = target.getAttribute('data-tooltip-title');
        if (tooltipTitle) {
            tooltipEl.classList.add(`${this.options.tooltipClass}--has-title`);
            tooltipEl.innerHTML = `<span class="tooltip-title">${tooltipTitle}</span>`;
        }
        
        // Add content
        if (this.options.allowHTML || target.hasAttribute('data-tooltip-html')) {
            tooltipEl.innerHTML += content;
        } else {
            tooltipEl.innerHTML += content;
        }
        
        // Create arrow element
        const arrowEl = document.createElement('div');
        arrowEl.className = this.options.arrowClass;
        tooltipEl.appendChild(arrowEl);
        
        // Append to container
        this.tooltipContainer.appendChild(tooltipEl);
        
        // Position the tooltip
        const position = target.getAttribute('data-tooltip-position') || 'top';
        
        if (this.options.followMouse) {
            this.positionTooltipForMouse(tooltipEl, event);
        } else {
            this.positionTooltip(tooltipEl, target, position, arrowEl);
        }
        
        // Store reference to active tooltip
        this.activeTooltips.push({
            target: target,
            element: tooltipEl,
            position: position
        });
        
        // Show the tooltip
        setTimeout(() => {
            tooltipEl.classList.add(`${this.options.tooltipClass}--visible`);
        }, 10);
    }
    
    /**
     * Hide all tooltips
     */
    hideAllTooltips() {
        this.activeTooltips.forEach(tooltip => {
            tooltip.element.classList.remove(`${this.options.tooltipClass}--visible`);
            
            setTimeout(() => {
                if (tooltip.element.parentNode) {
                    tooltip.element.parentNode.removeChild(tooltip.element);
                }
            }, this.options.animationDuration);
        });
        
        this.activeTooltips = [];
    }
    
    /**
     * Position tooltip relative to target element
     */
    positionTooltip(tooltipEl, targetEl, position, arrowEl) {
        const targetRect = targetEl.getBoundingClientRect();
        const tooltipRect = tooltipEl.getBoundingClientRect();
        
        // Reset any previous positioning
        tooltipEl.style.top = '';
        tooltipEl.style.left = '';
        tooltipEl.style.right = '';
        tooltipEl.style.bottom = '';
        tooltipEl.style.transform = '';
        
        // Clear existing arrow classes
        arrowEl.className = this.options.arrowClass;
        
        // Position based on specified position
        switch (position) {
            case 'top':
                tooltipEl.style.left = `${window.scrollX + targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)}px`;
                tooltipEl.style.top = `${window.scrollY + targetRect.top - tooltipRect.height - this.options.offset}px`;
                arrowEl.classList.add(`${this.options.arrowClass}--bottom`);
                arrowEl.style.left = '50%';
                arrowEl.style.marginLeft = '-6px';
                arrowEl.style.top = '100%';
                break;
                
            case 'bottom':
                tooltipEl.style.left = `${window.scrollX + targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)}px`;
                tooltipEl.style.top = `${window.scrollY + targetRect.bottom + this.options.offset}px`;
                arrowEl.classList.add(`${this.options.arrowClass}--top`);
                arrowEl.style.left = '50%';
                arrowEl.style.marginLeft = '-6px';
                arrowEl.style.bottom = '100%';
                break;
                
            case 'left':
                tooltipEl.style.left = `${window.scrollX + targetRect.left - tooltipRect.width - this.options.offset}px`;
                tooltipEl.style.top = `${window.scrollY + targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2)}px`;
                arrowEl.classList.add(`${this.options.arrowClass}--right`);
                arrowEl.style.top = '50%';
                arrowEl.style.marginTop = '-6px';
                arrowEl.style.left = '100%';
                break;
                
            case 'right':
                tooltipEl.style.left = `${window.scrollX + targetRect.right + this.options.offset}px`;
                tooltipEl.style.top = `${window.scrollY + targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2)}px`;
                arrowEl.classList.add(`${this.options.arrowClass}--left`);
                arrowEl.style.top = '50%';
                arrowEl.style.marginTop = '-6px';
                arrowEl.style.right = '100%';
                break;
        }
        
        // Adjust if the tooltip is outside viewport
        this.adjustTooltipPosition(tooltipEl, position, arrowEl);
    }
    
    /**
     * Position tooltip following mouse cursor
     */
    positionTooltipForMouse(tooltipEl, event) {
        const tooltipRect = tooltipEl.getBoundingClientRect();
        
        // Position the tooltip near the cursor
        tooltipEl.style.left = `${window.scrollX + event.clientX - (tooltipRect.width / 2)}px`;
        tooltipEl.style.top = `${window.scrollY + event.clientY - tooltipRect.height - 20}px`;
        
        // Hide the arrow for mouse-following tooltips
        const arrowEl = tooltipEl.querySelector(`.${this.options.arrowClass}`);
        if (arrowEl) {
            arrowEl.style.display = 'none';
        }
        
        // Adjust if the tooltip is outside viewport
        this.adjustTooltipPosition(tooltipEl, 'mouse');
    }
    
    /**
     * Adjust tooltip position to keep it within viewport
     */
    adjustTooltipPosition(tooltipEl, position, arrowEl) {
        const tooltipRect = tooltipEl.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Horizontal adjustment
        if (tooltipRect.left < 0) {
            tooltipEl.style.left = `${window.scrollX + this.options.offset}px`;
            
            if (position === 'top' || position === 'bottom') {
                // Move arrow to match the original center of the target
                if (arrowEl) {
                    arrowEl.style.left = `${Math.max(6, tooltipRect.width / 2 + tooltipRect.left - this.options.offset)}px`;
                    arrowEl.style.marginLeft = '0';
                }
            }
        } else if (tooltipRect.right > viewportWidth) {
            tooltipEl.style.left = `${window.scrollX + viewportWidth - tooltipRect.width - this.options.offset}px`;
            
            if (position === 'top' || position === 'bottom') {
                // Move arrow to match the original center of the target
                if (arrowEl) {
                    arrowEl.style.left = `${Math.min(tooltipRect.width - 6, tooltipRect.width / 2 - (viewportWidth - tooltipRect.right) + this.options.offset)}px`;
                    arrowEl.style.marginLeft = '0';
                }
            }
        }
        
        // Vertical adjustment
        if (tooltipRect.top < 0) {
            if (position === 'top') {
                // Flip to bottom if needed
                const targetForTop = this.activeTooltips.find(t => t.element === tooltipEl)?.target;
                if (targetForTop) {
                    const targetRect = targetForTop.getBoundingClientRect();
                    tooltipEl.style.top = `${window.scrollY + targetRect.bottom + this.options.offset}px`;
                    
                    if (arrowEl) {
                        arrowEl.className = `${this.options.arrowClass} ${this.options.arrowClass}--top`;
                        arrowEl.style.top = 'auto';
                        arrowEl.style.bottom = '100%';
                    }
                } else {
                    tooltipEl.style.top = `${window.scrollY + this.options.offset}px`;
                }
            } else {
                tooltipEl.style.top = `${window.scrollY + this.options.offset}px`;
            }
        } else if (tooltipRect.bottom > viewportHeight) {
            if (position === 'bottom') {
                // Flip to top if needed
                const targetForBottom = this.activeTooltips.find(t => t.element === tooltipEl)?.target;
                if (targetForBottom) {
                    const targetRect = targetForBottom.getBoundingClientRect();
                    tooltipEl.style.top = `${window.scrollY + targetRect.top - tooltipRect.height - this.options.offset}px`;
                    
                    if (arrowEl) {
                        arrowEl.className = `${this.options.arrowClass} ${this.options.arrowClass}--bottom`;
                        arrowEl.style.bottom = 'auto';
                        arrowEl.style.top = '100%';
                    }
                } else {
                    tooltipEl.style.top = `${window.scrollY + viewportHeight - tooltipRect.height - this.options.offset}px`;
                }
            } else {
                tooltipEl.style.top = `${window.scrollY + viewportHeight - tooltipRect.height - this.options.offset}px`;
            }
        }
    }
    
    /**
     * Update positions of all active tooltips
     */
    updateTooltipPositions() {
        this.activeTooltips.forEach(tooltip => {
            const arrowEl = tooltip.element.querySelector(`.${this.options.arrowClass}`);
            this.positionTooltip(tooltip.element, tooltip.target, tooltip.position, arrowEl);
        });
    }
    
    /**
     * Show a tooltip programmatically
     */
    showTooltipFor(selector, content, options = {}) {
        const targetEl = document.querySelector(selector);
        if (!targetEl) return;
        
        // Set content attribute
        targetEl.setAttribute('data-tooltip', content);
        
        // Set optional attributes
        if (options.title) {
            targetEl.setAttribute('data-tooltip-title', options.title);
        }
        
        if (options.type) {
            targetEl.setAttribute('data-tooltip-type', options.type);
        }
        
        if (options.position) {
            targetEl.setAttribute('data-tooltip-position', options.position);
        }
        
        if (options.html) {
            targetEl.setAttribute('data-tooltip-html', 'true');
        }
        
        // Show the tooltip
        this.showTooltip(targetEl);
        
        // Return a function to hide this specific tooltip
        return () => {
            const index = this.activeTooltips.findIndex(t => t.target === targetEl);
            if (index !== -1) {
                const tooltip = this.activeTooltips[index];
                tooltip.element.classList.remove(`${this.options.tooltipClass}--visible`);
                
                setTimeout(() => {
                    if (tooltip.element.parentNode) {
                        tooltip.element.parentNode.removeChild(tooltip.element);
                    }
                    this.activeTooltips.splice(index, 1);
                }, this.options.animationDuration);
            }
        };
    }
}

// Initialize the tooltips if script is loaded after DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(() => {
        window.synapseTooltips = new SynapseTooltips();
        window.synapseTooltips.init();
    }, 0);
} else {
    document.addEventListener('DOMContentLoaded', () => {
        window.synapseTooltips = new SynapseTooltips();
        window.synapseTooltips.init();
    });
}