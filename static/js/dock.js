// Dock system for Synapse Chamber

document.addEventListener('DOMContentLoaded', function() {
  initializeDock();
  initializeFileTree();
  initializeTools();
  initializeAgent();
  bindEventListeners();
});

// Dock Initialization
function initializeDock() {
  const dockContainer = document.getElementById('dockContainer');
  const dockCollapseBtn = document.getElementById('dockCollapseBtn');
  const dockToggleBtn = document.getElementById('dockToggleBtn');
  const mainContainer = document.querySelector('body');
  
  // Initialize dock state
  const isDockCollapsed = localStorage.getItem('dockCollapsed') === 'true';
  if (isDockCollapsed) {
    dockContainer.classList.add('dock-collapsed');
    dockToggleBtn.style.display = 'block';
    mainContainer.classList.add('dock-collapsed');
    mainContainer.classList.remove('dock-active');
  } else {
    dockContainer.classList.remove('dock-collapsed');
    dockToggleBtn.style.display = 'none';
    mainContainer.classList.add('dock-active');
    mainContainer.classList.remove('dock-collapsed');
  }
  
  // Collapse button click
  dockCollapseBtn.addEventListener('click', function() {
    dockContainer.classList.add('dock-collapsed');
    dockToggleBtn.style.display = 'block';
    mainContainer.classList.add('dock-collapsed');
    mainContainer.classList.remove('dock-active');
    localStorage.setItem('dockCollapsed', 'true');
  });
  
  // Toggle button click
  dockToggleBtn.addEventListener('click', function() {
    dockContainer.classList.remove('dock-collapsed');
    dockToggleBtn.style.display = 'none';
    mainContainer.classList.add('dock-active');
    mainContainer.classList.remove('dock-collapsed');
    localStorage.setItem('dockCollapsed', 'false');
  });
  
  // Create overlay for mobile
  const overlay = document.createElement('div');
  overlay.className = 'dock-overlay';
  document.body.appendChild(overlay);
  
  // Close dock when overlay is clicked
  overlay.addEventListener('click', function() {
    dockContainer.classList.add('dock-collapsed');
    dockToggleBtn.style.display = 'block';
    mainContainer.classList.add('dock-collapsed');
    mainContainer.classList.remove('dock-active');
    localStorage.setItem('dockCollapsed', 'true');
  });
}

// File Tree Initialization
function initializeFileTree() {
  const fileTree = document.getElementById('fileTree');
  if (!fileTree) return;
  
  // Clear loading indicator
  fileTree.innerHTML = '';
  
  // Fetch file list from server 
  fetchFileList();
}

// Fetch file list from server
function fetchFileList() {
  fetch('/api/files/list')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch file list');
      }
      return response.json();
    })
    .then(data => {
      renderFileTree(data.files);
    })
    .catch(error => {
      console.error('Error loading file list:', error);
      // Show error in file tree
      const fileTree = document.getElementById('fileTree');
      fileTree.innerHTML = `
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-circle"></i> 
          Failed to load files. <button class="btn btn-sm btn-outline-danger" onclick="fetchFileList()">Retry</button>
        </div>
      `;
      
      // In development, render some dummy files so UI can be tested
      if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        renderDummyFileTree();
      }
    });
}

// Render file tree from data
function renderFileTree(files) {
  const fileTree = document.getElementById('fileTree');
  fileTree.innerHTML = '';
  
  // Sort items: directories first, then files
  files.sort((a, b) => {
    if (a.type === 'dir' && b.type !== 'dir') return -1;
    if (a.type !== 'dir' && b.type === 'dir') return 1;
    return a.name.localeCompare(b.name);
  });
  
  // Create tree items for each file
  files.forEach(file => {
    const item = createTreeItem(file);
    fileTree.appendChild(item);
  });
}

// Create tree item element
function createTreeItem(file, level = 0) {
  const item = document.createElement('div');
  item.className = 'tree-item';
  item.dataset.path = file.path;
  item.dataset.type = file.type;
  
  // Icon based on file type
  let icon;
  if (file.type === 'dir') {
    icon = '<i class="fas fa-folder folder-icon"></i>';
    item.addEventListener('click', function(e) {
      e.stopPropagation();
      toggleFolder(this);
    });
  } else {
    // Different icons based on file extension
    const extension = file.name.split('.').pop().toLowerCase();
    if (['py', 'js', 'html', 'css', 'json'].includes(extension)) {
      icon = `<i class="fas fa-code code-icon"></i>`;
    } else if (['md', 'txt'].includes(extension)) {
      icon = `<i class="fas fa-file-alt file-icon"></i>`;
    } else if (['jpg', 'png', 'gif', 'svg'].includes(extension)) {
      icon = `<i class="fas fa-image file-icon"></i>`;
    } else {
      icon = `<i class="fas fa-file file-icon"></i>`;
    }
    
    item.addEventListener('click', function(e) {
      e.stopPropagation();
      openFile(this.dataset.path);
    });
  }
  
  // Item content
  item.innerHTML = `
    ${icon}
    <span>${file.name}</span>
  `;
  
  // If this is a directory, add children container
  if (file.type === 'dir' && file.children && file.children.length > 0) {
    const childrenContainer = document.createElement('div');
    childrenContainer.className = 'tree-children';
    childrenContainer.style.display = 'none'; // Initially collapsed
    
    // Sort children: directories first, then files
    file.children.sort((a, b) => {
      if (a.type === 'dir' && b.type !== 'dir') return -1;
      if (a.type !== 'dir' && b.type === 'dir') return 1;
      return a.name.localeCompare(b.name);
    });
    
    // Add children
    file.children.forEach(child => {
      const childItem = createTreeItem(child, level + 1);
      childrenContainer.appendChild(childItem);
    });
    
    // Add dropdown icon
    const dropdownIcon = document.createElement('i');
    dropdownIcon.className = 'fas fa-caret-right';
    dropdownIcon.style.marginRight = '5px';
    item.insertBefore(dropdownIcon, item.firstChild);
    
    // Add to parent
    const wrapper = document.createElement('div');
    wrapper.appendChild(item);
    wrapper.appendChild(childrenContainer);
    return wrapper;
  }
  
  return item;
}

// Toggle folder open/closed state
function toggleFolder(folderItem) {
  // Find the children container
  const wrapper = folderItem.parentElement;
  const childrenContainer = wrapper.querySelector('.tree-children');
  if (!childrenContainer) return;
  
  // Toggle display
  if (childrenContainer.style.display === 'none') {
    childrenContainer.style.display = 'block';
    // Change folder icon to open
    folderItem.querySelector('.fa-folder').classList.replace('fa-folder', 'fa-folder-open');
    // Change dropdown icon
    folderItem.querySelector('.fa-caret-right').classList.replace('fa-caret-right', 'fa-caret-down');
  } else {
    childrenContainer.style.display = 'none';
    // Change folder icon to closed
    folderItem.querySelector('.fa-folder-open').classList.replace('fa-folder-open', 'fa-folder');
    // Change dropdown icon
    folderItem.querySelector('.fa-caret-down').classList.replace('fa-caret-down', 'fa-caret-right');
  }
}

// Open a file
function openFile(filePath) {
  // Clear any active items
  document.querySelectorAll('.tree-item.active').forEach(item => {
    item.classList.remove('active');
  });
  
  // Set this item as active
  document.querySelector(`.tree-item[data-path="${filePath}"]`).classList.add('active');
  
  // Fetch and open the file content
  fetch(`/api/files/open?path=${encodeURIComponent(filePath)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to open file');
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        // Open file in editor
        openFileInEditor(filePath, data.content, data.language);
      } else {
        showNotification('error', data.message || 'Failed to open file');
      }
    })
    .catch(error => {
      console.error('Error opening file:', error);
      showNotification('error', 'Failed to open file: ' + error.message);
    });
}

// Open file in editor
function openFileInEditor(filePath, content, language) {
  // This would integrate with your code editor component
  // For now, show a placeholder message
  showNotification('info', `Opening ${filePath}...`);
  
  // In an actual implementation, you would update the editor
  // console.log('File content:', content);
  // console.log('Language:', language);
}

// Initialize tools tab
function initializeTools() {
  // Add click handlers for tool items
  document.querySelectorAll('.tool-item').forEach(item => {
    item.addEventListener('click', function() {
      const tool = this.dataset.tool;
      openTool(tool);
    });
  });
}

// Open a tool
function openTool(toolId) {
  // Clear any active tool items
  document.querySelectorAll('.tool-item.active').forEach(item => {
    item.classList.remove('active');
  });
  
  // Set this tool as active
  document.querySelector(`.tool-item[data-tool="${toolId}"]`).classList.add('active');
  
  // Handle different tools
  switch (toolId) {
    case 'code-editor':
      window.location.href = '/editor';
      break;
    case 'terminal':
      window.location.href = '/terminal';
      break;
    case 'debug':
      window.location.href = '/debug';
      break;
    case 'training-session':
      window.location.href = '/training';
      break;
    case 'memory-explorer':
      window.location.href = '/memory';
      break;
    case 'platform-manager':
      window.location.href = '/platforms';
      break;
    case 'analytics':
      window.location.href = '/dashboard';
      break;
    case 'logs':
      window.location.href = '/logs';
      break;
    case 'performance':
      window.location.href = '/performance';
      break;
    default:
      showNotification('info', `Opening tool: ${toolId}...`);
  }
}

// Initialize agent tab
function initializeAgent() {
  fetchAgentStatus();
  fetchAgentProjects();
  fetchFeedbackRequests();
  
  // Set up event listeners
  document.getElementById('newProjectBtn').addEventListener('click', function() {
    // Show new project modal
    const newProjectModal = new bootstrap.Modal(document.getElementById('newProjectModal'));
    newProjectModal.show();
  });
  
  document.getElementById('continueProjectBtn').addEventListener('click', function() {
    // Show project selection dialog
    fetchAgentProjects(true);
  });
  
  document.getElementById('pauseAgentBtn').addEventListener('click', function() {
    // Pause agent
    pauseAgent();
  });
  
  // Set up new project form submission
  document.getElementById('startProjectBtn').addEventListener('click', function() {
    createNewProject();
  });
}

// Fetch agent status
function fetchAgentStatus() {
  fetch('/api/agent/status')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch agent status');
      }
      return response.json();
    })
    .then(data => {
      updateAgentStatus(data);
    })
    .catch(error => {
      console.error('Error fetching agent status:', error);
      
      // For initial development, show placeholder status
      const placeholderStatus = {
        is_running: true,
        current_project: {
          description: 'Sample Project',
          status: 'in_progress',
          completion_percentage: 45
        }
      };
      updateAgentStatus(placeholderStatus);
    });
}

// Update agent status display
function updateAgentStatus(status) {
  const statusBadge = document.getElementById('agentStatusBadge');
  const progressBar = document.getElementById('agentProgressBar');
  const statusText = document.getElementById('agentStatusText');
  
  // Update status badge
  if (status.is_running) {
    statusBadge.innerText = 'Active';
    statusBadge.className = 'badge bg-success';
  } else {
    statusBadge.innerText = 'Paused';
    statusBadge.className = 'badge bg-warning';
  }
  
  // Update progress if there's a current project
  if (status.current_project) {
    const project = status.current_project;
    progressBar.style.width = `${project.completion_percentage}%`;
    statusText.innerText = `Working on: ${project.description.substring(0, 30)}...`;
    
    // Adjust progress bar color based on status
    if (project.status === 'completed') {
      progressBar.className = 'progress-bar bg-success';
    } else if (project.status === 'failed') {
      progressBar.className = 'progress-bar bg-danger';
    } else {
      progressBar.className = 'progress-bar bg-primary';
    }
  } else {
    progressBar.style.width = '0%';
    statusText.innerText = 'No active project';
  }
}

// Fetch agent projects
function fetchAgentProjects(showSelectionModal = false) {
  fetch('/api/agent/projects')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch agent projects');
      }
      return response.json();
    })
    .then(data => {
      updateProjectsList(data.projects);
      
      if (showSelectionModal) {
        showProjectSelectionModal(data.projects);
      }
    })
    .catch(error => {
      console.error('Error fetching agent projects:', error);
      
      // For initial development, show placeholder projects
      const placeholderProjects = [
        {
          id: 'project_1',
          description: 'Web Dashboard Application',
          status: 'in_progress',
          completion_percentage: 70
        },
        {
          id: 'project_2',
          description: 'API Integration Module',
          status: 'completed',
          completion_percentage: 100
        }
      ];
      
      updateProjectsList(placeholderProjects);
      
      if (showSelectionModal) {
        showProjectSelectionModal(placeholderProjects);
      }
    });
}

// Update projects list
function updateProjectsList(projects) {
  const projectsList = document.getElementById('recentProjectsList');
  projectsList.innerHTML = '';
  
  if (projects.length === 0) {
    projectsList.innerHTML = '<div class="list-group-item text-muted">No projects found</div>';
    return;
  }
  
  projects.forEach(project => {
    const item = document.createElement('div');
    item.className = 'list-group-item';
    item.innerHTML = `
      <div class="d-flex justify-content-between align-items-center">
        <span class="text-truncate" title="${project.description}">${project.description.substring(0, 25)}${project.description.length > 25 ? '...' : ''}</span>
        <span class="badge ${getBadgeClassForStatus(project.status)}">${project.completion_percentage}%</span>
      </div>
    `;
    
    // Add click event to open project details
    item.addEventListener('click', function() {
      showProjectDetails(project.id);
    });
    
    projectsList.appendChild(item);
  });
}

// Show project selection modal
function showProjectSelectionModal(projects) {
  // Create modal dynamically
  let modalHtml = `
    <div class="modal fade" id="projectSelectionModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content bg-dark">
          <div class="modal-header">
            <h5 class="modal-title">Select Project to Continue</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="list-group">
  `;
  
  projects.forEach(project => {
    modalHtml += `
      <button type="button" class="list-group-item list-group-item-action bg-dark text-light border-secondary" 
              onclick="continueProject('${project.id}')">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-1">${project.description.substring(0, 40)}${project.description.length > 40 ? '...' : ''}</h6>
            <small class="text-muted">Status: ${project.status}</small>
          </div>
          <span class="badge ${getBadgeClassForStatus(project.status)}">${project.completion_percentage}%</span>
        </div>
      </button>
    `;
  });
  
  modalHtml += `
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to DOM
  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = modalHtml;
  document.body.appendChild(modalContainer);
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('projectSelectionModal'));
  modal.show();
  
  // Remove modal from DOM after it's hidden
  document.getElementById('projectSelectionModal').addEventListener('hidden.bs.modal', function() {
    document.body.removeChild(modalContainer);
  });
}

// Continue a specific project
function continueProject(projectId) {
  // Close the modal
  bootstrap.Modal.getInstance(document.getElementById('projectSelectionModal')).hide();
  
  // Make API call to continue project
  fetch('/api/agent/continue', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      project_id: projectId
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to continue project');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'Project resumed successfully');
      fetchAgentStatus();
    } else {
      showNotification('error', data.message || 'Failed to resume project');
    }
  })
  .catch(error => {
    console.error('Error continuing project:', error);
    showNotification('error', 'Failed to resume project: ' + error.message);
  });
}

// Pause agent
function pauseAgent() {
  fetch('/api/agent/pause', {
    method: 'POST'
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to pause agent');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'Agent paused successfully');
      fetchAgentStatus();
    } else {
      showNotification('error', data.message || 'Failed to pause agent');
    }
  })
  .catch(error => {
    console.error('Error pausing agent:', error);
    showNotification('error', 'Failed to pause agent: ' + error.message);
  });
}

// Create new project
function createNewProject() {
  const description = document.getElementById('projectDescription').value;
  if (!description) {
    showNotification('warning', 'Please provide a project description');
    return;
  }
  
  // Gather preferences
  const preferences = {
    use_flask: document.getElementById('prefPythonFramework').checked,
    include_database: document.getElementById('prefDatabase').checked,
    include_testing: document.getElementById('prefTesting').checked,
    include_documentation: document.getElementById('prefDocumentation').checked
  };
  
  // Close modal
  bootstrap.Modal.getInstance(document.getElementById('newProjectModal')).hide();
  
  // Make API call to create project
  fetch('/api/agent/create_project', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      description: description,
      preferences: preferences
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to create project');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'Project created successfully');
      fetchAgentStatus();
      fetchAgentProjects();
    } else {
      showNotification('error', data.message || 'Failed to create project');
    }
  })
  .catch(error => {
    console.error('Error creating project:', error);
    showNotification('error', 'Failed to create project: ' + error.message);
  });
}

// Fetch feedback requests
function fetchFeedbackRequests() {
  fetch('/api/agent/feedback_requests?status=pending')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch feedback requests');
      }
      return response.json();
    })
    .then(data => {
      updateFeedbackDisplay(data.requests);
    })
    .catch(error => {
      console.error('Error fetching feedback requests:', error);
      
      // For initial development, check if we should show a placeholder request
      const shouldShowPlaceholder = Math.random() > 0.7; // 30% chance
      if (shouldShowPlaceholder) {
        const placeholderRequest = {
          id: 'feedback_123',
          message: 'I\'ve created a plan for your project. Please review and let me know if you\'d like to make any changes.',
          context: {
            type: 'project_plan',
            project_id: 'project_123',
            plan: [
              {
                title: 'Initialize project structure',
                description: 'Create basic directory structure'
              },
              {
                title: 'Setup dependencies',
                description: 'Install required packages'
              }
            ]
          }
        };
        updateFeedbackDisplay([placeholderRequest]);
      } else {
        updateFeedbackDisplay([]);
      }
    });
}

// Update feedback display
function updateFeedbackDisplay(requests) {
  const feedbackMessage = document.getElementById('feedbackMessage');
  const feedbackActions = document.getElementById('feedbackActions');
  
  if (requests.length === 0) {
    feedbackMessage.innerText = 'No pending feedback requests.';
    feedbackActions.style.display = 'none';
    return;
  }
  
  // Show the latest request
  const latestRequest = requests[0];
  feedbackMessage.innerText = latestRequest.message;
  feedbackActions.style.display = 'block';
  
  // Store the request ID for action buttons
  document.getElementById('acceptFeedbackBtn').dataset.requestId = latestRequest.id;
  document.getElementById('rejectFeedbackBtn').dataset.requestId = latestRequest.id;
  document.getElementById('modifyFeedbackBtn').dataset.requestId = latestRequest.id;
  
  // Add context data for reference
  feedbackMessage.dataset.context = JSON.stringify(latestRequest.context);
  
  // Set up event listeners for feedback buttons
  document.getElementById('acceptFeedbackBtn').addEventListener('click', function() {
    showFeedbackDetailModal(latestRequest, 'accept');
  });
  
  document.getElementById('rejectFeedbackBtn').addEventListener('click', function() {
    showFeedbackDetailModal(latestRequest, 'reject');
  });
  
  document.getElementById('modifyFeedbackBtn').addEventListener('click', function() {
    showFeedbackDetailModal(latestRequest, 'modify');
  });
}

// Show feedback detail modal
function showFeedbackDetailModal(request, action) {
  const feedbackModal = document.getElementById('feedbackModal');
  const feedbackContent = document.getElementById('feedbackContent');
  const feedbackResponseContainer = document.getElementById('feedbackResponseContainer');
  const feedbackResponse = document.getElementById('feedbackResponse');
  const feedbackModalActions = document.getElementById('feedbackModalActions');
  
  // Set modal title based on context type
  const modalTitle = feedbackModal.querySelector('.modal-title');
  const contextType = request.context.type;
  if (contextType === 'project_plan') {
    modalTitle.innerText = 'Review Project Plan';
  } else if (contextType === 'step_failure') {
    modalTitle.innerText = 'Step Failed - Feedback Needed';
  } else if (contextType === 'code_feedback') {
    modalTitle.innerText = 'Review Generated Code';
  } else {
    modalTitle.innerText = 'Agent Feedback';
  }
  
  // Prepare content based on context type
  let contentHtml = '';
  
  if (contextType === 'project_plan') {
    contentHtml = `
      <div class="mb-3">
        <h6>Project Description</h6>
        <p>${request.context.project_id}</p>
      </div>
      <div class="mb-3">
        <h6>Proposed Plan</h6>
        <ol class="list-group list-group-numbered">
    `;
    
    request.context.plan.forEach(step => {
      contentHtml += `
        <li class="list-group-item bg-dark border-secondary">
          <strong>${step.title}</strong>
          <p class="mb-0 small">${step.description}</p>
        </li>
      `;
    });
    
    contentHtml += `
        </ol>
      </div>
    `;
    
    // Different actions based on action type
    if (action === 'accept') {
      feedbackResponseContainer.style.display = 'none';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-success" onclick="submitFeedbackResponse('${request.id}', 'confirm')">
          Accept Plan
        </button>
      `;
    } else if (action === 'reject') {
      feedbackResponseContainer.style.display = 'block';
      feedbackResponse.placeholder = 'Please explain why you are rejecting the plan...';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-danger" onclick="submitFeedbackResponse('${request.id}', 'restart')">
          Request New Plan
        </button>
      `;
    } else if (action === 'modify') {
      // For modify, we would need a more complex UI to edit the plan
      // For now, just allow text feedback
      feedbackResponseContainer.style.display = 'block';
      feedbackResponse.placeholder = 'Please describe your suggested modifications...';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" onclick="submitFeedbackResponse('${request.id}', 'modify')">
          Submit Modifications
        </button>
      `;
    }
  } else if (contextType === 'step_failure') {
    const step = request.context.step;
    
    contentHtml = `
      <div class="alert alert-danger">
        <i class="fas fa-exclamation-circle"></i> Step Failed: ${step.title}
      </div>
      <div class="mb-3">
        <h6>Step Details</h6>
        <div class="card bg-dark border-secondary mb-3">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Step ${step.index + 1}: ${step.type}</h6>
            <p class="card-text">${step.description}</p>
            <div class="small">
              <div><strong>Files:</strong> ${step.files.join(', ') || 'None'}</div>
              <div><strong>Dependencies:</strong> ${step.dependencies.join(', ') || 'None'}</div>
              <div><strong>Commands:</strong> ${step.commands.join(', ') || 'None'}</div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Different actions based on action type
    if (action === 'accept') {
      feedbackResponseContainer.style.display = 'none';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-success" onclick="submitFeedbackResponse('${request.id}', 'retry', {step_index: ${step.index}})">
          Retry Step
        </button>
      `;
    } else if (action === 'reject') {
      feedbackResponseContainer.style.display = 'none';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-danger" onclick="submitFeedbackResponse('${request.id}', 'skip', {step_index: ${step.index}})">
          Skip Step
        </button>
      `;
    } else if (action === 'modify') {
      feedbackResponseContainer.style.display = 'block';
      feedbackResponse.placeholder = 'Please describe how to modify this step...';
      feedbackModalActions.innerHTML = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" onclick="submitFeedbackResponse('${request.id}', 'modify', {step_index: ${step.index}})">
          Submit Modifications
        </button>
      `;
    }
  } else {
    contentHtml = `
      <div class="mb-3">
        <h6>Feedback Request</h6>
        <p>${request.message}</p>
      </div>
    `;
    
    // Generic actions
    feedbackResponseContainer.style.display = 'block';
    feedbackResponse.placeholder = 'Your response...';
    feedbackModalActions.innerHTML = `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      <button type="button" class="btn btn-primary" onclick="submitFeedbackResponse('${request.id}', 'response')">
        Submit Response
      </button>
    `;
  }
  
  feedbackContent.innerHTML = contentHtml;
  
  // Show the modal
  const modal = new bootstrap.Modal(feedbackModal);
  modal.show();
}

// Submit feedback response
function submitFeedbackResponse(requestId, action, params = {}) {
  // Get response text if needed
  let responseText = '';
  if (document.getElementById('feedbackResponseContainer').style.display !== 'none') {
    responseText = document.getElementById('feedbackResponse').value;
    
    // Check if response is required
    if (!responseText && (action === 'modify' || action === 'response')) {
      showNotification('warning', 'Please provide a response');
      return;
    }
  }
  
  // Prepare response data
  const responseData = {
    type: document.querySelector('#feedbackContent h6')?.textContent.toLowerCase().replace(' ', '_') || 'general',
    action: action,
    response: responseText,
    ...params
  };
  
  // Close the modal
  bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
  
  // Make API call to submit feedback
  fetch(`/api/agent/provide_feedback/${requestId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(responseData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to submit feedback');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'Feedback submitted successfully');
      // Refresh feedback and status
      fetchFeedbackRequests();
      fetchAgentStatus();
    } else {
      showNotification('error', data.message || 'Failed to submit feedback');
    }
  })
  .catch(error => {
    console.error('Error submitting feedback:', error);
    showNotification('error', 'Failed to submit feedback: ' + error.message);
    
    // For development, still clear the feedback
    fetchFeedbackRequests();
  });
}

// Global event bindings
function bindEventListeners() {
  // File system actions
  document.getElementById('newFileBtn').addEventListener('click', function() {
    // Show new file modal
    const newFileModal = new bootstrap.Modal(document.getElementById('newFileModal'));
    newFileModal.show();
  });
  
  document.getElementById('newFolderBtn').addEventListener('click', function() {
    // Show new folder modal
    const newFolderModal = new bootstrap.Modal(document.getElementById('newFolderModal'));
    newFolderModal.show();
  });
  
  document.getElementById('createFileBtn').addEventListener('click', function() {
    createNewFile();
  });
  
  document.getElementById('createFolderBtn').addEventListener('click', function() {
    createNewFolder();
  });
  
  // File search
  document.getElementById('fileSearchBtn').addEventListener('click', function() {
    searchFiles();
  });
  
  document.getElementById('fileSearchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      searchFiles();
    }
  });
}

// Create new file
function createNewFile() {
  const fileName = document.getElementById('newFileName').value;
  const filePath = document.getElementById('newFilePath').value;
  const fileType = document.getElementById('newFileType').value;
  
  if (!fileName) {
    showNotification('warning', 'Please provide a file name');
    return;
  }
  
  // Close modal
  bootstrap.Modal.getInstance(document.getElementById('newFileModal')).hide();
  
  // Construct full path
  let fullPath = filePath;
  if (fullPath && !fullPath.endsWith('/')) {
    fullPath += '/';
  }
  fullPath += fileName;
  
  // If no extension, add one based on type
  if (!fileName.includes('.')) {
    switch (fileType) {
      case 'python':
        fullPath += '.py';
        break;
      case 'html':
        fullPath += '.html';
        break;
      case 'css':
        fullPath += '.css';
        break;
      case 'javascript':
        fullPath += '.js';
        break;
      case 'json':
        fullPath += '.json';
        break;
      case 'text':
        fullPath += '.txt';
        break;
      case 'markdown':
        fullPath += '.md';
        break;
    }
  }
  
  // Make API call to create file
  fetch('/api/files/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      path: fullPath,
      content: ''
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to create file');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'File created successfully');
      fetchFileList();
      
      // Open the file
      openFile(fullPath);
    } else {
      showNotification('error', data.message || 'Failed to create file');
    }
  })
  .catch(error => {
    console.error('Error creating file:', error);
    showNotification('error', 'Failed to create file: ' + error.message);
  });
}

// Create new folder
function createNewFolder() {
  const folderName = document.getElementById('newFolderName').value;
  const folderPath = document.getElementById('newFolderPath').value;
  
  if (!folderName) {
    showNotification('warning', 'Please provide a folder name');
    return;
  }
  
  // Close modal
  bootstrap.Modal.getInstance(document.getElementById('newFolderModal')).hide();
  
  // Construct full path
  let fullPath = folderPath;
  if (fullPath && !fullPath.endsWith('/')) {
    fullPath += '/';
  }
  fullPath += folderName;
  
  // Make API call to create folder
  fetch('/api/files/create_folder', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      path: fullPath
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to create folder');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      showNotification('success', 'Folder created successfully');
      fetchFileList();
    } else {
      showNotification('error', data.message || 'Failed to create folder');
    }
  })
  .catch(error => {
    console.error('Error creating folder:', error);
    showNotification('error', 'Failed to create folder: ' + error.message);
  });
}

// Search files
function searchFiles() {
  const searchTerm = document.getElementById('fileSearchInput').value;
  if (!searchTerm) {
    fetchFileList();
    return;
  }
  
  // Make API call to search files
  fetch(`/api/files/search?query=${encodeURIComponent(searchTerm)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to search files');
      }
      return response.json();
    })
    .then(data => {
      renderFileTree(data.files);
    })
    .catch(error => {
      console.error('Error searching files:', error);
      showNotification('error', 'Failed to search files: ' + error.message);
    });
}

// Show project details
function showProjectDetails(projectId) {
  fetch(`/api/agent/project_details/${projectId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch project details');
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        showProjectDetailsModal(data.project);
      } else {
        showNotification('error', data.message || 'Failed to fetch project details');
      }
    })
    .catch(error => {
      console.error('Error fetching project details:', error);
      showNotification('error', 'Failed to fetch project details: ' + error.message);
    });
}

// Show project details modal
function showProjectDetailsModal(project) {
  // Create modal HTML
  let modalHtml = `
    <div class="modal fade" id="projectDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content bg-dark">
          <div class="modal-header">
            <h5 class="modal-title">Project Details</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6>Description</h6>
              <p>${project.description}</p>
            </div>
            <div class="mb-3">
              <h6>Status</h6>
              <div class="d-flex align-items-center">
                <div class="progress flex-grow-1 bg-dark">
                  <div class="progress-bar ${getBadgeClassForStatus(project.status)}" style="width: ${project.completion_percentage}%"></div>
                </div>
                <span class="ms-2">${project.completion_percentage}%</span>
              </div>
              <small class="text-muted">Status: ${project.status}</small>
            </div>
            <div class="mb-3">
              <h6>Plan</h6>
              <div class="list-group list-group-flush">
  `;
  
  project.plan.forEach((step, index) => {
    let statusBadge = '';
    if (step.status === 'completed') {
      statusBadge = '<span class="badge bg-success">Completed</span>';
    } else if (step.status === 'in_progress') {
      statusBadge = '<span class="badge bg-primary">In Progress</span>';
    } else if (step.status === 'failed') {
      statusBadge = '<span class="badge bg-danger">Failed</span>';
    } else if (step.status === 'skipped') {
      statusBadge = '<span class="badge bg-warning">Skipped</span>';
    } else {
      statusBadge = '<span class="badge bg-secondary">Pending</span>';
    }
    
    modalHtml += `
      <div class="list-group-item bg-dark border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <span>${index + 1}. ${step.title}</span>
          ${statusBadge}
        </div>
        <p class="mb-0 small">${step.description}</p>
      </div>
    `;
  });
  
  modalHtml += `
              </div>
            </div>
  `;
  
  // Add files section if there are files
  if (project.generated_files.length > 0 || project.modified_files.length > 0) {
    modalHtml += `
            <div class="mb-3">
              <h6>Files</h6>
              <div class="row">
                <div class="col-md-6">
                  <h6 class="small">Generated Files</h6>
                  <ul class="list-group list-group-flush">
    `;
    
    if (project.generated_files.length === 0) {
      modalHtml += `<li class="list-group-item bg-dark border-secondary text-muted">No files generated yet</li>`;
    } else {
      project.generated_files.forEach(file => {
        modalHtml += `
          <li class="list-group-item bg-dark border-secondary d-flex justify-content-between align-items-center">
            <span>${file}</span>
            <button class="btn btn-sm btn-outline-info" onclick="openFile('${file}')">
              <i class="fas fa-eye"></i>
            </button>
          </li>
        `;
      });
    }
    
    modalHtml += `
                  </ul>
                </div>
                <div class="col-md-6">
                  <h6 class="small">Modified Files</h6>
                  <ul class="list-group list-group-flush">
    `;
    
    if (project.modified_files.length === 0) {
      modalHtml += `<li class="list-group-item bg-dark border-secondary text-muted">No files modified yet</li>`;
    } else {
      project.modified_files.forEach(file => {
        modalHtml += `
          <li class="list-group-item bg-dark border-secondary d-flex justify-content-between align-items-center">
            <span>${file}</span>
            <button class="btn btn-sm btn-outline-info" onclick="openFile('${file}')">
              <i class="fas fa-eye"></i>
            </button>
          </li>
        `;
      });
    }
    
    modalHtml += `
                  </ul>
                </div>
              </div>
            </div>
    `;
  }
  
  modalHtml += `
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" onclick="continueProject('${project.id}')">Continue Project</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to DOM
  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = modalHtml;
  document.body.appendChild(modalContainer);
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('projectDetailsModal'));
  modal.show();
  
  // Remove modal from DOM after it's hidden
  document.getElementById('projectDetailsModal').addEventListener('hidden.bs.modal', function() {
    document.body.removeChild(modalContainer);
  });
}

// Helper function to get badge class based on status
function getBadgeClassForStatus(status) {
  switch (status) {
    case 'completed':
      return 'bg-success';
    case 'in_progress':
      return 'bg-primary';
    case 'failed':
      return 'bg-danger';
    case 'planning':
      return 'bg-info';
    default:
      return 'bg-secondary';
  }
}

// Show notification
function showNotification(type, message) {
  // Check if we have the notification container
  let container = document.getElementById('notificationContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notificationContainer';
    container.className = 'notification-container';
    document.body.appendChild(container);
    
    // Add styles for the container
    const style = document.createElement('style');
    style.textContent = `
      .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
      }
      .notification {
        padding: 15px 20px;
        margin-bottom: 10px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 300px;
        max-width: 400px;
        opacity: 0;
        transform: translateY(-20px) translateX(20px);
        transition: opacity 0.3s, transform 0.3s;
      }
      .notification.show {
        opacity: 1;
        transform: translateY(0) translateX(0);
      }
      .notification-success { background-color: #28a745; }
      .notification-error { background-color: #dc3545; }
      .notification-warning { background-color: #ffc107; color: #212529; }
      .notification-info { background-color: #17a2b8; }
      .notification .close-btn {
        background: none;
        border: none;
        color: inherit;
        font-size: 16px;
        cursor: pointer;
        padding: 0 0 0 10px;
      }
    `;
    document.head.appendChild(style);
  }
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div>${message}</div>
    <button class="close-btn">&times;</button>
  `;
  
  // Add notification to container
  container.appendChild(notification);
  
  // Show notification with animation
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Set up close button
  notification.querySelector('.close-btn').addEventListener('click', function() {
    closeNotification(notification);
  });
  
  // Auto close after 5 seconds
  setTimeout(() => {
    closeNotification(notification);
  }, 5000);
}

// Close notification
function closeNotification(notification) {
  // Start fade out
  notification.classList.remove('show');
  
  // Remove after animation completes
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 300);
}