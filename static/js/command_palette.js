/**
 * Synapse Chamber Command Palette
 * 
 * A powerful, keyboard-driven command palette for quick navigation and actions
 * within the Synapse Chamber system. Inspired by IDE command palettes like in 
 * VSCode, JetBrains, and Sublime Text.
 */

class SynapseCommandPalette {
    constructor() {
        this.isOpen = false;
        this.commands = [];
        this.filteredCommands = [];
        this.selectedIndex = 0;
        this.searchTerm = '';
        this.recentCommands = [];
        this.maxRecentCommands = 5;
        this.commandHistory = [];
        this.maxHistory = 50;

        // Create DOM elements
        this.createDOMElements();
        
        // Initialize command palette
        this.initializeCommandPalette();
        
        // Load user preferences and history
        this.loadUserPreferences();
        this.loadCommandHistory();
        
        // Register global keyboard shortcut
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
    }
    
    /**
     * Create the DOM elements for the command palette
     */
    createDOMElements() {
        // Create command palette container
        this.container = document.createElement('div');
        this.container.id = 'synapseCommandPalette';
        this.container.className = 'command-palette-container';
        this.container.style.display = 'none';
        
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'command-palette-overlay';
        this.overlay.addEventListener('click', () => this.hide());
        
        // Create palette content
        this.paletteContent = document.createElement('div');
        this.paletteContent.className = 'command-palette-content';
        
        // Create search input
        this.searchContainer = document.createElement('div');
        this.searchContainer.className = 'command-palette-search';
        
        this.searchIcon = document.createElement('i');
        this.searchIcon.className = 'fas fa-search command-palette-search-icon';
        
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.className = 'command-palette-input';
        this.searchInput.placeholder = 'Type a command or search...';
        this.searchInput.addEventListener('input', () => this.handleSearch());
        this.searchInput.addEventListener('keydown', (e) => this.handleInputKeyDown(e));
        
        this.searchContainer.appendChild(this.searchIcon);
        this.searchContainer.appendChild(this.searchInput);
        
        // Create results container
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'command-palette-results';
        
        // Create footer
        this.footer = document.createElement('div');
        this.footer.className = 'command-palette-footer';
        
        this.footerHints = document.createElement('div');
        this.footerHints.className = 'command-palette-hints';
        this.footerHints.innerHTML = `
            <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
            <span><kbd>Enter</kbd> Execute</span>
            <span><kbd>Esc</kbd> Dismiss</span>
        `;
        
        this.footer.appendChild(this.footerHints);
        
        // Assemble palette
        this.paletteContent.appendChild(this.searchContainer);
        this.paletteContent.appendChild(this.resultsContainer);
        this.paletteContent.appendChild(this.footer);
        
        // Add to container
        this.container.appendChild(this.overlay);
        this.container.appendChild(this.paletteContent);
        
        // Add to document
        document.body.appendChild(this.container);
        
        // Add stylesheet
        this.addStyles();
    }
    
    /**
     * Add command palette styles to the document
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .command-palette-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: flex-start;
                justify-content: center;
            }
            
            .command-palette-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(3px);
            }
            
            .command-palette-content {
                position: relative;
                width: 600px;
                max-width: 90%;
                margin-top: 80px;
                background-color: #1e1e1e;
                border-radius: 8px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: commandPaletteSlideDown 0.2s ease-out;
            }
            
            @keyframes commandPaletteSlideDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .command-palette-search {
                display: flex;
                align-items: center;
                padding: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .command-palette-search-icon {
                color: #6c757d;
                margin-right: 10px;
            }
            
            .command-palette-input {
                flex: 1;
                background: none;
                border: none;
                color: #f8f9fa;
                font-size: 1rem;
                outline: none;
            }
            
            .command-palette-input::placeholder {
                color: #6c757d;
            }
            
            .command-palette-results {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .command-palette-category {
                font-size: 0.8rem;
                color: #6c757d;
                padding: 5px 15px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 10px;
            }
            
            .command-palette-item {
                display: flex;
                align-items: center;
                padding: 10px 15px;
                cursor: pointer;
                transition: background-color 0.1s;
            }
            
            .command-palette-item:hover, .command-palette-item.selected {
                background-color: rgba(13, 110, 253, 0.15);
            }
            
            .command-palette-item-icon {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #adb5bd;
            }
            
            .command-palette-item-text {
                flex: 1;
            }
            
            .command-palette-item-title {
                font-size: 0.95rem;
                color: #f8f9fa;
                margin: 0;
            }
            
            .command-palette-item-desc {
                font-size: 0.8rem;
                color: #adb5bd;
                margin: 0;
            }
            
            .command-palette-item-shortcut {
                display: flex;
                gap: 5px;
            }
            
            .command-palette-item-shortcut kbd {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                box-shadow: none;
                color: #adb5bd;
                font-size: 0.75rem;
                padding: 2px 5px;
            }
            
            .command-palette-footer {
                padding: 10px 15px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .command-palette-hints {
                display: flex;
                gap: 15px;
                color: #6c757d;
                font-size: 0.85rem;
            }
            
            .command-palette-hints kbd {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                box-shadow: none;
                color: #adb5bd;
                font-size: 0.7rem;
                padding: 2px 4px;
                margin: 0 2px;
            }
            
            .command-palette-match {
                color: #0d6efd;
                font-weight: bold;
            }
            
            .command-palette-badge {
                font-size: 0.7rem;
                padding: 2px 6px;
                border-radius: 10px;
                margin-left: 8px;
                background-color: rgba(25, 135, 84, 0.2);
                color: #20c997;
            }
            
            .command-palette-badge.warning {
                background-color: rgba(255, 193, 7, 0.2);
                color: #ffc107;
            }
            
            .command-palette-badge.danger {
                background-color: rgba(220, 53, 69, 0.2);
                color: #dc3545;
            }
            
            .command-palette-no-results {
                padding: 30px 15px;
                text-align: center;
                color: #6c757d;
            }
            
            /* Scrollbar Styles */
            .command-palette-results::-webkit-scrollbar {
                width: 6px;
            }
            
            .command-palette-results::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
            }
            
            .command-palette-results::-webkit-scrollbar-thumb {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 3px;
            }
            
            .command-palette-results::-webkit-scrollbar-thumb:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Initialize the command palette with available commands
     */
    initializeCommandPalette() {
        // Navigation commands
        this.registerCommands([
            {
                id: 'home',
                title: 'Go to Home',
                description: 'Navigate to the home page',
                category: 'Navigation',
                icon: 'fas fa-home',
                shortcut: ['g', 'h'],
                action: () => window.location.href = '/'
            },
            {
                id: 'terminal',
                title: 'Open Terminal',
                description: 'Navigate to the terminal interface',
                category: 'Navigation',
                icon: 'fas fa-terminal',
                shortcut: ['g', 't'],
                action: () => window.location.href = '/terminal'
            },
            {
                id: 'memory',
                title: 'Open Memory Explorer',
                description: 'Navigate to the memory explorer',
                category: 'Navigation',
                icon: 'fas fa-brain',
                shortcut: ['g', 'm'],
                action: () => window.location.href = '/memory'
            },
            {
                id: 'platforms',
                title: 'Manage AI Platforms',
                description: 'Navigate to AI platforms configuration',
                category: 'Navigation',
                icon: 'fas fa-robot',
                shortcut: ['g', 'p'],
                action: () => window.location.href = '/platforms'
            },
            {
                id: 'settings',
                title: 'Open Settings',
                description: 'Navigate to system settings',
                category: 'Navigation',
                icon: 'fas fa-cog',
                shortcut: ['g', 's'],
                action: () => window.location.href = '/settings'
            }
        ]);
        
        // Training commands
        this.registerCommands([
            {
                id: 'start-training',
                title: 'Start New Training Session',
                description: 'Begin a new AI training session',
                category: 'Training',
                icon: 'fas fa-play',
                badge: 'New',
                action: () => this.startNewTraining()
            },
            {
                id: 'training-status',
                title: 'View Training Status',
                description: 'Check the status of current training sessions',
                category: 'Training',
                icon: 'fas fa-tasks',
                action: () => window.location.href = '/training/status'
            },
            {
                id: 'training-insights',
                title: 'Training Insights',
                description: 'View analytics and insights from training sessions',
                category: 'Training',
                icon: 'fas fa-chart-line',
                action: () => window.location.href = '/training/insights'
            }
        ]);
        
        // Memory system commands
        this.registerCommands([
            {
                id: 'search-memory',
                title: 'Search Memory',
                description: 'Search across all stored memories',
                category: 'Memory',
                icon: 'fas fa-search',
                action: () => this.openSearchMemory()
            },
            {
                id: 'create-memory',
                title: 'Create New Memory',
                description: 'Add a new memory to the system',
                category: 'Memory',
                icon: 'fas fa-plus',
                action: () => window.location.href = '/memory/create'
            },
            {
                id: 'analyze-memory',
                title: 'Analyze Memory Patterns',
                description: 'Run pattern analysis on memory system',
                category: 'Memory',
                icon: 'fas fa-sitemap',
                badge: 'AI',
                action: () => window.location.href = '/memory/analyze'
            }
        ]);
        
        // AI commands
        this.registerCommands([
            {
                id: 'chat-with-agent',
                title: 'Chat with Agent',
                description: 'Start a conversation with the AI agent',
                category: 'AI',
                icon: 'fas fa-comment-alt',
                action: () => window.location.href = '/chat'
            },
            {
                id: 'api-console',
                title: 'Open API Console',
                description: 'Test AI integrations and APIs',
                category: 'AI',
                icon: 'fas fa-terminal',
                action: () => window.location.href = '/api/console'
            },
            {
                id: 'ai-settings',
                title: 'AI Settings',
                description: 'Configure AI behavior and preferences',
                category: 'AI',
                icon: 'fas fa-sliders-h',
                action: () => window.location.href = '/ai/settings'
            }
        ]);
        
        // System commands
        this.registerCommands([
            {
                id: 'theme-toggle',
                title: 'Toggle Dark/Light Theme',
                description: 'Switch between dark and light themes',
                category: 'System',
                icon: 'fas fa-moon',
                action: () => this.toggleTheme()
            },
            {
                id: 'clear-cache',
                title: 'Clear System Cache',
                description: 'Clear cached data and refresh the system',
                category: 'System',
                icon: 'fas fa-trash',
                badge: { text: 'Caution', type: 'warning' },
                action: () => this.clearCache()
            },
            {
                id: 'system-diagnostics',
                title: 'Run System Diagnostics',
                description: 'Check system health and performance',
                category: 'System',
                icon: 'fas fa-heartbeat',
                action: () => window.location.href = '/diagnostics'
            },
            {
                id: 'show-logs',
                title: 'View System Logs',
                description: 'View logs for debugging and monitoring',
                category: 'System',
                icon: 'fas fa-file-alt',
                action: () => window.location.href = '/logs'
            },
            {
                id: 'reload-app',
                title: 'Reload Application',
                description: 'Refresh the application state',
                category: 'System',
                icon: 'fas fa-sync',
                action: () => window.location.reload()
            }
        ]);
        
        // User commands
        this.registerCommands([
            {
                id: 'user-profile',
                title: 'Edit User Profile',
                description: 'View and edit your user profile',
                category: 'User',
                icon: 'fas fa-user',
                action: () => window.location.href = '/profile'
            },
            {
                id: 'user-preferences',
                title: 'User Preferences',
                description: 'Customize your user experience',
                category: 'User',
                icon: 'fas fa-user-cog',
                action: () => window.location.href = '/preferences'
            }
        ]);
        
        // Development tools
        this.registerCommands([
            {
                id: 'code-editor',
                title: 'Open Code Editor',
                description: 'Launch the code editor interface',
                category: 'Development',
                icon: 'fas fa-code',
                badge: 'New',
                action: () => window.location.href = '/editor'
            },
            {
                id: 'documentation',
                title: 'View Documentation',
                description: 'Open the system documentation',
                category: 'Development',
                icon: 'fas fa-book',
                action: () => window.location.href = '/docs'
            },
            {
                id: 'preview-mode',
                title: 'Toggle Preview Mode',
                description: 'Enable or disable preview mode',
                category: 'Development',
                icon: 'fas fa-eye',
                action: () => this.togglePreviewMode()
            }
        ]);
        
        // Meta commands
        this.registerCommands([
            {
                id: 'help',
                title: 'Help & Documentation',
                description: 'View help resources and documentation',
                category: 'Help',
                icon: 'fas fa-question-circle',
                action: () => window.location.href = '/help'
            },
            {
                id: 'keyboard-shortcuts',
                title: 'Keyboard Shortcuts',
                description: 'View all available keyboard shortcuts',
                category: 'Help',
                icon: 'fas fa-keyboard',
                action: () => window.location.href = '/shortcuts'
            },
            {
                id: 'contact-support',
                title: 'Contact Support',
                description: 'Get help from the support team',
                category: 'Help',
                icon: 'fas fa-life-ring',
                action: () => window.location.href = '/support'
            }
        ]);
    }
    
    /**
     * Register a new command or array of commands
     * @param {Object|Array} commands - Command object or array of command objects
     */
    registerCommands(commands) {
        if (Array.isArray(commands)) {
            this.commands = [...this.commands, ...commands];
        } else {
            this.commands.push(commands);
        }
    }
    
    /**
     * Toggle the command palette visibility
     */
    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    /**
     * Show the command palette
     */
    show() {
        if (this.isOpen) return;
        
        this.container.style.display = 'flex';
        this.isOpen = true;
        
        // Reset state
        this.searchTerm = '';
        this.searchInput.value = '';
        this.selectedIndex = 0;
        
        // Focus the search input
        setTimeout(() => {
            this.searchInput.focus();
            this.handleSearch();
        }, 50);
    }
    
    /**
     * Hide the command palette
     */
    hide() {
        this.container.style.display = 'none';
        this.isOpen = false;
    }
    
    /**
     * Handle search input changes
     */
    handleSearch() {
        this.searchTerm = this.searchInput.value.trim().toLowerCase();
        this.filterCommands();
        this.renderResults();
    }
    
    /**
     * Filter commands based on search term
     */
    filterCommands() {
        if (!this.searchTerm) {
            // Show recent commands first, then all commands
            const recentCommandIds = new Set(this.recentCommands);
            const recentCommands = this.commands.filter(cmd => recentCommandIds.has(cmd.id));
            const otherCommands = this.commands.filter(cmd => !recentCommandIds.has(cmd.id));
            this.filteredCommands = [...recentCommands, ...otherCommands];
            return;
        }
        
        const searchParts = this.searchTerm.split(' ');
        
        // Filter commands by search term
        this.filteredCommands = this.commands.filter(command => {
            const titleMatch = command.title.toLowerCase().includes(this.searchTerm);
            const descMatch = command.description.toLowerCase().includes(this.searchTerm);
            const categoryMatch = command.category.toLowerCase().includes(this.searchTerm);
            
            // Check if all parts of the search query match
            const allPartsMatch = searchParts.every(part => 
                command.title.toLowerCase().includes(part) || 
                command.description.toLowerCase().includes(part) ||
                command.category.toLowerCase().includes(part)
            );
            
            return titleMatch || descMatch || categoryMatch || allPartsMatch;
        });
        
        // Sort by relevance
        this.filteredCommands.sort((a, b) => {
            // Exact title matches come first
            const aExactTitle = a.title.toLowerCase() === this.searchTerm;
            const bExactTitle = b.title.toLowerCase() === this.searchTerm;
            
            if (aExactTitle && !bExactTitle) return -1;
            if (!aExactTitle && bExactTitle) return 1;
            
            // Then title starts with search term
            const aStartsWithTitle = a.title.toLowerCase().startsWith(this.searchTerm);
            const bStartsWithTitle = b.title.toLowerCase().startsWith(this.searchTerm);
            
            if (aStartsWithTitle && !bStartsWithTitle) return -1;
            if (!aStartsWithTitle && bStartsWithTitle) return 1;
            
            // Then check if in recent commands
            const aIsRecent = this.recentCommands.includes(a.id);
            const bIsRecent = this.recentCommands.includes(b.id);
            
            if (aIsRecent && !bIsRecent) return -1;
            if (!aIsRecent && bIsRecent) return 1;
            
            // Default to alphabetical
            return a.title.localeCompare(b.title);
        });
        
        this.selectedIndex = 0;
    }
    
    /**
     * Render filtered results to the UI
     */
    renderResults() {
        this.resultsContainer.innerHTML = '';
        
        if (this.filteredCommands.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'command-palette-no-results';
            noResults.innerHTML = `
                <i class="fas fa-search-minus mb-3 fa-2x"></i>
                <div>No commands found matching "${this.searchTerm}"</div>
            `;
            this.resultsContainer.appendChild(noResults);
            return;
        }
        
        // Group commands by category
        const commandsByCategory = {};
        
        if (!this.searchTerm && this.recentCommands.length > 0) {
            // Add recent commands category if showing all commands
            commandsByCategory['Recent'] = this.filteredCommands.filter(
                cmd => this.recentCommands.includes(cmd.id)
            ).slice(0, this.maxRecentCommands);
        }
        
        // Group remaining commands by their categories
        this.filteredCommands.forEach(command => {
            if (
                !this.searchTerm && 
                this.recentCommands.includes(command.id) && 
                commandsByCategory['Recent']?.some(c => c.id === command.id)
            ) {
                return; // Skip if already in recent category
            }
            
            if (!commandsByCategory[command.category]) {
                commandsByCategory[command.category] = [];
            }
            commandsByCategory[command.category].push(command);
        });
        
        // Render each category
        Object.keys(commandsByCategory).forEach(category => {
            const commands = commandsByCategory[category];
            if (commands.length === 0) return;
            
            // Create category header
            const categoryEl = document.createElement('div');
            categoryEl.className = 'command-palette-category';
            categoryEl.textContent = category;
            this.resultsContainer.appendChild(categoryEl);
            
            // Create command items
            commands.forEach(command => {
                const item = this.createCommandItem(command);
                this.resultsContainer.appendChild(item);
            });
        });
        
        // Highlight first item
        this.highlightItem(this.selectedIndex);
    }
    
    /**
     * Create a command item element
     * @param {Object} command - Command object
     * @returns {HTMLElement} Command item element
     */
    createCommandItem(command) {
        const item = document.createElement('div');
        item.className = 'command-palette-item';
        item.dataset.id = command.id;
        
        // Highlight matching text if search term exists
        let title = command.title;
        let description = command.description;
        
        if (this.searchTerm) {
            const regex = new RegExp(`(${this.searchTerm.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
            title = command.title.replace(regex, '<span class="command-palette-match">$1</span>');
            description = command.description.replace(regex, '<span class="command-palette-match">$1</span>');
        }
        
        // Add badge if present
        let badgeHtml = '';
        if (command.badge) {
            if (typeof command.badge === 'string') {
                badgeHtml = `<span class="command-palette-badge">${command.badge}</span>`;
            } else {
                badgeHtml = `<span class="command-palette-badge ${command.badge.type}">${command.badge.text}</span>`;
            }
        }
        
        // Add shortcut if present
        let shortcutHtml = '';
        if (command.shortcut) {
            shortcutHtml = `
                <div class="command-palette-item-shortcut">
                    ${command.shortcut.map(key => `<kbd>${key}</kbd>`).join('')}
                </div>
            `;
        }
        
        item.innerHTML = `
            <div class="command-palette-item-icon">
                <i class="${command.icon}"></i>
            </div>
            <div class="command-palette-item-text">
                <div class="command-palette-item-title">${title}${badgeHtml}</div>
                <div class="command-palette-item-desc">${description}</div>
            </div>
            ${shortcutHtml}
        `;
        
        // Add click event
        item.addEventListener('click', () => {
            this.executeCommand(command);
        });
        
        // Add mouseover event
        item.addEventListener('mouseover', () => {
            const newIndex = Array.from(this.resultsContainer.querySelectorAll('.command-palette-item'))
                .findIndex(el => el === item);
            if (newIndex !== -1) {
                this.selectedIndex = newIndex;
                this.highlightItem(this.selectedIndex);
            }
        });
        
        return item;
    }
    
    /**
     * Highlight a command item by index
     * @param {number} index - Index of the item to highlight
     */
    highlightItem(index) {
        const items = this.resultsContainer.querySelectorAll('.command-palette-item');
        
        // Remove highlighting from all items
        items.forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add highlighting to selected item
        if (items.length > 0 && index >= 0 && index < items.length) {
            items[index].classList.add('selected');
            
            // Scroll into view if needed
            const container = this.resultsContainer;
            const item = items[index];
            
            const containerRect = container.getBoundingClientRect();
            const itemRect = item.getBoundingClientRect();
            
            if (itemRect.bottom > containerRect.bottom) {
                container.scrollTop += itemRect.bottom - containerRect.bottom;
            } else if (itemRect.top < containerRect.top) {
                container.scrollTop -= containerRect.top - itemRect.top;
            }
        }
    }
    
    /**
     * Handle keyboard navigation in the command palette
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleInputKeyDown(e) {
        const items = this.resultsContainer.querySelectorAll('.command-palette-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.selectedIndex = (this.selectedIndex + 1) % items.length;
            this.highlightItem(this.selectedIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.selectedIndex = (this.selectedIndex - 1 + items.length) % items.length;
            this.highlightItem(this.selectedIndex);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            
            if (items.length > 0 && this.selectedIndex >= 0 && this.selectedIndex < items.length) {
                const selectedItem = items[this.selectedIndex];
                const commandId = selectedItem.dataset.id;
                const command = this.filteredCommands.find(cmd => cmd.id === commandId);
                
                if (command) {
                    this.executeCommand(command);
                }
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            this.hide();
        }
    }
    
    /**
     * Execute a command and handle the result
     * @param {Object} command - Command object to execute
     */
    executeCommand(command) {
        try {
            // Hide the command palette
            this.hide();
            
            // Add to recent commands
            this.addToRecentCommands(command.id);
            
            // Add to command history
            this.addToCommandHistory(command);
            
            // Execute the command
            if (typeof command.action === 'function') {
                command.action();
            }
        } catch (error) {
            console.error('Error executing command:', error);
            alert(`Error executing command: ${error.message}`);
        }
    }
    
    /**
     * Add a command to recent commands
     * @param {string} commandId - ID of the command to add
     */
    addToRecentCommands(commandId) {
        // Remove if already in recent commands
        this.recentCommands = this.recentCommands.filter(id => id !== commandId);
        
        // Add to front
        this.recentCommands.unshift(commandId);
        
        // Limit to max recent commands
        if (this.recentCommands.length > this.maxRecentCommands) {
            this.recentCommands = this.recentCommands.slice(0, this.maxRecentCommands);
        }
        
        // Save to localStorage
        localStorage.setItem('synapseCommandPaletteRecent', JSON.stringify(this.recentCommands));
    }
    
    /**
     * Add a command to command history
     * @param {Object} command - Command object to add to history
     */
    addToCommandHistory(command) {
        const timestamp = new Date().toISOString();
        
        this.commandHistory.unshift({
            id: command.id,
            title: command.title,
            category: command.category,
            timestamp
        });
        
        // Limit history size
        if (this.commandHistory.length > this.maxHistory) {
            this.commandHistory = this.commandHistory.slice(0, this.maxHistory);
        }
        
        // Save to localStorage
        localStorage.setItem('synapseCommandPaletteHistory', JSON.stringify(this.commandHistory));
    }
    
    /**
     * Load user preferences from localStorage
     */
    loadUserPreferences() {
        // Load recent commands
        try {
            const recentCommandsJson = localStorage.getItem('synapseCommandPaletteRecent');
            if (recentCommandsJson) {
                this.recentCommands = JSON.parse(recentCommandsJson);
            }
        } catch (error) {
            console.error('Error loading recent commands:', error);
            this.recentCommands = [];
        }
    }
    
    /**
     * Load command history from localStorage
     */
    loadCommandHistory() {
        try {
            const historyJson = localStorage.getItem('synapseCommandPaletteHistory');
            if (historyJson) {
                this.commandHistory = JSON.parse(historyJson);
            }
        } catch (error) {
            console.error('Error loading command history:', error);
            this.commandHistory = [];
        }
    }
    
    /**
     * Handle global keyboard shortcut to open command palette
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyDown(e) {
        // Ctrl+K or Cmd+K to open command palette
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.toggle();
        }
        
        // Handle command category shortcuts when palette is closed
        if (!this.isOpen && e.key === 'g' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            // Start the shortcut sequence
            this.shortcutTimeout = setTimeout(() => {
                this.activeShortcut = null;
            }, 1500);
            
            this.activeShortcut = 'g';
        } else if (this.activeShortcut === 'g') {
            clearTimeout(this.shortcutTimeout);
            
            // Check for valid navigation shortcuts
            const targetCommands = {
                'h': 'home',
                't': 'terminal',
                'm': 'memory',
                'p': 'platforms',
                's': 'settings'
            };
            
            if (targetCommands[e.key]) {
                const commandId = targetCommands[e.key];
                const command = this.commands.find(cmd => cmd.id === commandId);
                
                if (command) {
                    this.executeCommand(command);
                }
            }
            
            this.activeShortcut = null;
        }
    }
    
    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        const body = document.body;
        if (body.getAttribute('data-bs-theme') === 'light') {
            body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('synapseTheme', 'dark');
        } else {
            body.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('synapseTheme', 'light');
        }
    }
    
    /**
     * Clear system cache
     */
    clearCache() {
        if (confirm('Are you sure you want to clear the system cache? This will refresh the page.')) {
            localStorage.removeItem('synapseCommandPaletteRecent');
            localStorage.removeItem('synapseCommandPaletteHistory');
            
            // Clear other cache items
            const cacheKeys = Object.keys(localStorage).filter(key => 
                key.startsWith('synapse') && 
                key !== 'synapseTheme'
            );
            
            cacheKeys.forEach(key => {
                localStorage.removeItem(key);
            });
            
            // Reload page
            window.location.reload();
        }
    }
    
    /**
     * Open search memory interface
     */
    openSearchMemory() {
        const searchTerm = prompt('Enter search term to find in memory system:');
        if (searchTerm) {
            window.location.href = `/memory/search?q=${encodeURIComponent(searchTerm)}`;
        }
    }
    
    /**
     * Start a new training session
     */
    startNewTraining() {
        const confirmed = confirm('Start a new training session? This will open the training configuration interface.');
        if (confirmed) {
            window.location.href = '/training/new';
        }
    }
    
    /**
     * Toggle preview mode
     */
    togglePreviewMode() {
        const isPreviewMode = localStorage.getItem('synapsePreviewMode') === 'true';
        localStorage.setItem('synapsePreviewMode', (!isPreviewMode).toString());
        
        alert(`Preview mode ${!isPreviewMode ? 'enabled' : 'disabled'}`);
        window.location.reload();
    }
}

// Initialize command palette when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.synapseCommandPalette = new SynapseCommandPalette();
    
    // Add UI button for command palette if needed
    const addCommandButton = () => {
        const existingButton = document.getElementById('commandPaletteBtn');
        if (existingButton) return;
        
        const button = document.createElement('button');
        button.id = 'commandPaletteBtn';
        button.className = 'btn btn-sm btn-dark position-fixed';
        button.style.bottom = '20px';
        button.style.right = '20px';
        button.style.zIndex = '1000';
        button.style.width = '40px';
        button.style.height = '40px';
        button.style.borderRadius = '50%';
        button.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
        button.innerHTML = '<i class="fas fa-bolt"></i>';
        button.title = 'Command Palette (Ctrl+K)';
        
        button.addEventListener('click', () => {
            window.synapseCommandPalette.toggle();
        });
        
        document.body.appendChild(button);
    };
    
    // Wait a bit for other scripts to load
    setTimeout(addCommandButton, 500);
});