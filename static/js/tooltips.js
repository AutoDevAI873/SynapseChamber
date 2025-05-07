/**
 * Synapse Chamber - Contextual Tooltips System
 * Provides intelligent context-aware tooltips throughout the UI
 * Part of the Synapse Chamber UI/UX enhancement project
 */

class SynapseTooltips {
    constructor() {
        // Configuration for various tooltip categories
        this.tooltipConfig = {
            // AI Platform specific tooltips
            platforms: {
                "gpt": {
                    title: "ChatGPT",
                    description: "OpenAI's large language model optimized for chat conversations.",
                    footer: "Good for: Creative writing, sophisticated reasoning",
                    shortcut: "Alt+G"
                },
                "claude": {
                    title: "Claude",
                    description: "Anthropic's AI assistant known for longer context and nuanced responses.",
                    footer: "Good for: Detailed analysis, understanding complex text",
                    shortcut: "Alt+C"
                },
                "gemini": {
                    title: "Gemini",
                    description: "Google's multimodal AI model that can process text and images.",
                    footer: "Good for: Visual reasoning, analytical tasks",
                    shortcut: "Alt+M"
                },
                "grok": {
                    title: "Grok",
                    description: "X's conversational AI with real-time data access.",
                    footer: "Good for: Current events, conversational responses",
                    shortcut: "Alt+K"
                },
                "deepseek": {
                    title: "DeepSeek",
                    description: "Specialized AI with strong coding and technical capabilities.",
                    footer: "Good for: Programming tasks, technical documentation",
                    shortcut: "Alt+D"
                }
            },
            
            // Training module tooltips
            training: {
                "topic_selection": {
                    title: "Topic Selection",
                    description: "Choose a training area to focus on. Different topics expose the agent to diverse knowledge domains.",
                    footer: "Pro tip: Regularly rotate topics for well-rounded training"
                },
                "platform_selection": {
                    title: "Platform Selection",
                    description: "Choose which AI platforms to use for training. Each platform has different strengths and weaknesses.",
                    footer: "Best practice: Train across multiple platforms for diverse perspectives"
                },
                "prompt_input": {
                    title: "Training Prompt",
                    description: "The question or task you want the AIs to respond to. Make it clear, specific, and challenging.",
                    footer: "Effective prompts are precise and test specific capabilities"
                },
                "training_mode": {
                    title: "Training Mode",
                    description: "Controls how the system processes AI responses and updates agent knowledge.",
                    footer: "See documentation for details on each mode"
                },
                "history_view": {
                    title: "Training History",
                    description: "View past training sessions, responses, and analysis results.",
                    footer: "Analyze trends to identify knowledge gaps"
                }
            },
            
            // Memory system tooltips
            memory: {
                "conversation_browser": {
                    title: "Conversation Browser",
                    description: "Browse and search through stored conversations across all platforms.",
                    footer: "Use filters to find specific knowledge areas"
                },
                "memory_search": {
                    title: "Semantic Search",
                    description: "Search for memories using natural language. The system will find semantically similar content.",
                    footer: "Try describing concepts rather than just keywords"
                },
                "memory_item": {
                    title: "Memory Item",
                    description: "Individual knowledge unit stored in the system. Contains source, importance, and context metadata.",
                    footer: "Click to view associated memory connections"
                },
                "memory_graph": {
                    title: "Knowledge Graph",
                    description: "Visual representation of how memories and concepts are connected in the agent's knowledge base.",
                    footer: "Dense clusters indicate well-learned concepts"
                }
            },
            
            // Development environment tooltips
            development: {
                "file_explorer": {
                    title: "File Explorer",
                    description: "Browse and manage files in the agent's workspace.",
                    footer: "Right-click for additional actions"
                },
                "code_editor": {
                    title: "Code Editor",
                    description: "Edit code with syntax highlighting and intelligent assistance.",
                    footer: "Keyboard shortcut: Ctrl+S to save"
                },
                "terminal": {
                    title: "Terminal",
                    description: "Execute commands in a shell environment for development and testing.",
                    footer: "Type 'help' for available commands"
                },
                "command_palette": {
                    title: "Command Palette",
                    description: "Quick access to commands and actions throughout the interface.",
                    footer: "Keyboard shortcut: Ctrl+Shift+P"
                }
            },
            
            // System health indicators
            system: {
                "health_indicator": {
                    title: "System Health",
                    description: "Shows the overall health status of the Synapse Chamber components.",
                    footer: "Click for detailed diagnostics"
                },
                "memory_usage": {
                    title: "Memory Usage",
                    description: "Shows how much of the allocated memory is currently being used.",
                    footer: "Approaching capacity may require optimization"
                },
                "driver_status": {
                    title: "Browser Driver Status",
                    description: "Indicates whether the browser automation system is functioning properly.",
                    footer: "Green: Healthy, Yellow: Warning, Red: Error"
                },
                "api_status": {
                    title: "API Connection Status",
                    description: "Shows the health of connections to various external APIs and services.",
                    footer: "Click to view detailed connection logs"
                }
            }
        };
        
        // Initialize tooltips
        this.init();
    }
    
    /**
     * Initialize tooltip system
     */
    init() {
        // Initialize on document ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupTooltips());
        } else {
            this.setupTooltips();
        }
        
        // Set up mutation observer to handle dynamically added elements
        this.setupMutationObserver();
    }
    
    /**
     * Set up initial tooltips
     */
    setupTooltips() {
        // Find elements with data-tooltip attributes
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        // Process each tooltip element
        tooltipElements.forEach(element => {
            this.processTooltipElement(element);
        });
        
        // Add special context-sensitive tooltips
        this.addPlatformTooltips();
        this.addTrainingTooltips();
        this.addMemoryTooltips();
        this.addDevelopmentTooltips();
        this.addSystemTooltips();
    }
    
    /**
     * Process a single tooltip element
     */
    processTooltipElement(element) {
        const tooltipType = element.getAttribute('data-tooltip');
        const tooltipCategory = element.getAttribute('data-tooltip-category') || 'general';
        const tooltipId = element.getAttribute('data-tooltip-id');
        
        // Get tooltip content
        let tooltipContent = {
            title: element.getAttribute('data-tooltip-title') || '',
            description: element.getAttribute('data-tooltip-description') || '',
            footer: element.getAttribute('data-tooltip-footer') || '',
            shortcut: element.getAttribute('data-tooltip-shortcut') || ''
        };
        
        // If we have configuration for this tooltip, use it
        if (tooltipCategory && tooltipId && this.tooltipConfig[tooltipCategory] && this.tooltipConfig[tooltipCategory][tooltipId]) {
            tooltipContent = this.tooltipConfig[tooltipCategory][tooltipId];
        }
        
        // Create tooltip HTML
        const tooltipHTML = this.createTooltipHTML(tooltipContent);
        
        // Wrap element in tooltip wrapper if not already wrapped
        if (!element.parentElement.classList.contains('tooltip-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = `tooltip-wrapper tooltip-${tooltipType}`;
            element.parentNode.insertBefore(wrapper, element);
            wrapper.appendChild(element);
            
            // Add tooltip content to wrapper
            const tooltipContentElement = document.createElement('div');
            tooltipContentElement.className = 'tooltip-content';
            tooltipContentElement.innerHTML = tooltipHTML;
            wrapper.appendChild(tooltipContentElement);
            
            // Add tooltip trigger class to element
            element.classList.add('tooltip-trigger');
        }
    }
    
    /**
     * Create HTML for tooltip content
     */
    createTooltipHTML(content) {
        let html = '';
        
        if (content.title) {
            html += `<div class="tooltip-title">${content.title}</div>`;
        }
        
        if (content.description) {
            html += `<div class="tooltip-description">${content.description}</div>`;
        }
        
        if (content.footer) {
            html += `<div class="tooltip-footer">${content.footer}`;
            
            if (content.shortcut) {
                html += ` <span class="tooltip-shortcut">${content.shortcut}</span>`;
            }
            
            html += `</div>`;
        } else if (content.shortcut) {
            html += `<div class="tooltip-footer">Shortcut: <span class="tooltip-shortcut">${content.shortcut}</span></div>`;
        }
        
        return html;
    }
    
    /**
     * Set up a mutation observer to process dynamically added elements
     */
    setupMutationObserver() {
        // Create mutation observer
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // Check for added nodes with tooltip attributes
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        // Check if node is an element
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Process if it has a tooltip attribute
                            if (node.hasAttribute && node.hasAttribute('data-tooltip')) {
                                this.processTooltipElement(node);
                            }
                            
                            // Check children for tooltip attributes
                            const childTooltips = node.querySelectorAll('[data-tooltip]');
                            childTooltips.forEach(element => {
                                this.processTooltipElement(element);
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
    
    // Helper methods for specific tooltip categories
    
    /**
     * Add platform-specific tooltips
     */
    addPlatformTooltips() {
        // Find platform selection elements
        const platformElements = document.querySelectorAll('.platform-item, [data-platform]');
        
        platformElements.forEach(element => {
            const platformId = element.getAttribute('data-platform') || 
                              element.classList.contains('platform-item') ? 
                              element.querySelector('.platform-name')?.textContent.toLowerCase() : null;
            
            if (platformId && this.tooltipConfig.platforms[platformId]) {
                element.setAttribute('data-tooltip', 'top');
                element.setAttribute('data-tooltip-category', 'platforms');
                element.setAttribute('data-tooltip-id', platformId);
                this.processTooltipElement(element);
            }
        });
    }
    
    /**
     * Add training-related tooltips
     */
    addTrainingTooltips() {
        // Map of selectors to tooltip IDs
        const trainingSelectors = {
            '#topic-selector, .topic-selector': 'topic_selection',
            '#platform-selector, .platform-selector': 'platform_selection',
            '#prompt-input, .prompt-input': 'prompt_input',
            '#training-mode, .training-mode': 'training_mode',
            '#history-container, .training-history': 'history_view'
        };
        
        // Process each selector
        for (const [selector, tooltipId] of Object.entries(trainingSelectors)) {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach(element => {
                element.setAttribute('data-tooltip', 'top');
                element.setAttribute('data-tooltip-category', 'training');
                element.setAttribute('data-tooltip-id', tooltipId);
                this.processTooltipElement(element);
            });
        }
    }
    
    /**
     * Add memory system tooltips
     */
    addMemoryTooltips() {
        // Map of selectors to tooltip IDs
        const memorySelectors = {
            '#conversation-browser, .conversation-browser': 'conversation_browser',
            '#memory-search, .memory-search': 'memory_search',
            '.memory-item': 'memory_item',
            '#memory-graph, .memory-graph': 'memory_graph'
        };
        
        // Process each selector
        for (const [selector, tooltipId] of Object.entries(memorySelectors)) {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach(element => {
                element.setAttribute('data-tooltip', 'top');
                element.setAttribute('data-tooltip-category', 'memory');
                element.setAttribute('data-tooltip-id', tooltipId);
                this.processTooltipElement(element);
            });
        }
    }
    
    /**
     * Add development environment tooltips
     */
    addDevelopmentTooltips() {
        // Map of selectors to tooltip IDs
        const devSelectors = {
            '#file-explorer, .file-explorer': 'file_explorer',
            '#code-editor, .code-editor': 'code_editor',
            '#terminal, .terminal': 'terminal',
            '#command-palette, .command-palette': 'command_palette'
        };
        
        // Process each selector
        for (const [selector, tooltipId] of Object.entries(devSelectors)) {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach(element => {
                element.setAttribute('data-tooltip', 'top');
                element.setAttribute('data-tooltip-category', 'development');
                element.setAttribute('data-tooltip-id', tooltipId);
                this.processTooltipElement(element);
            });
        }
    }
    
    /**
     * Add system health tooltips
     */
    addSystemTooltips() {
        // Map of selectors to tooltip IDs
        const systemSelectors = {
            '#health-indicator, .health-indicator': 'health_indicator',
            '#memory-usage, .memory-usage': 'memory_usage',
            '#driver-status, .driver-status': 'driver_status',
            '#api-status, .api-status': 'api_status'
        };
        
        // Process each selector
        for (const [selector, tooltipId] of Object.entries(systemSelectors)) {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach(element => {
                element.setAttribute('data-tooltip', 'top');
                element.setAttribute('data-tooltip-category', 'system');
                element.setAttribute('data-tooltip-id', tooltipId);
                this.processTooltipElement(element);
            });
        }
    }
}

// Initialize tooltips system
const synapseTooltips = new SynapseTooltips();

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SynapseTooltips;
}