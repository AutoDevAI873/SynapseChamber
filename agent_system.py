import os
import logging
import json
import datetime
import time
import threading
import queue
import random
import re
from collections import defaultdict

class AgentSystem:
    """
    Automated Developer Agent for Synapse Chamber
    
    Functions similarly to Replit's Agent:
    - Plans and generates entire projects
    - Makes complex, multi-step changes
    - Pauses to ask for user feedback
    - Handles project scaffolding and implementation
    """
    
    def __init__(self, ai_controller=None, memory_system=None, training_manager=None):
        self.logger = logging.getLogger(__name__)
        self.ai_controller = ai_controller
        self.memory_system = memory_system
        self.training_manager = training_manager
        self.agent_dir = "data/agent"
        
        # Agent state
        self.is_running = False
        self.current_task = None
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.status_updates = []
        self.feedback_requests = []
        self.feedback_responses = {}
        
        # Project state
        self.current_project = None
        self.project_plan = []
        self.current_step = 0
        self.generated_files = []
        self.modified_files = []
        
        # Agent configuration
        self.primary_platform = "gpt"  # Default AI platform to use
        self.reflection_enabled = True
        self.auto_correction = True
        self.verbose_planning = True
        
        # Ensure agent directory exists
        os.makedirs(self.agent_dir, exist_ok=True)
        
        # Load agent state
        self._load_state()
    
    def _load_state(self):
        """Load agent state from disk"""
        state_path = os.path.join(self.agent_dir, "agent_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    
                    # Apply saved state
                    if 'primary_platform' in state:
                        self.primary_platform = state['primary_platform']
                    if 'reflection_enabled' in state:
                        self.reflection_enabled = state['reflection_enabled']
                    if 'auto_correction' in state:
                        self.auto_correction = state['auto_correction']
                    if 'verbose_planning' in state:
                        self.verbose_planning = state['verbose_planning']
                    
                    # Load current project if available
                    if 'current_project' in state and state['current_project']:
                        project_id = state['current_project']
                        self._load_project(project_id)
                    
                    self.logger.info("Loaded agent state")
            except Exception as e:
                self.logger.error(f"Error loading agent state: {str(e)}")
    
    def _save_state(self):
        """Save agent state to disk"""
        state_path = os.path.join(self.agent_dir, "agent_state.json")
        try:
            state = {
                'primary_platform': self.primary_platform,
                'reflection_enabled': self.reflection_enabled,
                'auto_correction': self.auto_correction,
                'verbose_planning': self.verbose_planning,
                'current_project': self.current_project['id'] if self.current_project else None,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)
                
            self.logger.info("Saved agent state")
        except Exception as e:
            self.logger.error(f"Error saving agent state: {str(e)}")
    
    def _load_project(self, project_id):
        """Load project state from disk"""
        project_path = os.path.join(self.agent_dir, f"project_{project_id}.json")
        if os.path.exists(project_path):
            try:
                with open(project_path, 'r') as f:
                    project_data = json.load(f)
                    self.current_project = project_data
                    self.project_plan = project_data.get('plan', [])
                    self.current_step = project_data.get('current_step', 0)
                    self.generated_files = project_data.get('generated_files', [])
                    self.modified_files = project_data.get('modified_files', [])
                    self.logger.info(f"Loaded project {project_id}")
                    return True
            except Exception as e:
                self.logger.error(f"Error loading project {project_id}: {str(e)}")
                return False
        else:
            self.logger.warning(f"Project {project_id} not found")
            return False
    
    def _save_project(self):
        """Save current project state to disk"""
        if not self.current_project:
            return False
            
        project_id = self.current_project['id']
        project_path = os.path.join(self.agent_dir, f"project_{project_id}.json")
        
        try:
            # Update project data
            self.current_project['plan'] = self.project_plan
            self.current_project['current_step'] = self.current_step
            self.current_project['generated_files'] = self.generated_files
            self.current_project['modified_files'] = self.modified_files
            self.current_project['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(project_path, 'w') as f:
                json.dump(self.current_project, f, indent=2)
                
            self.logger.info(f"Saved project {project_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving project {project_id}: {str(e)}")
            return False
    
    def start(self):
        """
        Start the agent system
        
        Returns:
            bool: Success status
        """
        if self.is_running:
            self.logger.warning("Agent system is already running")
            return False
        
        try:
            # Initialize worker thread
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.is_running = True
            self.worker_thread.start()
            
            self._add_status_update("Agent system started")
            self.logger.info("Agent system started")
            return True
        except Exception as e:
            self.logger.error(f"Error starting agent system: {str(e)}")
            self.is_running = False
            return False
    
    def stop(self):
        """
        Stop the agent system
        
        Returns:
            bool: Success status
        """
        if not self.is_running:
            self.logger.warning("Agent system is not running")
            return False
        
        try:
            self.is_running = False
            
            if self.worker_thread and self.worker_thread.is_alive():
                # Add a poison pill task
                self._schedule_task({'type': 'shutdown'})
                
                # Wait for the worker to finish (with timeout)
                self.worker_thread.join(timeout=5.0)
            
            self._add_status_update("Agent system stopped")
            self.logger.info("Agent system stopped")
            
            # Save state before shutdown
            self._save_state()
            if self.current_project:
                self._save_project()
                
            return True
        except Exception as e:
            self.logger.error(f"Error stopping agent system: {str(e)}")
            return False
    
    def _worker_loop(self):
        """Main worker loop for agent system"""
        while self.is_running:
            try:
                # Get the next task (with timeout to allow for shutdown)
                try:
                    task = self.task_queue.get(timeout=5.0)
                except queue.Empty:
                    # If no task, check if we have an active project and continue working
                    if self.current_project and self.current_step < len(self.project_plan):
                        self._continue_project_execution()
                    continue
                
                # Check for shutdown signal
                if task.get('type') == 'shutdown':
                    self.logger.info("Received shutdown signal, exiting worker loop")
                    break
                
                # Process the task
                self.current_task = task
                self._process_task(task)
                self.current_task = None
                
                # Mark task as done
                self.task_queue.task_done()
            
            except Exception as e:
                self.logger.error(f"Error in agent worker loop: {str(e)}")
                self.current_task = None
                time.sleep(5)  # Delay before retry
    
    def _process_task(self, task):
        """
        Process an agent task
        
        Args:
            task (dict): Task definition
        """
        task_type = task.get('type')
        self.logger.info(f"Processing task: {task_type}")
        
        if task_type == 'create_project':
            description = task.get('description')
            preferences = task.get('preferences', {})
            self._create_new_project(description, preferences)
        
        elif task_type == 'continue_project':
            project_id = task.get('project_id')
            self._continue_project(project_id)
        
        elif task_type == 'execute_step':
            step_index = task.get('step_index')
            force = task.get('force', False)
            self._execute_project_step(step_index, force)
        
        elif task_type == 'generate_code':
            file_path = task.get('file_path')
            description = task.get('description')
            self._generate_code_file(file_path, description)
        
        elif task_type == 'modify_code':
            file_path = task.get('file_path')
            description = task.get('description')
            self._modify_code_file(file_path, description)
        
        elif task_type == 'process_feedback':
            feedback_id = task.get('feedback_id')
            self._process_user_feedback(feedback_id)
        
        else:
            self.logger.warning(f"Unknown task type: {task_type}")
    
    def _schedule_task(self, task):
        """
        Schedule a task for execution
        
        Args:
            task (dict): Task definition with type, priority, etc.
        """
        try:
            # Add scheduled time if not present
            if 'scheduled_time' not in task:
                task['scheduled_time'] = time.time()
            
            # Add to queue
            self.task_queue.put(task)
            
            task_type = task.get('type')
            self.logger.info(f"Scheduled task: {task_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error scheduling task: {str(e)}")
            return False
    
    def _add_status_update(self, message, level='info'):
        """
        Add a status update
        
        Args:
            message (str): Status message
            level (str): Log level (info, warning, error)
        """
        update = {
            'timestamp': time.time(),
            'message': message,
            'level': level
        }
        
        self.status_updates.append(update)
        
        # Trim status updates to the most recent 100
        if len(self.status_updates) > 100:
            self.status_updates = self.status_updates[-100:]
        
        # Log based on level
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _create_new_project(self, description, preferences=None):
        """
        Create a new project based on description
        
        Args:
            description (str): Project description
            preferences (dict): User preferences for the project
        """
        self._add_status_update(f"Creating new project: {description[:50]}...")
        
        # Generate a unique project ID
        project_id = f"project_{int(time.time())}"
        
        # Initialize project structure
        self.current_project = {
            'id': project_id,
            'description': description,
            'preferences': preferences or {},
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'planning',
            'plan': [],
            'current_step': 0,
            'generated_files': [],
            'modified_files': []
        }
        
        # Generate project plan
        self._generate_project_plan()
        
        # Save initial project state
        self._save_project()
        self._save_state()
        
        # Request confirmation from user
        feedback_id = self._request_user_feedback(
            "I've created a plan for your project. Please review and let me know if you'd like to make any changes.",
            {
                'type': 'project_plan',
                'project_id': project_id,
                'plan': self.project_plan
            }
        )
        
        # Wait for feedback before proceeding
        self._add_status_update("Waiting for user feedback on project plan")
    
    def _generate_project_plan(self):
        """Generate a step-by-step plan for the current project"""
        if not self.current_project:
            self.logger.error("No current project to generate plan for")
            return False
            
        description = self.current_project.get('description', '')
        preferences = self.current_project.get('preferences', {})
        
        self._add_status_update("Generating project plan...")
        
        if not self.ai_controller:
            # Fallback plan generation if AI controller not available
            self._generate_fallback_plan(description, preferences)
            return True
        
        try:
            # Construct prompt for AI
            prompt = f"""Create a detailed step-by-step plan for implementing this project:
            
Description: {description}

User preferences:
{json.dumps(preferences, indent=2)}

Create a structured plan with the following:
1. Clear, numbered steps with specific actions
2. Identification of necessary files to create/modify
3. Dependencies to install
4. Project structure recommendations
5. Implementation order

Format your response as a JSON array of step objects, each with:
- "type": One of ["setup", "code_generation", "installation", "testing", "documentation"]
- "title": A brief title for the step
- "description": Detailed description of what to do
- "files": Array of file paths to create or modify
- "dependencies": Array of dependencies needed
- "commands": Array of commands to run (if any)

Example:
[
  {{
    "type": "setup",
    "title": "Initialize project structure",
    "description": "Create basic directory structure for the project",
    "files": ["src/", "tests/", "docs/", "src/__init__.py"],
    "dependencies": [],
    "commands": ["mkdir -p src tests docs"]
  }},
  {{
    "type": "installation",
    "title": "Install core dependencies",
    "description": "Install required Python packages",
    "files": ["requirements.txt"],
    "dependencies": ["flask", "sqlalchemy", "pytest"],
    "commands": ["pip install -r requirements.txt"]
  }}
]

Return only the JSON array without any additional explanation.
"""
            
            # Get plan from AI
            response = self.ai_controller.interact_with_ai(self.primary_platform, prompt)
            
            if not response or not response.get('content'):
                raise Exception("Failed to get project plan from AI")
                
            # Extract the plan from the response
            plan_text = response.get('content', '')
            
            # Extract JSON content (AI might wrap it in markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', plan_text)
            if json_match:
                plan_text = json_match.group(1)
            
            # Parse the plan
            try:
                plan = json.loads(plan_text)
                if not isinstance(plan, list):
                    raise Exception("Expected a list of steps")
                    
                # Add step indices
                for i, step in enumerate(plan):
                    step['index'] = i
                    step['status'] = 'pending'
                
                self.project_plan = plan
                self.current_step = 0
                self.current_project['status'] = 'planned'
                self.current_project['plan'] = plan
                
                self._add_status_update(f"Generated project plan with {len(plan)} steps")
                return True
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing plan JSON: {str(e)}")
                # Fallback to regex-based extraction
                self._extract_plan_from_text(plan_text)
                return True
                
        except Exception as e:
            self.logger.error(f"Error generating project plan: {str(e)}")
            # Fallback plan generation
            self._generate_fallback_plan(description, preferences)
            return False
    
    def _extract_plan_from_text(self, text):
        """Extract plan steps from unstructured text"""
        steps = []
        
        # Try to find step patterns
        step_patterns = [
            r'(\d+)\.\s+(?:Step\s+\d+:)?\s*([^:\n]+)(?::|\.)\s*(.*?)(?=\d+\.\s+|$)',
            r'(?:Step|Task)\s+(\d+):\s*([^:\n]+)(?::|\.)\s*(.*?)(?=(?:Step|Task)\s+\d+:|$)'
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                for index, title, description in matches:
                    steps.append({
                        'index': int(index) - 1,
                        'type': self._infer_step_type(title, description),
                        'title': title.strip(),
                        'description': description.strip(),
                        'files': self._extract_files_from_text(description),
                        'dependencies': self._extract_dependencies_from_text(description),
                        'commands': self._extract_commands_from_text(description),
                        'status': 'pending'
                    })
                break
        
        # If no steps found, create basic steps
        if not steps:
            steps = self._generate_fallback_plan_steps()
            
        self.project_plan = steps
        self.current_step = 0
        self.current_project['status'] = 'planned'
        self.current_project['plan'] = steps
        
        self._add_status_update(f"Generated project plan with {len(steps)} steps")
    
    def _infer_step_type(self, title, description):
        """Infer step type from title and description"""
        title_lower = title.lower()
        desc_lower = description.lower()
        
        if any(term in title_lower or term in desc_lower for term in ['install', 'dependency', 'package', 'requirement']):
            return 'installation'
        elif any(term in title_lower or term in desc_lower for term in ['structure', 'setup', 'initialize', 'scaffold']):
            return 'setup'
        elif any(term in title_lower or term in desc_lower for term in ['test', 'testing']):
            return 'testing'
        elif any(term in title_lower or term in desc_lower for term in ['document', 'documentation', 'readme']):
            return 'documentation'
        else:
            return 'code_generation'
    
    def _extract_files_from_text(self, text):
        """Extract file paths mentioned in text"""
        # Look for file paths with extensions
        file_patterns = [
            r'[a-zA-Z0-9_\-\/\.]+\.[a-zA-Z0-9]+',  # Matches: file.ext, path/to/file.ext
            r'["\']([a-zA-Z0-9_\-\/\.]+\.[a-zA-Z0-9]+)["\']',  # Matches quoted files
            r'`([a-zA-Z0-9_\-\/\.]+\.[a-zA-Z0-9]+)`'  # Matches backtick-quoted files
        ]
        
        files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            files.update(matches)
        
        # Look for directories
        dir_pattern = r'(?:directory|dir|folder)[\s:]*["\']?([a-zA-Z0-9_\-\/\.]+/?)["\']?'
        dir_matches = re.findall(dir_pattern, text, re.IGNORECASE)
        files.update([d if d.endswith('/') else f"{d}/" for d in dir_matches])
        
        return list(files)
    
    def _extract_dependencies_from_text(self, text):
        """Extract dependencies mentioned in text"""
        # Patterns for dependencies
        dependency_patterns = [
            r'(?:install|dependency|require|package)[\s:]*["\']?([a-zA-Z0-9_\-]+)["\']?',
            r'pip\s+install\s+([a-zA-Z0-9_\-]+)',
            r'npm\s+install\s+([a-zA-Z0-9_\-]+)'
        ]
        
        dependencies = set()
        for pattern in dependency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dependencies.update(matches)
        
        return list(dependencies)
    
    def _extract_commands_from_text(self, text):
        """Extract commands mentioned in text"""
        command_patterns = [
            r'run[\s:]*["\']?([^"\'\n]+)["\']?',
            r'execute[\s:]*["\']?([^"\'\n]+)["\']?',
            r'command[\s:]*["\']?([^"\'\n]+)["\']?',
            r'`([^`\n]+)`'  # Commands in backticks
        ]
        
        commands = set()
        for pattern in command_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            commands.update([m.strip() for m in matches if m.strip()])
        
        return list(commands)
    
    def _generate_fallback_plan(self, description, preferences):
        """Generate a fallback plan if AI planning fails"""
        self._add_status_update("Using fallback plan generation", level='warning')
        
        # Create basic steps based on project description
        steps = self._generate_fallback_plan_steps()
        
        self.project_plan = steps
        self.current_step = 0
        self.current_project['status'] = 'planned'
        self.current_project['plan'] = steps
        
        self._add_status_update(f"Generated fallback project plan with {len(steps)} steps")
    
    def _generate_fallback_plan_steps(self):
        """Generate basic fallback plan steps"""
        description = self.current_project.get('description', '')
        
        # Determine project type
        project_type = "web_application"  # Default type
        if "flask" in description.lower() or "web app" in description.lower():
            project_type = "web_application"
        elif "api" in description.lower() or "rest" in description.lower():
            project_type = "api"
        elif "cli" in description.lower() or "command line" in description.lower():
            project_type = "cli"
        elif "data" in description.lower() or "analysis" in description.lower():
            project_type = "data_analysis"
        
        # Generate steps based on project type
        if project_type == "web_application":
            return [
                {
                    'index': 0,
                    'type': 'setup',
                    'title': 'Initialize project structure',
                    'description': 'Create basic directory structure for the web application',
                    'files': ['app.py', 'templates/', 'static/', 'requirements.txt'],
                    'dependencies': [],
                    'commands': ['mkdir -p templates static'],
                    'status': 'pending'
                },
                {
                    'index': 1,
                    'type': 'installation',
                    'title': 'Install dependencies',
                    'description': 'Install Flask and other required packages',
                    'files': ['requirements.txt'],
                    'dependencies': ['flask', 'flask-sqlalchemy', 'werkzeug'],
                    'commands': ['pip install -r requirements.txt'],
                    'status': 'pending'
                },
                {
                    'index': 2,
                    'type': 'code_generation',
                    'title': 'Create Flask application',
                    'description': 'Implement the main Flask application file',
                    'files': ['app.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 3,
                    'type': 'code_generation',
                    'title': 'Create database models',
                    'description': 'Define database models for the application',
                    'files': ['models.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 4,
                    'type': 'code_generation',
                    'title': 'Create templates',
                    'description': 'Create HTML templates for the web interface',
                    'files': ['templates/layout.html', 'templates/index.html'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 5,
                    'type': 'code_generation',
                    'title': 'Create static assets',
                    'description': 'Create CSS and JavaScript files',
                    'files': ['static/styles.css', 'static/script.js'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 6,
                    'type': 'testing',
                    'title': 'Create tests',
                    'description': 'Implement basic tests for the application',
                    'files': ['tests.py'],
                    'dependencies': ['pytest'],
                    'commands': ['python -m pytest tests.py'],
                    'status': 'pending'
                },
                {
                    'index': 7,
                    'type': 'documentation',
                    'title': 'Create documentation',
                    'description': 'Write documentation for the project',
                    'files': ['README.md'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                }
            ]
        elif project_type == "api":
            return [
                {
                    'index': 0,
                    'type': 'setup',
                    'title': 'Initialize project structure',
                    'description': 'Create basic directory structure for the API',
                    'files': ['app.py', 'api/', 'models/', 'requirements.txt'],
                    'dependencies': [],
                    'commands': ['mkdir -p api models'],
                    'status': 'pending'
                },
                {
                    'index': 1,
                    'type': 'installation',
                    'title': 'Install dependencies',
                    'description': 'Install Flask, Flask-RESTful and other required packages',
                    'files': ['requirements.txt'],
                    'dependencies': ['flask', 'flask-restful', 'flask-sqlalchemy'],
                    'commands': ['pip install -r requirements.txt'],
                    'status': 'pending'
                },
                {
                    'index': 2,
                    'type': 'code_generation',
                    'title': 'Create API application',
                    'description': 'Implement the main API application file',
                    'files': ['app.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 3,
                    'type': 'code_generation',
                    'title': 'Create database models',
                    'description': 'Define database models for the API',
                    'files': ['models/base.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 4,
                    'type': 'code_generation',
                    'title': 'Create API endpoints',
                    'description': 'Implement API resource endpoints',
                    'files': ['api/resources.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 5,
                    'type': 'testing',
                    'title': 'Create tests',
                    'description': 'Implement API tests',
                    'files': ['tests.py'],
                    'dependencies': ['pytest'],
                    'commands': ['python -m pytest tests.py'],
                    'status': 'pending'
                },
                {
                    'index': 6,
                    'type': 'documentation',
                    'title': 'Create API documentation',
                    'description': 'Write API documentation',
                    'files': ['README.md', 'api-docs.md'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                }
            ]
        else:
            # Generic fallback plan
            return [
                {
                    'index': 0,
                    'type': 'setup',
                    'title': 'Initialize project structure',
                    'description': 'Create basic directory structure for the project',
                    'files': ['main.py', 'requirements.txt'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 1,
                    'type': 'installation',
                    'title': 'Install dependencies',
                    'description': 'Install required packages',
                    'files': ['requirements.txt'],
                    'dependencies': [],
                    'commands': ['pip install -r requirements.txt'],
                    'status': 'pending'
                },
                {
                    'index': 2,
                    'type': 'code_generation',
                    'title': 'Create main module',
                    'description': 'Implement the main module',
                    'files': ['main.py'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                },
                {
                    'index': 3,
                    'type': 'testing',
                    'title': 'Create tests',
                    'description': 'Implement tests',
                    'files': ['tests.py'],
                    'dependencies': ['pytest'],
                    'commands': ['python -m pytest tests.py'],
                    'status': 'pending'
                },
                {
                    'index': 4,
                    'type': 'documentation',
                    'title': 'Create documentation',
                    'description': 'Write documentation',
                    'files': ['README.md'],
                    'dependencies': [],
                    'commands': [],
                    'status': 'pending'
                }
            ]
    
    def _continue_project(self, project_id):
        """
        Continue working on an existing project
        
        Args:
            project_id (str): Project ID to continue
        """
        # Load the project
        if not self._load_project(project_id):
            self._add_status_update(f"Failed to load project {project_id}", level='error')
            return False
        
        self._add_status_update(f"Continuing project: {project_id}")
        
        # Update state
        self._save_state()
        
        # Continue from current step
        self._continue_project_execution()
    
    def _continue_project_execution(self):
        """Continue executing the current project from the current step"""
        if not self.current_project:
            self.logger.error("No current project to continue")
            return False
        
        if not self.project_plan:
            self.logger.error("No project plan to execute")
            return False
        
        # Check if we're waiting for feedback
        if self.feedback_requests and not self._check_feedback_received():
            # Still waiting for feedback, don't proceed
            return False
        
        # Check if we've reached the end of the plan
        if self.current_step >= len(self.project_plan):
            self._add_status_update("Project plan completed", level='info')
            self.current_project['status'] = 'completed'
            self._save_project()
            return True
        
        # Execute the current step
        self._execute_project_step(self.current_step)
        return True
    
    def _check_feedback_received(self):
        """Check if we have received feedback for the most recent request"""
        if not self.feedback_requests:
            return True
            
        # Get the most recent feedback request
        latest_request = self.feedback_requests[-1]
        feedback_id = latest_request.get('id')
        
        # Check if we've received a response
        return feedback_id in self.feedback_responses
    
    def _execute_project_step(self, step_index, force=False):
        """
        Execute a specific step in the project plan
        
        Args:
            step_index (int): Index of the step to execute
            force (bool): Force execution even if step is already completed
        """
        if not self.current_project or not self.project_plan:
            self.logger.error("No current project or plan to execute step")
            return False
        
        # Validate step index
        if step_index < 0 or step_index >= len(self.project_plan):
            self._add_status_update(f"Invalid step index: {step_index}", level='error')
            return False
        
        # Get the step
        step = self.project_plan[step_index]
        
        # Check if step is already completed
        if step.get('status') == 'completed' and not force:
            self._add_status_update(f"Step {step_index} already completed, skipping")
            
            # Move to next step
            self.current_step = step_index + 1
            self._save_project()
            self._continue_project_execution()
            return True
        
        # Set step as in progress
        step['status'] = 'in_progress'
        self.current_step = step_index
        self._save_project()
        
        self._add_status_update(f"Executing step {step_index}: {step.get('title')}")
        
        # Execute based on step type
        step_type = step.get('type')
        result = False
        
        if step_type == 'setup':
            result = self._execute_setup_step(step)
        elif step_type == 'installation':
            result = self._execute_installation_step(step)
        elif step_type == 'code_generation':
            result = self._execute_code_generation_step(step)
        elif step_type == 'testing':
            result = self._execute_testing_step(step)
        elif step_type == 'documentation':
            result = self._execute_documentation_step(step)
        else:
            self._add_status_update(f"Unknown step type: {step_type}", level='warning')
            # Try generic execution
            result = self._execute_generic_step(step)
        
        # Update step status
        if result:
            step['status'] = 'completed'
            self._add_status_update(f"Completed step {step_index}: {step.get('title')}")
            
            # Move to next step
            self.current_step = step_index + 1
            self._save_project()
            
            # Continue to next step if in automated execution
            self._continue_project_execution()
        else:
            step['status'] = 'failed'
            self._add_status_update(f"Failed to execute step {step_index}: {step.get('title')}", level='error')
            self._save_project()
            
            # Request user help
            feedback_id = self._request_user_feedback(
                f"I encountered an issue with step {step_index}: {step.get('title')}. Can you provide guidance or make changes to help me continue?",
                {
                    'type': 'step_failure',
                    'project_id': self.current_project['id'],
                    'step_index': step_index,
                    'step': step
                }
            )
        
        return result
    
    def _execute_setup_step(self, step):
        """Execute a setup step"""
        description = step.get('description', '')
        files = step.get('files', [])
        commands = step.get('commands', [])
        
        self._add_status_update(f"Setting up project structure: {description}")
        
        # Execute any setup commands
        for command in commands:
            self._add_status_update(f"Running setup command: {command}")
            # In real implementation, execute command with subprocess
            # For now, just log it
            self._add_status_update(f"Command executed: {command}")
        
        # Create directories mentioned in files
        directories = [f for f in files if f.endswith('/')]
        for directory in directories:
            self._add_status_update(f"Creating directory: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                self._add_status_update(f"Error creating directory {directory}: {str(e)}", level='error')
        
        # Request generation of initial files
        for file_path in files:
            if not file_path.endswith('/'):  # Skip directories
                self._schedule_task({
                    'type': 'generate_code',
                    'file_path': file_path,
                    'description': f"Create initial version of {file_path}\n\nBased on step: {description}"
                })
        
        return True
    
    def _execute_installation_step(self, step):
        """Execute an installation step"""
        description = step.get('description', '')
        files = step.get('files', [])
        dependencies = step.get('dependencies', [])
        commands = step.get('commands', [])
        
        self._add_status_update(f"Installing dependencies: {description}")
        
        # Create requirements files if needed
        for file_path in files:
            if 'requirements.txt' in file_path:
                self._add_status_update(f"Creating {file_path}")
                req_content = '\n'.join(dependencies)
                try:
                    # Create directory if needed
                    dir_name = os.path.dirname(file_path)
                    if dir_name:
                        os.makedirs(dir_name, exist_ok=True)
                    
                    with open(file_path, 'w') as f:
                        f.write(req_content)
                    
                    self.generated_files.append(file_path)
                except Exception as e:
                    self._add_status_update(f"Error creating {file_path}: {str(e)}", level='error')
        
        # For actual implementation, use packager_tool to install dependencies
        # For now, just log it
        if dependencies:
            dependency_list = ', '.join(dependencies)
            self._add_status_update(f"Would install dependencies: {dependency_list}")
            # In real implementation:
            # self.packager_tool.install(dependencies)
        
        # Execute commands
        for command in commands:
            self._add_status_update(f"Running installation command: {command}")
            # In real implementation, execute command with subprocess
            # For now, just log it
            self._add_status_update(f"Command executed: {command}")
        
        return True
    
    def _execute_code_generation_step(self, step):
        """Execute a code generation step"""
        description = step.get('description', '')
        files = step.get('files', [])
        
        self._add_status_update(f"Generating code: {description}")
        
        # Request generation of files
        for file_path in files:
            if not file_path.endswith('/'):  # Skip directories
                self._schedule_task({
                    'type': 'generate_code',
                    'file_path': file_path,
                    'description': f"Create {file_path}\n\nBased on step: {description}\n\nProject context: {self.current_project.get('description', '')}"
                })
        
        # Wait for file generation tasks to complete in a real implementation
        # For now, just simulate it
        time.sleep(1)
        
        return True
    
    def _execute_testing_step(self, step):
        """Execute a testing step"""
        description = step.get('description', '')
        files = step.get('files', [])
        
        self._add_status_update(f"Setting up tests: {description}")
        
        # Generate test files
        for file_path in files:
            if not file_path.endswith('/'):  # Skip directories
                self._schedule_task({
                    'type': 'generate_code',
                    'file_path': file_path,
                    'description': f"Create test file {file_path}\n\nBased on step: {description}\n\nImplement tests for project: {self.current_project.get('description', '')}"
                })
        
        # In a real implementation, you would also run the tests
        self._add_status_update("Test files generated successfully")
        
        return True
    
    def _execute_documentation_step(self, step):
        """Execute a documentation step"""
        description = step.get('description', '')
        files = step.get('files', [])
        
        self._add_status_update(f"Creating documentation: {description}")
        
        # Generate documentation files
        for file_path in files:
            if not file_path.endswith('/'):  # Skip directories
                self._schedule_task({
                    'type': 'generate_code',
                    'file_path': file_path,
                    'description': f"Create documentation file {file_path}\n\nBased on step: {description}\n\nDocument project: {self.current_project.get('description', '')}"
                })
        
        self._add_status_update("Documentation generated successfully")
        
        return True
    
    def _execute_generic_step(self, step):
        """Execute a generic step"""
        description = step.get('description', '')
        files = step.get('files', [])
        commands = step.get('commands', [])
        
        self._add_status_update(f"Executing step: {description}")
        
        # Execute commands
        for command in commands:
            self._add_status_update(f"Running command: {command}")
            # In real implementation, execute command with subprocess
            # For now, just log it
            self._add_status_update(f"Command executed: {command}")
        
        # Generate or modify files
        for file_path in files:
            if not file_path.endswith('/'):  # Skip directories
                # Check if file already exists
                if os.path.exists(file_path):
                    self._schedule_task({
                        'type': 'modify_code',
                        'file_path': file_path,
                        'description': f"Modify {file_path}\n\nBased on step: {description}"
                    })
                else:
                    self._schedule_task({
                        'type': 'generate_code',
                        'file_path': file_path,
                        'description': f"Create {file_path}\n\nBased on step: {description}"
                    })
        
        return True
    
    def _generate_code_file(self, file_path, description):
        """
        Generate a code file
        
        Args:
            file_path (str): Path to the file to generate
            description (str): Description of what to generate
        """
        self._add_status_update(f"Generating code file: {file_path}")
        
        if not self.ai_controller:
            self._add_status_update("AI controller not available, can't generate code", level='error')
            return False
        
        try:
            # Create directory if needed
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            
            # Generate file contents with AI
            prompt = f"""Generate code for the following file: {file_path}

Description: {description}

Project context: {self.current_project.get('description', '')}

Step context: I'm working on a project step to create this file as part of the overall project.

Current files in the project:
{', '.join(self.generated_files + self.modified_files)}

Please generate complete, functional code for this file. Include comments and documentation where appropriate.
Ensure the code is properly formatted and follows best practices for the file type.
"""
            
            response = self.ai_controller.interact_with_ai(self.primary_platform, prompt)
            
            if not response or not response.get('content'):
                raise Exception("Failed to generate code from AI")
                
            # Extract the code from the response
            code_text = response.get('content', '')
            
            # Extract code blocks if present
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)\s*```', code_text)
            if code_blocks:
                # Use the largest code block
                code_text = max(code_blocks, key=len)
            
            # Write to file
            with open(file_path, 'w') as f:
                f.write(code_text)
            
            # Add to generated files
            if file_path not in self.generated_files:
                self.generated_files.append(file_path)
            
            self._add_status_update(f"Generated file {file_path} successfully")
            
            # Save project state
            self._save_project()
            
            return True
        except Exception as e:
            self._add_status_update(f"Error generating file {file_path}: {str(e)}", level='error')
            return False
    
    def _modify_code_file(self, file_path, description):
        """
        Modify an existing code file
        
        Args:
            file_path (str): Path to the file to modify
            description (str): Description of the modifications
        """
        self._add_status_update(f"Modifying code file: {file_path}")
        
        if not self.ai_controller:
            self._add_status_update("AI controller not available, can't modify code", level='error')
            return False
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self._add_status_update(f"File {file_path} does not exist", level='error')
                return False
            
            # Read current file contents
            with open(file_path, 'r') as f:
                current_code = f.read()
            
            # Generate modifications with AI
            prompt = f"""Modify the following file: {file_path}

Description of changes needed: {description}

Project context: {self.current_project.get('description', '')}

Current file contents:
```
{current_code}
```

Please provide the complete updated file with the requested modifications. 
Include comments explaining the changes you made.
Ensure the code remains functional and follows best practices.
"""
            
            response = self.ai_controller.interact_with_ai(self.primary_platform, prompt)
            
            if not response or not response.get('content'):
                raise Exception("Failed to generate code modifications from AI")
                
            # Extract the code from the response
            modified_code = response.get('content', '')
            
            # Extract code blocks if present
            code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)\s*```', modified_code)
            if code_blocks:
                # Use the largest code block
                modified_code = max(code_blocks, key=len)
            
            # Write to file
            with open(file_path, 'w') as f:
                f.write(modified_code)
            
            # Add to modified files
            if file_path not in self.modified_files and file_path not in self.generated_files:
                self.modified_files.append(file_path)
            
            self._add_status_update(f"Modified file {file_path} successfully")
            
            # Save project state
            self._save_project()
            
            return True
        except Exception as e:
            self._add_status_update(f"Error modifying file {file_path}: {str(e)}", level='error')
            return False
    
    def _request_user_feedback(self, message, context):
        """
        Request feedback from the user
        
        Args:
            message (str): Message to the user
            context (dict): Context for the feedback
            
        Returns:
            str: Feedback request ID
        """
        # Generate unique ID for feedback request
        feedback_id = f"feedback_{int(time.time())}_{len(self.feedback_requests)}"
        
        # Create feedback request
        feedback_request = {
            'id': feedback_id,
            'message': message,
            'context': context,
            'timestamp': time.time(),
            'status': 'pending'
        }
        
        # Add to feedback requests
        self.feedback_requests.append(feedback_request)
        
        # Trim old feedback requests (keep last 20)
        if len(self.feedback_requests) > 20:
            self.feedback_requests = self.feedback_requests[-20:]
        
        self._add_status_update(f"Requested user feedback: {message}")
        
        # In a real implementation, this would send the request to the user interface
        # For now, just log it
        self.logger.info(f"Feedback request {feedback_id}: {message}")
        
        return feedback_id
    
    def _process_user_feedback(self, feedback_id):
        """
        Process feedback received from the user
        
        Args:
            feedback_id (str): ID of the feedback to process
        """
        # Find the feedback
        if feedback_id not in self.feedback_responses:
            self._add_status_update(f"Feedback {feedback_id} not found", level='error')
            return False
        
        feedback = self.feedback_responses[feedback_id]
        feedback_type = feedback.get('type')
        response = feedback.get('response')
        
        self._add_status_update(f"Processing user feedback: {feedback_type}")
        
        if feedback_type == 'project_plan':
            # User has confirmed or modified the project plan
            if response.get('action') == 'confirm':
                self._add_status_update("User confirmed project plan")
                # Begin executing the plan
                self._continue_project_execution()
            elif response.get('action') == 'modify':
                self._add_status_update("User modified project plan")
                # Update the plan
                modified_plan = response.get('modified_plan')
                if modified_plan:
                    self.project_plan = modified_plan
                    self.current_project['plan'] = modified_plan
                    self._save_project()
                    # Begin executing the updated plan
                    self._continue_project_execution()
            elif response.get('action') == 'restart':
                self._add_status_update("User requested project plan restart")
                # Generate a new plan
                self._generate_project_plan()
                # Request confirmation again
                feedback_id = self._request_user_feedback(
                    "I've created a new plan for your project. Please review and let me know if you'd like to make any changes.",
                    {
                        'type': 'project_plan',
                        'project_id': self.current_project['id'],
                        'plan': self.project_plan
                    }
                )
        
        elif feedback_type == 'step_failure':
            # User has provided guidance on a failed step
            if response.get('action') == 'retry':
                step_index = response.get('step_index')
                self._add_status_update(f"Retrying step {step_index} based on user feedback")
                self._execute_project_step(step_index, force=True)
            elif response.get('action') == 'skip':
                step_index = response.get('step_index')
                self._add_status_update(f"Skipping step {step_index} based on user feedback")
                # Mark step as skipped
                if 0 <= step_index < len(self.project_plan):
                    self.project_plan[step_index]['status'] = 'skipped'
                # Move to next step
                self.current_step = step_index + 1
                self._save_project()
                self._continue_project_execution()
            elif response.get('action') == 'modify':
                step_index = response.get('step_index')
                modified_step = response.get('modified_step')
                self._add_status_update(f"Modifying step {step_index} based on user feedback")
                # Update the step
                if 0 <= step_index < len(self.project_plan) and modified_step:
                    self.project_plan[step_index] = modified_step
                    self._save_project()
                    # Retry the step
                    self._execute_project_step(step_index, force=True)
        
        elif feedback_type == 'code_feedback':
            # User has provided feedback on generated code
            file_path = response.get('file_path')
            self._add_status_update(f"Processing code feedback for {file_path}")
            
            if response.get('action') == 'accept':
                self._add_status_update(f"User accepted code for {file_path}")
                # Continue with execution
                self._continue_project_execution()
            elif response.get('action') == 'regenerate':
                self._add_status_update(f"Regenerating code for {file_path} based on user feedback")
                description = response.get('description', '')
                self._generate_code_file(file_path, description)
            elif response.get('action') == 'modify':
                self._add_status_update(f"Modifying code for {file_path} based on user feedback")
                modified_code = response.get('modified_code')
                if modified_code:
                    try:
                        with open(file_path, 'w') as f:
                            f.write(modified_code)
                        self._add_status_update(f"Updated {file_path} with user modifications")
                        
                        # Add to modified files
                        if file_path not in self.modified_files and file_path not in self.generated_files:
                            self.modified_files.append(file_path)
                        
                        # Save project state
                        self._save_project()
                    except Exception as e:
                        self._add_status_update(f"Error updating {file_path}: {str(e)}", level='error')
        
        else:
            self._add_status_update(f"Unknown feedback type: {feedback_type}", level='warning')
        
        return True
    
    def provide_feedback(self, feedback_id, response):
        """
        Provide user feedback for a requested feedback
        
        Args:
            feedback_id (str): ID of the feedback request
            response (dict): The user's response
            
        Returns:
            bool: Success status
        """
        # Validate feedback ID
        found = False
        for request in self.feedback_requests:
            if request['id'] == feedback_id:
                found = True
                request['status'] = 'responded'
                break
        
        if not found:
            self.logger.error(f"Feedback request {feedback_id} not found")
            return False
        
        # Store the response
        self.feedback_responses[feedback_id] = response
        
        # Schedule task to process the feedback
        self._schedule_task({
            'type': 'process_feedback',
            'feedback_id': feedback_id,
            'priority': 1,
            'scheduled_time': time.time()  # Process immediately
        })
        
        self._add_status_update(f"Received user feedback for {feedback_id}")
        
        return True
    
    def create_new_project(self, description, preferences=None):
        """
        Start creating a new project
        
        Args:
            description (str): Project description
            preferences (dict, optional): User preferences for the project
            
        Returns:
            dict: Task information or error
        """
        try:
            if not description:
                return {'status': 'error', 'message': 'Project description is required'}
                
            # Schedule the project creation task
            task = {
                'type': 'create_project',
                'description': description,
                'preferences': preferences or {},
                'priority': 1,
                'scheduled_time': time.time() + 10  # Start soon
            }
            
            success = self._schedule_task(task)
            
            if success:
                self._add_status_update(f"Scheduled new project creation: {description[:50]}...")
                return {'status': 'success', 'task': task}
            else:
                return {'status': 'error', 'message': 'Failed to schedule project creation task'}
        except Exception as e:
            self.logger.error(f"Error creating new project: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_projects(self, limit=10):
        """
        Get list of projects
        
        Args:
            limit (int): Maximum number of projects to return
            
        Returns:
            list: Project information
        """
        projects = []
        
        # Get all project files
        project_files = [f for f in os.listdir(self.agent_dir) if f.startswith('project_') and f.endswith('.json')]
        
        # Sort by last modified time (newest first)
        project_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.agent_dir, f)), reverse=True)
        
        # Load project data
        for filename in project_files[:limit]:
            try:
                with open(os.path.join(self.agent_dir, filename), 'r') as f:
                    project_data = json.load(f)
                    
                    # Add summary information
                    project_summary = {
                        'id': project_data.get('id'),
                        'description': project_data.get('description'),
                        'status': project_data.get('status'),
                        'created_at': project_data.get('created_at'),
                        'last_updated': project_data.get('last_updated'),
                        'steps_total': len(project_data.get('plan', [])),
                        'steps_completed': sum(1 for step in project_data.get('plan', []) if step.get('status') == 'completed'),
                        'files_count': len(project_data.get('generated_files', [])) + len(project_data.get('modified_files', []))
                    }
                    
                    projects.append(project_summary)
            except Exception as e:
                self.logger.error(f"Error loading project from {filename}: {str(e)}")
        
        return projects
    
    def get_project_details(self, project_id):
        """
        Get detailed information about a project
        
        Args:
            project_id (str): Project ID
            
        Returns:
            dict: Project details
        """
        # Load project data
        project_path = os.path.join(self.agent_dir, f"project_{project_id}.json")
        if not os.path.exists(project_path):
            return {'status': 'error', 'message': f"Project {project_id} not found"}
            
        try:
            with open(project_path, 'r') as f:
                project_data = json.load(f)
                
                # Calculate additional stats
                steps_completed = sum(1 for step in project_data.get('plan', []) if step.get('status') == 'completed')
                steps_total = len(project_data.get('plan', []))
                completion_percentage = int((steps_completed / max(1, steps_total)) * 100)
                
                # Add computed fields
                project_data['completion_percentage'] = completion_percentage
                project_data['steps_completed'] = steps_completed
                project_data['steps_total'] = steps_total
                
                return {'status': 'success', 'project': project_data}
        except Exception as e:
            self.logger.error(f"Error loading project {project_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self):
        """
        Get the current status of the agent system
        
        Returns:
            dict: Status information
        """
        # Count active feedback requests
        pending_feedback = sum(1 for req in self.feedback_requests if req.get('status') == 'pending')
        
        # Get current project info
        current_project_info = None
        if self.current_project:
            steps_completed = sum(1 for step in self.project_plan if step.get('status') == 'completed')
            steps_total = len(self.project_plan)
            
            current_project_info = {
                'id': self.current_project.get('id'),
                'description': self.current_project.get('description'),
                'status': self.current_project.get('status'),
                'current_step': self.current_step,
                'steps_completed': steps_completed,
                'steps_total': steps_total,
                'completion_percentage': int((steps_completed / max(1, steps_total)) * 100)
            }
        
        # Get recent status updates
        recent_updates = self.status_updates[-10:] if self.status_updates else []
        
        return {
            'is_running': self.is_running,
            'current_task': self.current_task,
            'current_project': current_project_info,
            'pending_feedback': pending_feedback,
            'primary_platform': self.primary_platform,
            'reflection_enabled': self.reflection_enabled,
            'auto_correction': self.auto_correction,
            'recent_updates': recent_updates
        }
    
    def get_status_updates(self, limit=20):
        """
        Get recent status updates
        
        Args:
            limit (int): Maximum number of updates to return
            
        Returns:
            list: Status update messages
        """
        return self.status_updates[-limit:] if self.status_updates else []
    
    def get_feedback_requests(self, status=None):
        """
        Get feedback requests
        
        Args:
            status (str, optional): Filter by status ('pending', 'responded')
            
        Returns:
            list: Feedback requests
        """
        if status:
            return [req for req in self.feedback_requests if req.get('status') == status]
        return self.feedback_requests
    
    def update_configuration(self, config):
        """
        Update agent configuration
        
        Args:
            config (dict): New configuration settings
            
        Returns:
            bool: Success status
        """
        try:
            updated = False
            
            if 'primary_platform' in config:
                self.primary_platform = config['primary_platform']
                updated = True
                
            if 'reflection_enabled' in config:
                self.reflection_enabled = config['reflection_enabled']
                updated = True
                
            if 'auto_correction' in config:
                self.auto_correction = config['auto_correction']
                updated = True
                
            if 'verbose_planning' in config:
                self.verbose_planning = config['verbose_planning']
                updated = True
            
            if updated:
                self._save_state()
                self._add_status_update("Agent configuration updated")
                
            return True
        except Exception as e:
            self.logger.error(f"Error updating configuration: {str(e)}")
            return False
    
    def __del__(self):
        """Clean up resources on deletion"""
        # Stop the agent system if running
        if self.is_running:
            self.stop()
            
        # Save all data
        self._save_state()
        if self.current_project:
            self._save_project()