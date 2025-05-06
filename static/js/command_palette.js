/**
 * Synapse Chamber Command Palette
 * 
 * A powerful command palette that provides quick access to all system functions
 * through keyboard shortcuts and natural language processing.
 */

class CommandPalette {
    constructor(options = {}) {
        this.options = Object.assign({
            maxResults: 10,
            shortcutKey: 'p',
            shortcutModifier: 'ctrl+shift',
            placeholder: 'Type a command or search...',
            fuzzyMatchThreshold: 0.3,
            enableNaturalLanguage: true,
            animationDuration: 300
        }, options);
        
        // Store commands with descriptions and handlers
        this.commands = [];
        
        // Context for commands
        this.context = {
            currentSection: null,
            selectedFile: null,
            selectedComponent: null,
            activeTrainingSession: null,
            brainVisualization: null
        };
        
        // Initialize the UI
        this.initUI();
        
        // Register keyboard shortcut
        this.registerShortcut();
        
        // Initialize default commands
        this.registerDefaultCommands();
    }

    initUI() {
        // Create command palette element
        this.element = document.createElement('div');
        this.element.className = 'command-palette';
        
        // Input field
        this.inputWrapper = document.createElement('div');
        this.inputWrapper.className = 'command-input-wrapper';
        
        this.input = document.createElement('input');
        this.input.type = 'text';
        this.input.className = 'command-input';
        this.input.placeholder = this.options.placeholder;
        
        this.inputWrapper.appendChild(this.input);
        this.element.appendChild(this.inputWrapper);
        
        // Results container
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'command-results';
        this.element.appendChild(this.resultsContainer);
        
        // Add to DOM
        document.body.appendChild(this.element);
        
        // Set up event listeners
        this.input.addEventListener('input', () => this.updateResults());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isVisible && !this.element.contains(e.target)) {
                this.hide();
            }
        });
        
        // Prevent clicks inside from propagating
        this.element.addEventListener('click', (e) => e.stopPropagation());
        
        // Initial state
        this.isVisible = false;
        this.selectedIndex = -1;
    }

    registerShortcut() {
        document.addEventListener('keydown', (e) => {
            // Check for shortcut (Ctrl+Shift+P by default)
            const modifierKey = this.options.shortcutModifier.includes('ctrl') && e.ctrlKey ||
                               this.options.shortcutModifier.includes('shift') && e.shiftKey ||
                               this.options.shortcutModifier.includes('alt') && e.altKey ||
                               this.options.shortcutModifier.includes('meta') && e.metaKey;
                               
            const mainKey = e.key.toLowerCase() === this.options.shortcutKey.toLowerCase();
            
            if (modifierKey && mainKey) {
                e.preventDefault();
                this.toggle();
            }
            
            // ESC to close
            if (e.key === 'Escape' && this.isVisible) {
                e.preventDefault();
                this.hide();
            }
        });
    }

    registerCommand(command) {
        if (!command.id || !command.title || !command.handler) {
            console.error('Command must have id, title, and handler properties');
            return;
        }
        
        // Add to commands list
        this.commands.push(command);
    }

    registerDefaultCommands() {
        // Navigation commands
        this.registerCommand({
            id: 'navigate-home',
            title: 'Navigate to Home',
            description: 'Go to the home page',
            icon: 'fas fa-home',
            shortcut: 'Alt+H',
            category: 'navigation',
            handler: () => window.location.href = '/'
        });
        
        this.registerCommand({
            id: 'navigate-dashboard',
            title: 'Open Dashboard',
            description: 'Go to the analytics dashboard',
            icon: 'fas fa-chart-line',
            shortcut: 'Alt+D',
            category: 'navigation',
            handler: () => window.location.href = '/dashboard'
        });
        
        this.registerCommand({
            id: 'navigate-training',
            title: 'Open Training',
            description: 'Go to the training interface',
            icon: 'fas fa-graduation-cap',
            shortcut: 'Alt+T',
            category: 'navigation',
            handler: () => window.location.href = '/training'
        });
        
        this.registerCommand({
            id: 'navigate-memory',
            title: 'Open Memory Explorer',
            description: 'Go to the memory exploration interface',
            icon: 'fas fa-brain',
            shortcut: 'Alt+M',
            category: 'navigation',
            handler: () => window.location.href = '/memory'
        });
        
        // UI commands
        this.registerCommand({
            id: 'toggle-dock',
            title: 'Toggle Dock Panel',
            description: 'Show or hide the dock panel',
            icon: 'fas fa-columns',
            shortcut: 'Alt+1',
            category: 'ui',
            handler: () => {
                const dockBtn = document.getElementById('toggleDockBtn');
                if (dockBtn) dockBtn.click();
            }
        });
        
        this.registerCommand({
            id: 'toggle-theme',
            title: 'Toggle Dark/Light Theme',
            description: 'Switch between dark and light theme',
            icon: 'fas fa-moon',
            shortcut: 'Alt+L',
            category: 'ui',
            handler: () => {
                const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-bs-theme', theme);
                // Store preference
                localStorage.setItem('theme-preference', theme);
                
                // Show notification
                if (window.showNotification) {
                    window.showNotification('info', `Theme changed to ${theme} mode`);
                }
            }
        });
        
        this.registerCommand({
            id: 'fullscreen-toggle',
            title: 'Toggle Fullscreen',
            description: 'Enter or exit fullscreen mode',
            icon: 'fas fa-expand',
            shortcut: 'F11',
            category: 'ui',
            handler: () => {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    }
                }
            }
        });
        
        // Training commands
        this.registerCommand({
            id: 'start-training',
            title: 'Start New Training Session',
            description: 'Begin a new AI training session',
            icon: 'fas fa-play',
            shortcut: 'Alt+N',
            category: 'training',
            handler: () => window.location.href = '/training/new'
        });
        
        this.registerCommand({
            id: 'view-logs',
            title: 'View Training Logs',
            description: 'See logs from previous training sessions',
            icon: 'fas fa-list',
            shortcut: 'Alt+L',
            category: 'training',
            handler: () => window.location.href = '/logs'
        });
        
        // File operations
        this.registerCommand({
            id: 'new-file',
            title: 'Create New File',
            description: 'Create a new file in the project',
            icon: 'fas fa-file-plus',
            shortcut: 'Alt+F',
            category: 'file',
            handler: () => {
                const newFileBtn = document.getElementById('newFileBtn');
                if (newFileBtn) newFileBtn.click();
            }
        });
        
        this.registerCommand({
            id: 'new-folder',
            title: 'Create New Folder',
            description: 'Create a new folder in the project',
            icon: 'fas fa-folder-plus',
            shortcut: 'Alt+G',
            category: 'file',
            handler: () => {
                const newFolderBtn = document.getElementById('newFolderBtn');
                if (newFolderBtn) newFolderBtn.click();
            }
        });
        
        // Brain visualization commands
        this.registerCommand({
            id: 'brain-toggle',
            title: 'Toggle Brain Visualization',
            description: 'Show or hide the 3D brain visualization',
            icon: 'fas fa-brain',
            shortcut: 'Alt+B',
            category: 'visualization',
            handler: () => {
                // This handler will be updated when brain visualization is enabled
                const brainContainer = document.getElementById('brainVisualizationContainer');
                if (brainContainer) {
                    brainContainer.classList.toggle('d-none');
                    // Show notification
                    if (window.showNotification) {
                        const visible = !brainContainer.classList.contains('d-none');
                        window.showNotification('info', `Brain visualization ${visible ? 'shown' : 'hidden'}`);
                    }
                } else {
                    // Show notification that visualization isn't available
                    if (window.showNotification) {
                        window.showNotification('warning', 'Brain visualization not available on this page');
                    }
                }
            }
        });
        
        // Agent commands
        this.registerCommand({
            id: 'agent-new-project',
            title: 'Create New Agent Project',
            description: 'Have the agent create a new project',
            icon: 'fas fa-robot',
            shortcut: 'Alt+P',
            category: 'agent',
            handler: () => {
                const newProjectBtn = document.getElementById('newProjectBtn');
                if (newProjectBtn) newProjectBtn.click();
            }
        });
        
        // Run application command
        this.registerCommand({
            id: 'run-application',
            title: 'Run Application',
            description: 'Start or restart the application',
            icon: 'fas fa-play',
            shortcut: 'Alt+R',
            category: 'development',
            handler: () => {
                const runButton = document.getElementById('runButton');
                if (runButton) runButton.click();
            }
        });
        
        // Help command
        this.registerCommand({
            id: 'show-help',
            title: 'Show Help',
            description: 'Display help information and keyboard shortcuts',
            icon: 'fas fa-question-circle',
            shortcut: 'F1',
            category: 'help',
            handler: () => {
                // Show help modal or navigate to help page
                const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
                if (helpModal) {
                    helpModal.show();
                } else {
                    window.location.href = '/help';
                }
            }
        });
    }

    show() {
        if (this.isVisible) return;
        
        // Show the palette
        this.element.classList.add('visible');
        this.isVisible = true;
        
        // Clear and focus input
        this.input.value = '';
        setTimeout(() => this.input.focus(), 10);
        
        // Update results (show all commands initially)
        this.updateResults();
    }

    hide() {
        if (!this.isVisible) return;
        
        this.element.classList.remove('visible');
        this.isVisible = false;
        
        // Clear input and results
        this.input.value = '';
        this.resultsContainer.innerHTML = '';
        this.selectedIndex = -1;
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    updateResults() {
        const query = this.input.value.trim().toLowerCase();
        let results;
        
        if (!query) {
            // Show all commands, grouped by category
            results = this.groupCommandsByCategory(this.commands);
        } else if (this.options.enableNaturalLanguage && this.isNaturalLanguageQuery(query)) {
            // Process as natural language
            results = this.processNaturalLanguage(query);
        } else {
            // Regular search
            results = this.commands.filter(cmd => {
                // Match against title, description or category
                return cmd.title.toLowerCase().includes(query) ||
                       (cmd.description && cmd.description.toLowerCase().includes(query)) ||
                       (cmd.category && cmd.category.toLowerCase().includes(query));
            }).slice(0, this.options.maxResults);
        }
        
        this.renderResults(results);
    }

    groupCommandsByCategory(commands) {
        // Get unique categories
        const categories = [...new Set(commands.map(cmd => cmd.category || 'other'))];
        
        // Sort categories
        const categoryOrder = ['navigation', 'ui', 'training', 'file', 'agent', 'development', 'visualization', 'help', 'other'];
        categories.sort((a, b) => {
            const indexA = categoryOrder.indexOf(a);
            const indexB = categoryOrder.indexOf(b);
            return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
        });
        
        // Group commands
        const grouped = {};
        categories.forEach(category => {
            grouped[category] = commands.filter(cmd => (cmd.category || 'other') === category);
        });
        
        // Flatten but keep category headers
        const results = [];
        categories.forEach(category => {
            if (grouped[category].length === 0) return;
            
            // Add category header
            results.push({
                isHeader: true,
                category: category,
                title: this.formatCategoryName(category)
            });
            
            // Add commands in this category
            results.push(...grouped[category]);
        });
        
        return results;
    }

    formatCategoryName(category) {
        return category.charAt(0).toUpperCase() + category.slice(1);
    }

    isNaturalLanguageQuery(query) {
        // Check if query looks like natural language
        // Simple heuristic: contains a verb or has multiple words with articles
        const verbs = ['show', 'open', 'go', 'navigate', 'create', 'make', 'start', 'run', 'toggle', 'display'];
        const hasVerb = verbs.some(verb => query.includes(verb));
        
        const hasArticle = ['the', 'a', 'an'].some(article => query.includes(` ${article} `));
        
        return hasVerb || hasArticle || query.split(' ').length > 3;
    }

    processNaturalLanguage(query) {
        // This is a simplified NLP processor
        // In a real implementation, you'd use a more sophisticated approach
        
        // Extract key terms
        const words = query.split(/\s+/);
        
        // Action words map to command categories
        const actionMap = {
            'show': ['ui', 'visualization'],
            'view': ['ui', 'visualization'],
            'display': ['ui', 'visualization'],
            'open': ['navigation', 'file'],
            'go': ['navigation'],
            'navigate': ['navigation'],
            'create': ['file', 'agent'],
            'new': ['file', 'agent'],
            'make': ['file', 'agent'],
            'start': ['training', 'development'],
            'run': ['development'],
            'toggle': ['ui'],
            'switch': ['ui'],
            'help': ['help'],
            'file': ['file'],
            'folder': ['file'],
            'brain': ['visualization'],
            'train': ['training'],
            'agent': ['agent'],
            'project': ['agent', 'file'],
            'theme': ['ui']
        };
        
        // Score each command based on term matches
        const scoredCommands = this.commands.map(cmd => {
            let score = 0;
            
            // Check each word in the query
            words.forEach(word => {
                // Direct matches in command properties
                if (cmd.title.toLowerCase().includes(word)) score += 10;
                if (cmd.description && cmd.description.toLowerCase().includes(word)) score += 5;
                if (cmd.category && cmd.category.toLowerCase().includes(word)) score += 3;
                
                // Check if word is an action word that maps to this command's category
                const categories = actionMap[word] || [];
                if (categories.includes(cmd.category)) score += 7;
            });
            
            return { command: cmd, score };
        });
        
        // Sort by score and get top results
        const sortedCommands = scoredCommands
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, this.options.maxResults)
            .map(item => item.command);
            
        // If no results, return empty array
        if (sortedCommands.length === 0) {
            return [{
                isHeader: true,
                category: 'no-results',
                title: 'No matching commands found'
            }];
        }
            
        return sortedCommands;
    }

    renderResults(results) {
        // Clear previous results
        this.resultsContainer.innerHTML = '';
        
        // Create and append result elements
        results.forEach((result, index) => {
            if (result.isHeader) {
                // Category header
                const header = document.createElement('div');
                header.className = 'command-category-header';
                header.textContent = result.title;
                this.resultsContainer.appendChild(header);
                return;
            }
            
            const resultElement = document.createElement('div');
            resultElement.className = 'command-result';
            resultElement.dataset.index = index;
            
            // Icon
            const iconElement = document.createElement('div');
            iconElement.className = 'command-icon';
            
            const icon = document.createElement('i');
            icon.className = result.icon || 'fas fa-terminal';
            iconElement.appendChild(icon);
            
            // Details
            const detailsElement = document.createElement('div');
            detailsElement.className = 'command-details';
            
            const titleElement = document.createElement('div');
            titleElement.className = 'command-title';
            titleElement.textContent = result.title;
            detailsElement.appendChild(titleElement);
            
            if (result.description) {
                const descriptionElement = document.createElement('div');
                descriptionElement.className = 'command-description';
                descriptionElement.textContent = result.description;
                detailsElement.appendChild(descriptionElement);
            }
            
            // Shortcut
            let shortcutElement = null;
            if (result.shortcut) {
                shortcutElement = document.createElement('div');
                shortcutElement.className = 'command-shortcut';
                shortcutElement.textContent = result.shortcut;
            }
            
            // Assemble
            resultElement.appendChild(iconElement);
            resultElement.appendChild(detailsElement);
            if (shortcutElement) {
                resultElement.appendChild(shortcutElement);
            }
            
            // Add click handler
            resultElement.addEventListener('click', () => {
                this.executeCommand(result);
            });
            
            this.resultsContainer.appendChild(resultElement);
        });
        
        // Reset selection
        this.selectedIndex = -1;
    }

    handleKeydown(e) {
        if (!this.isVisible) return;
        
        const resultElements = this.resultsContainer.querySelectorAll('.command-result');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, resultElements.length - 1);
                this.updateSelection();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.updateSelection();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.selectedIndex < resultElements.length) {
                    const selectedResult = resultElements[this.selectedIndex];
                    const commandIndex = parseInt(selectedResult.dataset.index, 10);
                    const command = this.commands[commandIndex];
                    if (command) {
                        this.executeCommand(command);
                    }
                }
                break;
        }
    }

    updateSelection() {
        const resultElements = this.resultsContainer.querySelectorAll('.command-result');
        resultElements.forEach((el, index) => {
            if (index === this.selectedIndex) {
                el.classList.add('selected');
                // Scroll into view if needed
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                el.classList.remove('selected');
            }
        });
    }

    executeCommand(command) {
        // Hide the palette
        this.hide();
        
        // Execute the command
        try {
            command.handler(this.context);
        } catch (error) {
            console.error('Error executing command:', error);
            
            // Show error notification
            if (window.showNotification) {
                window.showNotification('error', `Error executing command: ${error.message}`);
            }
        }
    }

    // Update context with current system state
    updateContext(contextUpdates) {
        this.context = { ...this.context, ...contextUpdates };
    }
}

// Create global command palette instance when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Create command palette instance
    window.commandPalette = new CommandPalette();
});