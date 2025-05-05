// Training Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const trainingForm = document.getElementById('training-form');
    const topicSelect = document.getElementById('topic');
    const topicDescription = document.getElementById('topic-description');
    const trainingLogs = document.getElementById('training-logs');
    const clearLogsBtn = document.getElementById('clear-logs-btn');
    const currentSessionCard = document.getElementById('current-session-card');
    const sessionProgress = document.getElementById('session-progress');
    const viewDetailsBtn = document.getElementById('view-details-btn');
    const applyTrainingBtn = document.getElementById('apply-training-btn');
    const modalApplyBtn = document.getElementById('modal-apply-btn');
    
    // Check for existing session
    const currentSessionId = localStorage.getItem('currentTrainingSession');
    if (currentSessionId) {
        // Fetch session status
        fetchSessionStatus(currentSessionId).then(statusData => {
            if (statusData && (statusData.status === 'started' || statusData.status === 'in_progress')) {
                updateCurrentSessionUI(statusData);
                startPollingUpdates(currentSessionId);
            }
        });
    }
    
    // Handle form submission
    if (trainingForm) {
        trainingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get selected platforms
            const platformCheckboxes = document.querySelectorAll('input[name="platforms"]:checked');
            const platforms = Array.from(platformCheckboxes).map(cb => cb.value);
            
            if (platforms.length === 0) {
                showError('Please select at least one AI platform');
                return;
            }
            
            const formData = {
                topic: document.getElementById('topic').value,
                mode: document.getElementById('mode').value,
                platforms: platforms,
                goal: document.getElementById('goal').value
            };
            
            // Disable form while submitting
            const submitBtn = document.getElementById('start-training-btn');
            const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
            
            // Clear previous logs
            if (trainingLogs) {
                trainingLogs.innerHTML = '<div class="text-info">Starting training session...</div>';
            }
            
            // Start training session
            fetch('/api/training/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    showSuccess('Training session started successfully!');
                    
                    // Store session ID for polling
                    const sessionId = data.result.session_id;
                    localStorage.setItem('currentTrainingSession', sessionId);
                    
                    // Update UI to show current session
                    updateCurrentSessionUI(data.result);
                    
                    // Start polling for updates
                    startPollingUpdates(sessionId);
                } else {
                    showError(data.message || 'Failed to start training session');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while starting the training session');
            })
            .finally(() => {
                // Re-enable form
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            });
        });
    }
    
    // Update topic description when selection changes
    if (topicSelect) {
        topicSelect.addEventListener('change', function() {
            const selectedTopic = this.value;
            if (topicDescription) {
                // Get the description from the data attribute
                const descriptions = JSON.parse(topicSelect.dataset.descriptions || '{}');
                topicDescription.textContent = descriptions[selectedTopic] || '';
            }
        });
    }
    
    // Clear logs
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', function() {
            if (trainingLogs) {
                trainingLogs.innerHTML = '<div class="text-muted text-center py-5">Logs cleared</div>';
            }
        });
    }
    
    // View session details
    if (viewDetailsBtn) {
        viewDetailsBtn.addEventListener('click', function() {
            const sessionId = localStorage.getItem('currentTrainingSession');
            if (sessionId) {
                showSessionDetails(sessionId);
            }
        });
    }
    
    // Apply training to AutoDev
    if (applyTrainingBtn) {
        applyTrainingBtn.addEventListener('click', function() {
            const sessionId = localStorage.getItem('currentTrainingSession');
            if (sessionId) {
                applyTrainingToAutodev(sessionId);
            }
        });
    }
    
    // Modal apply button
    if (modalApplyBtn) {
        modalApplyBtn.addEventListener('click', function() {
            const threadId = this.dataset.threadId;
            if (threadId) {
                applyTrainingToAutodev(threadId);
            }
        });
    }
    
    // Add event listeners for thread action buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-thread-btn')) {
            const threadId = e.target.dataset.threadId;
            showSessionDetails(threadId);
        } else if (e.target.classList.contains('apply-thread-btn')) {
            const threadId = e.target.dataset.threadId;
            applyTrainingToAutodev(threadId);
        }
    });
    
    // Poll for training updates
    function startPollingUpdates(sessionId) {
        // Initial status check
        fetchSessionStatus(sessionId);
        fetchTrainingUpdates();
        
        // Setup polling interval (every 5 seconds)
        const pollingInterval = setInterval(() => {
            fetchSessionStatus(sessionId);
            fetchTrainingUpdates();
        }, 5000);
        
        // Store interval ID to clear it later
        localStorage.setItem('pollingIntervalId', pollingInterval);
    }
    
    // Update current session UI
    function updateCurrentSessionUI(sessionData) {
        if (!currentSessionCard) return;
        
        // Display the session card
        currentSessionCard.style.display = 'block';
        
        // Update session information
        document.getElementById('session-topic').textContent = sessionData.topic || 'Unknown';
        document.getElementById('session-mode').textContent = sessionData.mode || 'Unknown';
        document.getElementById('session-platforms').textContent = 
            sessionData.platforms ? sessionData.platforms.join(', ') : 'All platforms';
        
        // Update status badge
        const statusBadge = document.getElementById('session-status');
        if (statusBadge) {
            statusBadge.textContent = capitalizeFirstLetter(sessionData.status || 'In Progress');
            
            // Update badge color
            statusBadge.className = 'badge';
            if (sessionData.status === 'completed') {
                statusBadge.classList.add('bg-success');
                // Enable apply button
                if (applyTrainingBtn) applyTrainingBtn.disabled = false;
            } else if (sessionData.status === 'failed') {
                statusBadge.classList.add('bg-danger');
            } else {
                statusBadge.classList.add('bg-primary');
            }
        }
        
        // Update progress
        if (sessionProgress) {
            const progressPercent = Math.min(100, Math.max(0, sessionData.progress || 0));
            sessionProgress.style.width = `${progressPercent}%`;
            sessionProgress.textContent = `${progressPercent}%`;
            sessionProgress.setAttribute('aria-valuenow', progressPercent);
        }
    }
    
    // Fetch session status
    function fetchSessionStatus(sessionId) {
        return fetch(`/api/training/status/${sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const sessionStatus = data.session_status;
                    
                    // Update UI with session status
                    updateCurrentSessionUI(sessionStatus);
                    
                    // Check if completed or failed to stop polling
                    if (sessionStatus.status === 'completed' || sessionStatus.status === 'failed') {
                        const intervalId = parseInt(localStorage.getItem('pollingIntervalId'));
                        if (intervalId) {
                            clearInterval(intervalId);
                            localStorage.removeItem('pollingIntervalId');
                        }
                        
                        // Refresh training history
                        refreshTrainingHistory();
                    }
                    
                    return sessionStatus;
                }
                return null;
            })
            .catch(error => {
                console.error('Error fetching session status:', error);
                return null;
            });
    }
    
    // Fetch training updates
    function fetchTrainingUpdates() {
        if (!trainingLogs) return;
        
        fetch('/api/training/updates')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.updates && data.updates.length > 0) {
                    updateTrainingLogs(data.updates);
                }
            })
            .catch(error => {
                console.error('Error fetching training updates:', error);
            });
    }
    
    // Update training logs in UI
    function updateTrainingLogs(updates) {
        if (!trainingLogs) return;
        
        trainingLogs.innerHTML = '';
        
        updates.forEach(update => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry mb-2';
            
            // Format timestamp
            const timestamp = new Date(update.timestamp);
            const timeStr = timestamp.toLocaleTimeString();
            
            // Style based on content
            let messageClass = '';
            if (update.message.includes('Error') || update.message.includes('❌')) {
                messageClass = 'text-danger';
            } else if (update.message.includes('✅')) {
                messageClass = 'text-success';
            } else if (update.message.includes('🔄')) {
                messageClass = 'text-info';
            } else if (update.message.includes('🧠')) {
                messageClass = 'text-warning';
            }
            
            logEntry.innerHTML = `
                <small class="text-muted">${timeStr}</small>
                <span class="${messageClass}">${update.message}</span>
            `;
            
            trainingLogs.appendChild(logEntry);
        });
        
        // Scroll to bottom
        trainingLogs.scrollTop = trainingLogs.scrollHeight;
    }
    
    // Show session details in modal
    function showSessionDetails(threadId) {
        const sessionDetailsModal = new bootstrap.Modal(document.getElementById('session-details-modal'));
        
        fetch(`/api/training/status/${threadId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const sessionData = data.session_status;
                    
                    // Populate modal
                    document.getElementById('detail-thread-id').textContent = threadId;
                    document.getElementById('detail-topic').textContent = sessionData.topic || 'N/A';
                    document.getElementById('detail-goal').textContent = sessionData.goal || 'N/A';
                    document.getElementById('detail-created').textContent = 
                        new Date(sessionData.timestamp || Date.now()).toLocaleString();
                    document.getElementById('detail-status').textContent = 
                        capitalizeFirstLetter(sessionData.status || 'N/A');
                    
                    // Final plan
                    const finalPlanEl = document.getElementById('detail-final-plan');
                    if (finalPlanEl) {
                        if (sessionData.recommendation && sessionData.recommendation.summary) {
                            finalPlanEl.innerHTML = `<p>${sessionData.recommendation.summary}</p>`;
                        } else if (sessionData.final_plan) {
                            finalPlanEl.innerHTML = `<p>${sessionData.final_plan}</p>`;
                        } else {
                            finalPlanEl.innerHTML = '<p class="text-muted">No final plan available</p>';
                        }
                    }
                    
                    // AI Contributions
                    const contributionsEl = document.getElementById('detail-contributions');
                    if (contributionsEl) {
                        if (sessionData.recommendation && sessionData.recommendation.insights) {
                            const insights = sessionData.recommendation.insights;
                            contributionsEl.innerHTML = '<ul class="list-unstyled">';
                            insights.forEach(insight => {
                                contributionsEl.innerHTML += `<li><strong>${insight.platform}:</strong> ${insight.insight}</li>`;
                            });
                            contributionsEl.innerHTML += '</ul>';
                        } else {
                            contributionsEl.innerHTML = '<p class="text-muted">No AI contributions available</p>';
                        }
                    }
                    
                    // Conversations
                    const conversationsEl = document.getElementById('detail-conversations');
                    if (conversationsEl) {
                        if (sessionData.conversations && sessionData.conversations.length > 0) {
                            conversationsEl.innerHTML = '';
                            sessionData.conversations.forEach(convId => {
                                conversationsEl.innerHTML += `
                                    <tr>
                                        <td>${convId}</td>
                                        <td>Unknown</td>
                                        <td>Unknown</td>
                                        <td><a href="/logs?conversation=${convId}" class="btn btn-sm btn-outline-info" target="_blank">View</a></td>
                                    </tr>
                                `;
                            });
                        } else {
                            conversationsEl.innerHTML = '<tr><td colspan="4" class="text-center">No conversations associated</td></tr>';
                        }
                    }
                    
                    // Set thread ID for apply button
                    if (modalApplyBtn) {
                        modalApplyBtn.dataset.threadId = threadId;
                    }
                    
                    // Show modal
                    sessionDetailsModal.show();
                } else {
                    showError('Failed to load session details');
                }
            })
            .catch(error => {
                console.error('Error loading session details:', error);
                showError('An error occurred while loading session details');
            });
    }
    
    // Apply training to AutoDev
    function applyTrainingToAutodev(threadId) {
        fetch('/api/autodev/apply_training', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({thread_id: threadId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showSuccess('Training applied to AutoDev successfully!');
                
                // Close modal if open
                const sessionDetailsModal = bootstrap.Modal.getInstance(document.getElementById('session-details-modal'));
                if (sessionDetailsModal) {
                    sessionDetailsModal.hide();
                }
            } else {
                showError(data.message || 'Failed to apply training to AutoDev');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while applying training to AutoDev');
        });
    }
    
    // Refresh training history
    function refreshTrainingHistory() {
        // In a real implementation, this would fetch the latest training threads
        // and update the table. For simplicity, we'll just update the UI to show success.
        const historyTable = document.getElementById('training-history');
        if (historyTable) {
            const sessionId = localStorage.getItem('currentTrainingSession');
            if (!sessionId) return;
            
            // Check if this thread is already in the table
            const existingRow = historyTable.querySelector(`[data-thread-id="${sessionId}"]`);
            if (existingRow) {
                // Update the status cell
                const statusCell = existingRow.querySelector('td:nth-child(4)');
                if (statusCell) {
                    statusCell.textContent = 'Completed';
                }
                return;
            }
            
            // Add a new row for this thread
            const newRow = document.createElement('tr');
            newRow.setAttribute('data-thread-id', sessionId);
            newRow.innerHTML = `
                <td>${sessionId}</td>
                <td>${document.getElementById('session-topic').textContent}</td>
                <td>${new Date().toLocaleString()}</td>
                <td>Completed</td>
                <td>
                    <button class="btn btn-sm btn-outline-info view-thread-btn" data-thread-id="${sessionId}">Details</button>
                    <button class="btn btn-sm btn-outline-success apply-thread-btn" data-thread-id="${sessionId}">Apply</button>
                </td>
            `;
            
            // Add to the top of the table
            const tbody = historyTable.querySelector('tbody') || historyTable;
            const firstRow = tbody.querySelector('tr');
            if (firstRow) {
                tbody.insertBefore(newRow, firstRow);
            } else {
                tbody.appendChild(newRow);
            }
        }
    }
    
    // Helper function to show success message
    function showSuccess(message) {
        const successToast = new bootstrap.Toast(document.getElementById('success-toast'));
        document.getElementById('success-message').textContent = message;
        successToast.show();
    }
    
    // Helper function to show error message
    function showError(message) {
        const errorToast = new bootstrap.Toast(document.getElementById('error-toast'));
        document.getElementById('error-message').textContent = message;
        errorToast.show();
    }
    
    // Helper function to capitalize first letter
    function capitalizeFirstLetter(string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});