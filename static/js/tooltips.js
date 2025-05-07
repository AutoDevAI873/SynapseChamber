/**
 * Synapse Chamber - Contextual Tooltips
 * Provides dynamic, context-aware tooltips for improved user experience
 * Part of the Synapse Chamber UX enhancement project
 */

class SynapseTooltips {
    constructor(options = {}) {
        this.options = Object.assign({
            tooltipClass: 'synapse-tooltip',
            containerClass: 'synapse-tooltip-container',
            arrowClass: 'synapse-tooltip-arrow',
            titleClass: 'synapse-tooltip-title',
            contentClass: 'synapse-tooltip-content',
            activeClass: 'synapse-tooltip--active',
            zIndex: 9000,
            showDelay: 300,
            hideDelay: 200,
            offset: 10,
            duration: 200,
            enableAnimations: true,
            autoPosition: true,
            dataAttrSelector: '[data-tooltip]',
            titleSelector: '[data-tooltip-title]',
            contentSelector: '[data-tooltip-content]',
            positionSelector: '[data-tooltip-position]',
            typeSelector: '[data-tooltip-type]',
            defaultPosition: 'top',
            defaultType: 'default',
            allowHtml: false
        }, options);

        this.activeTooltips = [];
        this.tooltipIdCounter = 0;
        this.tooltipContainer = null;
        this.tooltipHideTimeouts = new Map();
        this.tooltipShowTimeouts = new Map();
    }

    /**
     * Initialize tooltips
     */
    init() {
        this.addStyles();
        this.createTooltipContainer();
        this.bindEvents();

        // Make tooltips accessible globally
        window.SynapseTooltips = this;

        console.log('Synapse Tooltips initialized');
    }

    /**
     * Add CSS styles for tooltips
     */
    addStyles() {
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
                max-width: 250px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                pointer-events: none;
                transition: opacity ${this.options.duration}ms ease, transform ${this.options.duration}ms ease;
                opacity: 0;
                transform: translateY(5px);
                border-left: 3px solid transparent;
            }
            
            .${this.options.tooltipClass}.${this.options.activeClass} {
                opacity: 1;
                transform: translateY(0);
            }
            
            .${this.options.tooltipClass}--info {
                border-left-color: var(--bs-info);
            }
            
            .${this.options.tooltipClass}--warning {
                border-left-color: var(--bs-warning);
            }
            
            .${this.options.tooltipClass}--error {
                border-left-color: var(--bs-danger);
            }
            
            .${this.options.tooltipClass}--success {
                border-left-color: var(--bs-success);
            }
            
            .${this.options.tooltipClass}--default {
                border-left-color: var(--bs-primary);
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
            
            .${this.options.titleClass} {
                font-weight: bold;
                margin-bottom: 4px;
            }
            
            .${this.options.contentClass} {
                line-height: 1.4;
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
     * Bind event listeners
     */
    bindEvents() {
        // Bind event handlers for data-attribute tooltips
        document.addEventListener('mouseenter', (e) => {
            const tooltipElem = this.findTooltipElement(e.target);
            if (tooltipElem) {
                const content = tooltipElem.getAttribute('data-tooltip');
                if (content) {
                    this.showTooltipFromData(tooltipElem);
                }
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const tooltipElem = this.findTooltipElement(e.target);
            if (tooltipElem) {
                const tooltipId = tooltipElem._tooltipId;
                if (tooltipId) {
                    this.hideTooltip(tooltipId);
                }
            }
        }, true);

        // Recalculate positions on window resize
        window.addEventListener('resize', this.debounce(() => {
            this.activeTooltips.forEach(tooltip => {
                const targetElement = tooltip.targetElement;
                if (targetElement && document.body.contains(targetElement)) {
                    this.positionTooltip(tooltip.element, targetElement, tooltip.position);
                } else {
                    this.hideTooltip(tooltip.id);
                }
            });
        }, 100));

        // Handle scroll events
        window.addEventListener('scroll', this.debounce(() => {
            this.activeTooltips.forEach(tooltip => {
                const targetElement = tooltip.targetElement;
                if (targetElement && document.body.contains(targetElement)) {
                    this.positionTooltip(tooltip.element, targetElement, tooltip.position);
                } else {
                    this.hideTooltip(tooltip.id);
                }
            });
        }, 100), true);
    }

    /**
     * Find tooltip element
     */
    findTooltipElement(element) {
        if (element.matches(this.options.dataAttrSelector)) {
            return element;
        }
        
        let current = element;
        while (current && current !== document.body) {
            if (current.matches(this.options.dataAttrSelector)) {
                return current;
            }
            current = current.parentElement;
        }
        
        return null;
    }

    /**
     * Show tooltip from data attributes
     */
    showTooltipFromData(element) {
        const content = element.getAttribute('data-tooltip');
        const title = element.getAttribute('data-tooltip-title') || '';
        const position = element.getAttribute('data-tooltip-position') || this.options.defaultPosition;
        const type = element.getAttribute('data-tooltip-type') || this.options.defaultType;
        
        const tooltipId = this.showTooltip({
            content: content,
            title: title,
            position: position,
            type: type,
            targetElement: element
        });
        
        // Store the tooltip ID on the element
        element._tooltipId = tooltipId;
        
        return tooltipId;
    }

    /**
     * Show a tooltip
     */
    showTooltip(options) {
        const tooltipOptions = Object.assign({
            content: '',
            title: '',
            position: this.options.defaultPosition,
            type: this.options.defaultType,
            allowHtml: this.options.allowHtml,
            targetElement: null,
            autoHide: false,
            autoHideDelay: 3000
        }, options);
        
        const { content, title, position, type, targetElement, autoHide, autoHideDelay } = tooltipOptions;
        
        // Generate a unique ID for this tooltip
        const tooltipId = `tooltip-${++this.tooltipIdCounter}`;
        
        // Clear any existing hide timeout
        if (targetElement && targetElement._tooltipId) {
            const existingTooltipId = targetElement._tooltipId;
            if (this.tooltipHideTimeouts.has(existingTooltipId)) {
                clearTimeout(this.tooltipHideTimeouts.get(existingTooltipId));
                this.tooltipHideTimeouts.delete(existingTooltipId);
            }
            
            // Hide the existing tooltip
            this.hideTooltip(existingTooltipId, true);
        }
        
        // Schedule the tooltip to appear after the delay
        const showTimeout = setTimeout(() => {
            // Create the tooltip element
            const tooltipElement = document.createElement('div');
            tooltipElement.id = tooltipId;
            tooltipElement.className = `${this.options.tooltipClass} ${this.options.tooltipClass}--${type}`;
            
            // Create tooltip content
            const tooltipContent = document.createElement('div');
            tooltipContent.className = this.options.contentClass;
            
            if (tooltipOptions.allowHtml) {
                tooltipContent.innerHTML = content;
            } else {
                tooltipContent.textContent = content;
            }
            
            // Create tooltip title if provided
            if (title) {
                const tooltipTitle = document.createElement('div');
                tooltipTitle.className = this.options.titleClass;
                
                if (tooltipOptions.allowHtml) {
                    tooltipTitle.innerHTML = title;
                } else {
                    tooltipTitle.textContent = title;
                }
                
                tooltipElement.appendChild(tooltipTitle);
            }
            
            tooltipElement.appendChild(tooltipContent);
            
            // Create arrow element
            const arrowElement = document.createElement('div');
            arrowElement.className = this.options.arrowClass;
            tooltipElement.appendChild(arrowElement);
            
            // Add the tooltip to the container
            this.tooltipContainer.appendChild(tooltipElement);
            
            // Position the tooltip
            if (targetElement) {
                this.positionTooltip(tooltipElement, targetElement, position);
            } else {
                // Position in the center if no target
                tooltipElement.style.top = '50%';
                tooltipElement.style.left = '50%';
                tooltipElement.style.transform = 'translate(-50%, -50%)';
            }
            
            // Add to active tooltips
            this.activeTooltips.push({
                id: tooltipId,
                element: tooltipElement,
                targetElement: targetElement,
                position: position
            });
            
            // Make the tooltip visible
            setTimeout(() => {
                tooltipElement.classList.add(this.options.activeClass);
            }, 10);
            
            // Set up auto-hide if specified
            if (autoHide) {
                setTimeout(() => {
                    this.hideTooltip(tooltipId);
                }, autoHideDelay);
            }
            
            // Clear the show timeout reference
            this.tooltipShowTimeouts.delete(tooltipId);
        }, this.options.showDelay);
        
        // Store the timeout reference
        this.tooltipShowTimeouts.set(tooltipId, showTimeout);
        
        return tooltipId;
    }

    /**
     * Hide a tooltip
     */
    hideTooltip(tooltipId, immediate = false) {
        // Cancel any pending show operation
        if (this.tooltipShowTimeouts.has(tooltipId)) {
            clearTimeout(this.tooltipShowTimeouts.get(tooltipId));
            this.tooltipShowTimeouts.delete(tooltipId);
            return;
        }
        
        // Find the tooltip in the active tooltips
        const tooltipIndex = this.activeTooltips.findIndex(t => t.id === tooltipId);
        if (tooltipIndex === -1) return;
        
        const tooltip = this.activeTooltips[tooltipIndex].element;
        
        if (immediate) {
            // Remove immediately
            if (tooltip && tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
            this.activeTooltips.splice(tooltipIndex, 1);
        } else {
            // Schedule the tooltip to hide after the delay
            const hideTimeout = setTimeout(() => {
                // Fade out animation
                tooltip.classList.remove(this.options.activeClass);
                
                // Remove the element after the animation completes
                setTimeout(() => {
                    if (tooltip && tooltip.parentNode) {
                        tooltip.parentNode.removeChild(tooltip);
                    }
                    this.activeTooltips.splice(tooltipIndex, 1);
                }, this.options.duration);
                
                // Remove the timeout reference
                this.tooltipHideTimeouts.delete(tooltipId);
            }, this.options.hideDelay);
            
            // Store the timeout reference
            this.tooltipHideTimeouts.set(tooltipId, hideTimeout);
        }
    }

    /**
     * Position a tooltip relative to a target element
     */
    positionTooltip(tooltip, target, preferredPosition) {
        const targetRect = target.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        
        // Default position
        let position = preferredPosition || this.options.defaultPosition;
        const arrow = tooltip.querySelector(`.${this.options.arrowClass}`);
        
        // Reset arrow class
        if (arrow) {
            arrow.className = this.options.arrowClass;
        }
        
        // If auto-positioning is enabled, choose the best position
        if (this.options.autoPosition && position === 'auto') {
            // Calculate available space in each direction
            const spaceTop = targetRect.top;
            const spaceBottom = windowHeight - targetRect.bottom;
            const spaceLeft = targetRect.left;
            const spaceRight = windowWidth - targetRect.right;
            
            // Find the position with the most space
            const spaces = [
                { position: 'top', space: spaceTop },
                { position: 'bottom', space: spaceBottom },
                { position: 'left', space: spaceLeft },
                { position: 'right', space: spaceRight }
            ];
            
            // Sort by available space
            spaces.sort((a, b) => b.space - a.space);
            
            // Choose the position with the most space
            position = spaces[0].position;
        }
        
        // Calculate tooltip position
        let top, left;
        
        switch (position) {
            case 'top':
                top = targetRect.top - tooltipRect.height - this.options.offset;
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                
                // Add arrow
                if (arrow) {
                    arrow.classList.add(`${this.options.arrowClass}--bottom`);
                    arrow.style.left = '50%';
                    arrow.style.marginLeft = '-6px';
                    arrow.style.bottom = '-6px';
                }
                break;
                
            case 'bottom':
                top = targetRect.bottom + this.options.offset;
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                
                // Add arrow
                if (arrow) {
                    arrow.classList.add(`${this.options.arrowClass}--top`);
                    arrow.style.left = '50%';
                    arrow.style.marginLeft = '-6px';
                    arrow.style.top = '-6px';
                }
                break;
                
            case 'left':
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                left = targetRect.left - tooltipRect.width - this.options.offset;
                
                // Add arrow
                if (arrow) {
                    arrow.classList.add(`${this.options.arrowClass}--right`);
                    arrow.style.top = '50%';
                    arrow.style.marginTop = '-6px';
                    arrow.style.right = '-6px';
                }
                break;
                
            case 'right':
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                left = targetRect.right + this.options.offset;
                
                // Add arrow
                if (arrow) {
                    arrow.classList.add(`${this.options.arrowClass}--left`);
                    arrow.style.top = '50%';
                    arrow.style.marginTop = '-6px';
                    arrow.style.left = '-6px';
                }
                break;
        }
        
        // Make sure the tooltip is within the viewport
        if (left < 10) left = 10;
        if (left + tooltipRect.width > windowWidth - 10) left = windowWidth - tooltipRect.width - 10;
        if (top < 10) top = 10;
        if (top + tooltipRect.height > windowHeight - 10) top = windowHeight - tooltipRect.height - 10;
        
        // Set the tooltip position
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    /**
     * Utility function for debouncing
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Show a floating tooltip at a specific position
     */
    showFloatingTooltip(options) {
        const { content, title, type, x, y, autoHide, autoHideDelay } = Object.assign({
            content: '',
            title: '',
            type: this.options.defaultType,
            x: 0,
            y: 0,
            autoHide: true,
            autoHideDelay: 3000
        }, options);
        
        const tooltipId = this.showTooltip({
            content,
            title,
            type,
            autoHide,
            autoHideDelay
        });
        
        const tooltip = document.getElementById(tooltipId);
        if (tooltip) {
            tooltip.style.top = `${y}px`;
            tooltip.style.left = `${x}px`;
        }
        
        return tooltipId;
    }

    /**
     * Hide all tooltips
     */
    hideAllTooltips() {
        // Clone the array since we'll be modifying it
        const tooltips = [...this.activeTooltips];
        tooltips.forEach(tooltip => {
            this.hideTooltip(tooltip.id, true);
        });
    }
}

// Initialize tooltips if script is loaded after DOM is ready
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