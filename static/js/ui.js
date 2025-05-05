// UI.js - Client-side interactions for Synapse Chamber

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize platform selection in AI Interaction page
    const platformCards = document.querySelectorAll('.platform-card');
    if (platformCards.length > 0) {
        platformCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove active class from all cards
                platformCards.forEach(c => c.classList.remove('border-primary'));
                
                // Add active class to clicked card
                this.classList.add('border-primary');
                
                // Set hidden input value
                const platformInput = document.getElementById('selected-platform');
                if (platformInput) {
                    platformInput.value = this.getAttribute('data-platform');
                }
            });
        });
    }

    // Handle AI Interaction form submission
    const interactionForm = document.getElementById('interaction-form');
    if (interactionForm) {
        interactionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const platformInput = document.getElementById('selected-platform');
            const promptInput = document.getElementById('prompt');
            const subjectInput = document.getElementById('subject');
            const goalInput = document.getElementById('goal');
            
            // Validate inputs
            if (!platformInput.value) {
                showAlert('Please select an AI platform first', 'warning');
                return;
            }
            
            if (!promptInput.value.trim()) {
                showAlert('Please enter a prompt', 'warning');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            // Hide previous response
            const responseContainer = document.getElementById('response-container');
            if (responseContainer) {
                responseContainer.classList.add('d-none');
            }
            
            // Prepare data
            const data = {
                platform: platformInput.value,
                prompt: promptInput.value,
                subject: subjectInput ? subjectInput.value : '',
                goal: goalInput ? goalInput.value : ''
            };
            
            // Send request
            fetch('/api/start_interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                // Reset form state
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                if (result.status === 'success') {
                    // Display response
                    displayResponse(result);
                    
                    // Add to conversation history
                    if (result.conversation_id) {
                        addToConversationHistory({
                            id: result.conversation_id,
                            platform: result.platform,
                            subject: data.subject || 'Untitled Conversation',
                            created_at: result.timestamp || new Date().toISOString()
                        });
                    }
                } else {
                    showAlert('Error: ' + (result.message || 'Unknown error'), 'danger');
                }
            })
            .catch(error => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                showAlert('Error: ' + error.message, 'danger');
            });
        });
    }

    // Load conversation history
    if (document.getElementById('conversation-history')) {
        loadConversationHistory();
    }

    // Load logs if on logs page
    if (document.getElementById('logs-container')) {
        loadLogs();
    }

    // Handle settings form submission
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const data = {
                browser_settings: {
                    headless: formData.get('browser_headless') === 'on',
                    timeout: parseInt(formData.get('browser_timeout')) || 30,
                    screenshot_on_action: formData.get('browser_screenshot') === 'on'
                },
                captcha_settings: {
                    auto_solve: formData.get('captcha_auto_solve') === 'on',
                    timeout: parseInt(formData.get('captcha_timeout')) || 60
                },
                memory_settings: {
                    storage_type: formData.get('memory_storage_type') || 'database',
                    vector_db_url: formData.get('memory_vector_db_url') || ''
                }
            };
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            // Send request
            fetch('/api/save_settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                // Reset form state
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                if (result.status === 'success') {
                    showAlert('Settings saved successfully', 'success');
                } else {
                    showAlert('Error: ' + (result.message || 'Unknown error'), 'danger');
                }
            })
            .catch(error => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                showAlert('Error: ' + error.message, 'danger');
            });
        });
    }
});

function displayResponse(data) {
    const responseContainer = document.getElementById('response-container');
    if (!responseContainer) return;
    
    // Create response content
    responseContainer.innerHTML = `
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <div>
                    <span class="platform-label">
                        <span class="platform-icon">${capitalizeFirstLetter(data.platform)}</span>
                    </span>
                </div>
                <small class="text-muted">${new Date(data.timestamp || Date.now()).toLocaleString()}</small>
            </div>
            <div class="card-body">
                <h5 class="card-title">Response</h5>
                <div class="response-content">${formatResponse(data.response)}</div>
            </div>
            <div class="card-footer">
                <small class="text-muted">Conversation ID: ${data.conversation_id || 'N/A'}</small>
            </div>
        </div>
    `;
    
    // Show response container
    responseContainer.classList.remove('d-none');
    
    // Scroll to response
    responseContainer.scrollIntoView({ behavior: 'smooth' });
}

function formatResponse(text) {
    if (!text) return 'No response received';
    
    // Handle code blocks (triple backticks)
    text = text.replace(/```([a-z]*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');
    
    // Handle inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Handle line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.innerHTML = alertHTML;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function addToConversationHistory(conversation) {
    let history = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
    
    // Add new conversation to history if not already present
    if (!history.some(conv => conv.id === conversation.id)) {
        history.unshift(conversation);
        
        // Limit history size
        if (history.length > 10) {
            history = history.slice(0, 10);
        }
        
        localStorage.setItem('conversationHistory', JSON.stringify(history));
        
        // Update UI if history container exists
        const historyContainer = document.getElementById('conversation-history');
        if (historyContainer) {
            updateConversationHistoryUI(history);
        }
    }
}

function loadConversationHistory() {
    const history = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
    updateConversationHistoryUI(history);
}

function updateConversationHistoryUI(history) {
    const historyContainer = document.getElementById('conversation-history');
    if (!historyContainer) return;
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<div class="text-muted text-center py-3">No recent conversations</div>';
        return;
    }
    
    let html = '';
    history.forEach(conv => {
        const date = new Date(conv.created_at).toLocaleDateString();
        html += `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${conv.subject || 'Untitled'}</div>
                    <small class="text-muted">
                        <span class="platform-label">
                            <span class="platform-icon">${capitalizeFirstLetter(conv.platform)}</span>
                        </span>
                        ${date}
                    </small>
                </div>
                <a href="/logs?conversation=${conv.id}" class="btn btn-sm btn-outline-secondary">View</a>
            </div>
        `;
    });
    
    historyContainer.innerHTML = html;
}

function loadLogs() {
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) return;
    
    // Check if specific conversation view
    const conversationView = document.getElementById('conversation-view');
    if (conversationView) {
        // Already viewing a specific conversation
        return;
    }
    
    // Fetch conversations
    fetch('/api/conversations')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.conversations) {
                displayConversationsList(data.conversations);
            } else {
                // Use mock data for demonstration
                displayMockConversations();
            }
        })
        .catch(error => {
            console.error('Error loading conversations:', error);
            // Use mock data for demonstration
            displayMockConversations();
        });
}

function displayConversationDetails(conversation) {
    const conversationView = document.getElementById('conversation-view');
    if (!conversationView) return;
    
    let messagesHTML = '';
    if (conversation.messages && conversation.messages.length > 0) {
        conversation.messages.forEach(msg => {
            const date = new Date(msg.timestamp).toLocaleString();
            const messageClass = msg.is_user ? 'user-message' : 'ai-message';
            const sender = msg.is_user ? 'You' : capitalizeFirstLetter(conversation.platform);
            
            let screenshotHTML = '';
            if (msg.screenshot_path) {
                screenshotHTML = `
                    <div class="message-screenshot mt-2">
                        <img src="${msg.screenshot_path}" alt="Screenshot" class="thumbnail img-fluid" 
                            onclick="window.open('${msg.screenshot_path}', '_blank')">
                    </div>
                `;
            }
            
            messagesHTML += `
                <div class="message ${messageClass}">
                    <div class="message-header">
                        <strong>${sender}</strong>
                        <small class="text-muted">${date}</small>
                    </div>
                    <div class="message-content">${formatResponse(msg.content)}</div>
                    ${screenshotHTML}
                </div>
            `;
        });
    } else {
        messagesHTML = '<div class="text-center text-muted py-4">No messages in this conversation</div>';
    }
    
    conversationView.innerHTML = `
        <div class="card">
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${conversation.subject || 'Untitled Conversation'}</h5>
                    <span class="badge bg-secondary">${capitalizeFirstLetter(conversation.platform)}</span>
                </div>
                ${conversation.goal ? `<div class="text-muted small mt-1">Goal: ${conversation.goal}</div>` : ''}
            </div>
            <div class="card-body">
                <div class="messages-container">
                    ${messagesHTML}
                </div>
            </div>
            <div class="card-footer text-muted">
                <small>Created: ${new Date(conversation.created_at).toLocaleString()}</small>
            </div>
        </div>
    `;
}

function displayConversationsList(conversations) {
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) return;
    
    if (conversations.length === 0) {
        logsContainer.innerHTML = '<div class="alert alert-info">No conversations found</div>';
        return;
    }
    
    let html = '<div class="list-group">';
    conversations.forEach(conv => {
        const date = new Date(conv.created_at).toLocaleString();
        html += `
            <a href="/logs?conversation=${conv.id}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${conv.subject || 'Untitled Conversation'}</h5>
                    <small>${date}</small>
                </div>
                <div class="d-flex w-100 justify-content-between">
                    <small class="text-muted">
                        <span class="badge bg-secondary">${capitalizeFirstLetter(conv.platform)}</span>
                        ${conv.goal ? ` · Goal: ${conv.goal}` : ''}
                    </small>
                    <small class="text-muted">${conv.message_count || 0} messages</small>
                </div>
            </a>
        `;
    });
    html += '</div>';
    
    logsContainer.innerHTML = html;
}

function displayMockConversations() {
    const mockConversations = [
        {
            id: 1,
            platform: "gpt",
            subject: "Upwork Automation",
            goal: "Create a system to automate Upwork job applications",
            created_at: "2023-06-15T10:30:00",
            message_count: 2
        },
        {
            id: 2,
            platform: "gemini",
            subject: "HELB Portal Enhancement",
            goal: "Analyze HELB website architecture for improvements",
            created_at: "2023-06-14T15:45:00",
            message_count: 1
        }
    ];
    
    displayConversationsList(mockConversations);
}