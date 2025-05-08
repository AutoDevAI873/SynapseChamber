import os
import logging
import json
import datetime
import time
import random
import threading
import queue
from collections import defaultdict, Counter

class SelfTrainingSystem:
    """
    Self-Training System for Synapse Chamber
    
    Enables AutoDev to autonomously improve through:
    - Self-initiated training sessions
    - Automated performance analysis
    - Capability gap identification
    - Progress tracking and self-assessment
    """
    
    def __init__(self, training_manager=None, memory_system=None, analytics_system=None, ai_controller=None):
        self.logger = logging.getLogger(__name__)
        self.training_manager = training_manager
        self.memory_system = memory_system
        self.analytics_system = analytics_system
        self.ai_controller = ai_controller
        self.self_training_dir = "data/self_training"
        
        # Status tracking
        self.is_running = False
        self.current_task = None
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.status_updates = []
        
        # Training history and progress tracking
        self.training_history = []
        self.capability_scores = {}
        self.identified_gaps = []
        self.active_goals = []
        
        # Training parameters
        self.training_frequency = 24 * 3600  # Default: once per day (in seconds)
        self.max_consecutive_sessions = 3
        self.min_success_threshold = 0.7
        
        # Ensure self-training directory exists
        os.makedirs(self.self_training_dir, exist_ok=True)
        
        # Initialize self-training system
        self._init_system()
    
    def _init_system(self):
        """Initialize the self-training system"""
        # Load configuration
        self._load_config()
        
        # Load training history
        self._load_training_history()
        
        # Load capability scores
        self._load_capability_scores()
        
        # Load active goals
        self._load_active_goals()
    
    def _load_config(self):
        """Load self-training configuration"""
        config_path = os.path.join(self.self_training_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                    # Apply configuration
                    if 'training_frequency' in config:
                        self.training_frequency = config['training_frequency']
                    if 'max_consecutive_sessions' in config:
                        self.max_consecutive_sessions = config['max_consecutive_sessions']
                    if 'min_success_threshold' in config:
                        self.min_success_threshold = config['min_success_threshold']
                    
                    self.logger.info("Loaded self-training configuration")
            except Exception as e:
                self.logger.error(f"Error loading self-training configuration: {str(e)}")
    
    def _save_config(self):
        """Save self-training configuration"""
        config_path = os.path.join(self.self_training_dir, "config.json")
        try:
            config = {
                'training_frequency': self.training_frequency,
                'max_consecutive_sessions': self.max_consecutive_sessions,
                'min_success_threshold': self.min_success_threshold,
                'last_updated': datetime.datetime.now().isoformat()
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.logger.info("Saved self-training configuration")
        except Exception as e:
            self.logger.error(f"Error saving self-training configuration: {str(e)}")
    
    def _load_training_history(self):
        """Load self-training history"""
        history_path = os.path.join(self.self_training_dir, "training_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.training_history = json.load(f)
                    self.logger.info(f"Loaded {len(self.training_history)} self-training history records")
            except Exception as e:
                self.logger.error(f"Error loading self-training history: {str(e)}")
                self.training_history = []
    
    def _save_training_history(self):
        """Save self-training history"""
        history_path = os.path.join(self.self_training_dir, "training_history.json")
        try:
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f, indent=2)
                
            self.logger.info(f"Saved {len(self.training_history)} self-training history records")
        except Exception as e:
            self.logger.error(f"Error saving self-training history: {str(e)}")
    
    def _load_capability_scores(self):
        """Load capability scores"""
        scores_path = os.path.join(self.self_training_dir, "capability_scores.json")
        if os.path.exists(scores_path):
            try:
                with open(scores_path, 'r') as f:
                    self.capability_scores = json.load(f)
                    self.logger.info(f"Loaded capability scores for {len(self.capability_scores)} areas")
            except Exception as e:
                self.logger.error(f"Error loading capability scores: {str(e)}")
                self.capability_scores = {}
    
    def _save_capability_scores(self):
        """Save capability scores"""
        scores_path = os.path.join(self.self_training_dir, "capability_scores.json")
        try:
            with open(scores_path, 'w') as f:
                json.dump(self.capability_scores, f, indent=2)
                
            self.logger.info(f"Saved capability scores for {len(self.capability_scores)} areas")
        except Exception as e:
            self.logger.error(f"Error saving capability scores: {str(e)}")
    
    def _load_active_goals(self):
        """Load active training goals"""
        goals_path = os.path.join(self.self_training_dir, "active_goals.json")
        if os.path.exists(goals_path):
            try:
                with open(goals_path, 'r') as f:
                    self.active_goals = json.load(f)
                    self.logger.info(f"Loaded {len(self.active_goals)} active training goals")
            except Exception as e:
                self.logger.error(f"Error loading active goals: {str(e)}")
                self.active_goals = []
    
    def _save_active_goals(self):
        """Save active training goals"""
        goals_path = os.path.join(self.self_training_dir, "active_goals.json")
        try:
            with open(goals_path, 'w') as f:
                json.dump(self.active_goals, f, indent=2)
                
            self.logger.info(f"Saved {len(self.active_goals)} active training goals")
        except Exception as e:
            self.logger.error(f"Error saving active goals: {str(e)}")
    
    def start(self):
        """
        Start the self-training system
        
        Returns:
            bool: Success status
        """
        if self.is_running:
            self.logger.warning("Self-training system is already running")
            return False
        
        try:
            # Initialize worker thread
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.is_running = True
            self.worker_thread.start()
            
            self._add_status_update("Self-training system started")
            self.logger.info("Self-training system started")
            
            # Schedule initial capability assessment
            self._schedule_task({
                'type': 'capability_assessment',
                'priority': 1,
                'scheduled_time': time.time() + 60  # Start assessment in 1 minute
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error starting self-training system: {str(e)}")
            self.is_running = False
            return False
    
    def stop(self):
        """
        Stop the self-training system
        
        Returns:
            bool: Success status
        """
        if not self.is_running:
            self.logger.warning("Self-training system is not running")
            return False
        
        try:
            self.is_running = False
            
            if self.worker_thread and self.worker_thread.is_alive():
                # Add a poison pill task
                self._schedule_task({'type': 'shutdown'})
                
                # Wait for the worker to finish (with timeout)
                self.worker_thread.join(timeout=5.0)
            
            self._add_status_update("Self-training system stopped")
            self.logger.info("Self-training system stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping self-training system: {str(e)}")
            return False
    
    def _worker_loop(self):
        """Main worker loop for self-training system"""
        while self.is_running:
            try:
                # Get the next task (with timeout to allow for shutdown)
                try:
                    task = self.task_queue.get(timeout=5.0)
                except queue.Empty:
                    # Check if it's time to schedule a new training session
                    self._check_training_schedule()
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
                self.logger.error(f"Error in self-training worker loop: {str(e)}")
                self.current_task = None
                time.sleep(5)  # Delay before retry
    
    def _process_task(self, task):
        """
        Process a self-training task
        
        Args:
            task (dict): Task definition
        """
        task_type = task.get('type')
        self.logger.info(f"Processing task: {task_type}")
        
        if task_type == 'capability_assessment':
            self._perform_capability_assessment()
        
        elif task_type == 'training_session':
            topic = task.get('topic')
            mode = task.get('mode', 'all_ais_train')
            platforms = task.get('platforms')
            goal = task.get('goal')
            
            self._run_training_session(topic, mode, platforms, goal)
        
        elif task_type == 'apply_training':
            thread_id = task.get('thread_id')
            self._apply_training_results(thread_id)
        
        elif task_type == 'gap_analysis':
            self._perform_gap_analysis()
        
        elif task_type == 'goal_planning':
            self._perform_goal_planning()
        
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
    
    def _check_training_schedule(self):
        """Check if it's time to schedule a new training session"""
        # Skip if queue is not empty
        if not self.task_queue.empty():
            return
        
        # Skip if no training manager available
        if not self.training_manager:
            return
        
        # Check when the last training session was run
        last_training = None
        for entry in reversed(self.training_history):
            if entry.get('type') == 'training_session':
                last_training = entry
                break
        
        # If no training yet, or it's been long enough, schedule a new session
        current_time = time.time()
        
        if not last_training or current_time - last_training.get('timestamp', 0) > self.training_frequency:
            # Schedule gap analysis first to identify what to train
            self._schedule_task({
                'type': 'gap_analysis',
                'priority': 2,
                'scheduled_time': current_time + 10  # Start soon
            })
    
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
    
    def _perform_capability_assessment(self):
        """
        Perform an assessment of AutoDev's current capabilities
        
        Updates capability_scores with assessment results
        """
        self._add_status_update("Starting capability assessment")
        
        # Define capability areas to assess
        capability_areas = [
            'natural_language_processing',
            'api_integration',
            'error_handling',
            'file_operations',
            'automation',
            'reasoning',
            'problem_solving',
            'self_improvement'
        ]
        
        # Get training history for analysis
        history_scores = self._analyze_training_history()
        
        # Initialize scores dictionary if needed
        if not self.capability_scores:
            self.capability_scores = {area: 0.5 for area in capability_areas}
        
        # Update scores based on training history
        for area, score in history_scores.items():
            if area in self.capability_scores:
                # Blend existing score (70%) with new assessment (30%)
                self.capability_scores[area] = (self.capability_scores[area] * 0.7) + (score * 0.3)
        
        # Normalize scores to 0-1 range
        for area in self.capability_scores:
            self.capability_scores[area] = max(0, min(1, self.capability_scores[area]))
        
        # Save updated scores
        self._save_capability_scores()
        
        # Add assessment results to training history
        assessment_entry = {
            'type': 'capability_assessment',
            'timestamp': time.time(),
            'scores': self.capability_scores.copy(),
            'summary': "Automated capability assessment completed"
        }
        
        self.training_history.append(assessment_entry)
        self._save_training_history()
        
        # Schedule gap analysis based on assessment
        self._schedule_task({
            'type': 'gap_analysis',
            'priority': 2,
            'scheduled_time': time.time() + 60  # Start gap analysis in 1 minute
        })
        
        self._add_status_update("Capability assessment completed")
    
    def _analyze_training_history(self):
        """
        Analyze training history to assess capabilities
        
        Returns:
            dict: Capability scores based on training history
        """
        # Initialize scores
        scores = defaultdict(float)
        counts = defaultdict(int)
        
        # Get recent training sessions (last 20)
        recent_sessions = [entry for entry in self.training_history 
                           if entry.get('type') == 'training_session'][-20:]
        
        # No history yet
        if not recent_sessions:
            return {}
        
        # Analyze each session
        for session in recent_sessions:
            topic = session.get('topic')
            success = session.get('success', False)
            
            # Map topics to capability areas
            capability_area = self._topic_to_capability_area(topic)
            
            if capability_area:
                # Success adds a point, failure subtracts half a point
                scores[capability_area] += 1.0 if success else -0.5
                counts[capability_area] += 1
        
        # Normalize scores
        result = {}
        for area, score in scores.items():
            if counts[area] > 0:
                # Normalize to 0-1 range
                normalized = 0.5 + (score / (counts[area] * 2))
                result[area] = max(0, min(1, normalized))
        
        return result
    
    def _topic_to_capability_area(self, topic):
        """Map a training topic to a capability area"""
        if not topic:
            return None
            
        topic_lower = topic.lower()
        
        # Enhanced capability areas with more granular classification
        capability_mapping = {
            # Language Capabilities
            'natural_language_processing': [
                'natural language', 'nlp', 'language understanding', 'linguistics',
                'text analysis', 'sentiment', 'parsing', 'language model'
            ],
            'creative_writing': [
                'story', 'write', 'novel', 'creative', 'fiction', 'poem', 'narrative'
            ],
            'language_translation': [
                'translate', 'translation', 'multilingual', 'language conversion'
            ],
            
            # Technical Capabilities
            'code_generation': [
                'code', 'programming', 'function', 'algorithm', 'development', 'software',
                'class', 'method', 'implementation'
            ],
            'api_integration': [
                'api', 'endpoint', 'integration', 'interface', 'service', 'request'
            ],
            'error_handling': [
                'error', 'exception', 'handling', 'recovery', 'failure', 'fault'
            ],
            'file_operations': [
                'file', 'io', 'read', 'write', 'save', 'load', 'storage'
            ],
            
            # System Capabilities
            'automation': [
                'automat', 'browser', 'script', 'batch', 'workflow', 'process'
            ],
            'debugging': [
                'debug', 'diagnose', 'fix', 'troubleshoot', 'issue', 'bug'
            ],
            'testing': [
                'test', 'validation', 'verify', 'assertion', 'quality', 'unit test'
            ],
            
            # Analytical Capabilities
            'reasoning': [
                'reason', 'logic', 'deduction', 'inference', 'critical thinking',
                'analysis', 'evaluate'
            ],
            'problem_solving': [
                'problem', 'solve', 'solution', 'resolve', 'approach', 'strategy'
            ],
            'decision_making': [
                'decision', 'choose', 'select', 'prioritize', 'judgment', 'assessment'
            ],
            
            # Learning Capabilities
            'self_improvement': [
                'improve', 'learn', 'adapt', 'growth', 'evolve', 'self-correction'
            ],
            'knowledge_acquisition': [
                'knowledge', 'learn', 'study', 'research', 'explore', 'discover'
            ],
            'pattern_recognition': [
                'pattern', 'recognize', 'identify', 'correlate', 'trend', 'similarity'
            ],
            
            # Domain Capabilities
            'domain_knowledge': [
                'domain', 'specialized', 'field', 'industry', 'specific', 'expert'
            ],
            'research': [
                'research', 'investigate', 'analyze', 'study', 'examine', 'inquiry'
            ],
            'data_analysis': [
                'data', 'analysis', 'statistics', 'metrics', 'insights', 'analytics'
            ],
            
            # Interaction Capabilities
            'human_interaction': [
                'interaction', 'communication', 'human', 'interface', 'dialogue', 'conversation'
            ],
            'instruction_following': [
                'instruction', 'direction', 'guidance', 'command', 'follow', 'execute'
            ],
            'explanation': [
                'explain', 'clarify', 'elaborate', 'describe', 'detail', 'simplify'
            ]
        }
        
        # Find the best matching capability area
        best_match = None
        max_matches = 0
        
        for capability, keywords in capability_mapping.items():
            # Count how many keywords match the topic
            matches = sum(1 for keyword in keywords if keyword in topic_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = capability
        
        # If we found a match, return it
        if max_matches > 0:
            return best_match
        
        # Default capability area if no match found
        return 'general'
    
    def _perform_gap_analysis(self):
        """
        Analyze capability gaps and identify training needs
        
        Updates identified_gaps with analysis results
        """
        self._add_status_update("Starting capability gap analysis")
        
        # Check if we have capability scores
        if not self.capability_scores:
            self._add_status_update("No capability scores available, performing assessment first", level='warning')
            self._perform_capability_assessment()
        
        # Sort capabilities by score (ascending)
        sorted_capabilities = sorted(self.capability_scores.items(), key=lambda x: x[1])
        
        # Identify the lowest scoring capabilities
        self.identified_gaps = []
        
        for area, score in sorted_capabilities:
            if score < 0.7:  # Consider anything below 0.7 as a gap
                gap = {
                    'area': area,
                    'current_score': score,
                    'target_score': min(1.0, score + 0.2),
                    'identified_at': time.time(),
                    'priority': 1 if score < 0.5 else 2
                }
                
                self.identified_gaps.append(gap)
        
        # Save the identified gaps to training history
        gaps_entry = {
            'type': 'gap_analysis',
            'timestamp': time.time(),
            'gaps': self.identified_gaps.copy()
        }
        
        self.training_history.append(gaps_entry)
        self._save_training_history()
        
        # Schedule goal planning based on gaps
        self._schedule_task({
            'type': 'goal_planning',
            'priority': 2,
            'scheduled_time': time.time() + 30  # Start goal planning soon
        })
        
        self._add_status_update(f"Identified {len(self.identified_gaps)} capability gaps")
    
    def _perform_goal_planning(self):
        """
        Plan training goals based on identified gaps
        
        Updates active_goals with planned goals
        """
        self._add_status_update("Starting training goal planning")
        
        # Check if we have identified gaps
        if not self.identified_gaps:
            self._add_status_update("No capability gaps identified, performing gap analysis first", level='warning')
            self._perform_gap_analysis()
            
            if not self.identified_gaps:
                self._add_status_update("No capability gaps found, no training needed at this time")
                return
        
        # Update active goals
        self.active_goals = []
        
        for gap in self.identified_gaps:
            area = gap['area']
            
            # Create a training goal for this gap
            topic = self._capability_area_to_topic(area)
            
            if topic:
                goal = {
                    'area': area,
                    'topic': topic,
                    'created_at': time.time(),
                    'target_score': gap['target_score'],
                    'status': 'planned',
                    'priority': gap['priority'],
                    'training_sessions': []
                }
                
                self.active_goals.append(goal)
        
        # Sort goals by priority
        self.active_goals.sort(key=lambda g: g['priority'])
        
        # Save active goals
        self._save_active_goals()
        
        # Add goal planning to training history
        planning_entry = {
            'type': 'goal_planning',
            'timestamp': time.time(),
            'goals': self.active_goals.copy()
        }
        
        self.training_history.append(planning_entry)
        self._save_training_history()
        
        # Schedule training session for highest priority goal
        if self.active_goals:
            highest_priority_goal = self.active_goals[0]
            self._schedule_training_for_goal(highest_priority_goal)
        
        self._add_status_update(f"Created {len(self.active_goals)} training goals")
    
    def _capability_area_to_topic(self, area):
        """Map a capability area to a training topic"""
        # Mapping from capability areas to training topics
        topic_map = {
            'natural_language_processing': 'natural_language',
            'api_integration': 'api_handling',
            'error_handling': 'error_handling',
            'file_operations': 'file_handling',
            'automation': 'automation',
            'reasoning': 'natural_language',  # Use NLP for reasoning training
            'problem_solving': 'error_handling',  # Use error handling for problem solving
            'self_improvement': 'natural_language'  # Use NLP for self-improvement
        }
        
        return topic_map.get(area)
    
    def _schedule_training_for_goal(self, goal):
        """
        Schedule a training session for a specific goal
        
        Args:
            goal (dict): Training goal to schedule for
        """
        if not self.training_manager:
            self._add_status_update("Training manager not available, cannot schedule training", level='error')
            return
        
        topic = goal.get('topic')
        if not topic:
            self._add_status_update(f"No topic specified for goal {goal.get('area')}, cannot schedule training", level='error')
            return
        
        # Update goal status
        goal['status'] = 'in_progress'
        self._save_active_goals()
        
        # Schedule training session
        self._schedule_task({
            'type': 'training_session',
            'topic': topic,
            'mode': 'all_ais_train',  # Default to using all AIs
            'platforms': None,  # Use all available platforms
            'goal': f"Improve {goal.get('area')} capabilities to reach score of {goal.get('target_score')}",
            'target_goal': goal,
            'priority': 1,
            'scheduled_time': time.time() + 120  # Start in 2 minutes
        })
        
        self._add_status_update(f"Scheduled training session for {goal.get('area')}")
    
    def _run_training_session(self, topic, mode, platforms, goal, target_goal=None):
        """
        Run a training session
        
        Args:
            topic (str): Training topic
            mode (str): Training mode
            platforms (list): AI platforms to use
            goal (str): Training goal
            target_goal (dict, optional): Target goal from active_goals
        """
        if not self.training_manager:
            self._add_status_update("Training manager not available, cannot run training", level='error')
            return
        
        self._add_status_update(f"Starting training session for topic: {topic}")
        
        try:
            # Start the training session
            result = self.training_manager.start_session(
                topic=topic,
                mode=mode,
                platforms=platforms,
                goal=goal
            )
            
            if result.get('status') != 'success':
                self._add_status_update(f"Failed to start training session: {result.get('message', 'Unknown error')}", level='error')
                return
            
            session_id = result.get('session_id')
            
            # Record the training session
            session_entry = {
                'type': 'training_session',
                'timestamp': time.time(),
                'topic': topic,
                'mode': mode,
                'platforms': platforms,
                'goal': goal,
                'session_id': session_id,
                'status': 'running'
            }
            
            self.training_history.append(session_entry)
            self._save_training_history()
            
            # If this session is for a specific goal, update the goal
            if target_goal:
                target_goal['training_sessions'].append(session_id)
                self._save_active_goals()
            
            # Wait for session to complete
            max_wait_time = 600  # 10 minutes max
            wait_start = time.time()
            completed = False
            
            while time.time() - wait_start < max_wait_time:
                # Check session status
                status = self.training_manager.get_session_status(session_id)
                
                if status.get('status') == 'completed':
                    completed = True
                    break
                elif status.get('status') == 'failed':
                    self._add_status_update(f"Training session failed: {status.get('error', 'Unknown error')}", level='error')
                    
                    # Update session entry
                    session_entry['status'] = 'failed'
                    session_entry['success'] = False
                    self._save_training_history()
                    
                    return
                    
                # Wait before checking again
                time.sleep(30)
            
            if not completed:
                self._add_status_update("Training session timed out", level='warning')
                
                # Update session entry
                session_entry['status'] = 'timeout'
                session_entry['success'] = False
                self._save_training_history()
                
                return
            
            # Session completed successfully
            self._add_status_update(f"Training session completed: {topic}")
            
            # Update session entry
            session_entry['status'] = 'completed'
            session_entry['success'] = True
            self._save_training_history()
            
            # Schedule task to apply training results
            self._schedule_task({
                'type': 'apply_training',
                'thread_id': session_id,
                'priority': 1,
                'scheduled_time': time.time() + 60  # Apply training soon
            })
            
        except Exception as e:
            self._add_status_update(f"Error running training session: {str(e)}", level='error')
    
    def _apply_training_results(self, thread_id):
        """
        Apply training results to update AutoDev
        
        Args:
            thread_id: ID of the completed training thread
        """
        if not self.training_manager:
            self._add_status_update("Training manager not available, cannot apply training", level='error')
            return
        
        self._add_status_update(f"Applying training results from thread: {thread_id}")
        
        try:
            # Find the training session in history
            training_session = None
            for entry in reversed(self.training_history):
                if entry.get('type') == 'training_session' and entry.get('session_id') == thread_id:
                    training_session = entry
                    break
            
            if not training_session:
                self._add_status_update(f"Training session {thread_id} not found in history", level='warning')
            
            # Get the thread data
            thread_data = self.memory_system.get_thread(thread_id) if self.memory_system else None
            
            if not thread_data:
                self._add_status_update(f"Thread {thread_id} not found in memory system", level='warning')
                
                # Try to get from training manager
                status = self.training_manager.get_session_status(thread_id)
                thread_data = status
            
            # Extract information for capability update
            topic = thread_data.get('topic', training_session.get('topic') if training_session else None)
            capability_area = self._topic_to_capability_area(topic)
            
            # Check if this was successful
            success = True  # Assume success if we made it this far
            
            # Update capability scores
            if capability_area and capability_area in self.capability_scores:
                current_score = self.capability_scores[capability_area]
                
                # Improve score if successful
                if success:
                    # Increase by 0.1, but never above 1.0
                    new_score = min(1.0, current_score + 0.1)
                    self.capability_scores[capability_area] = new_score
                    
                    self._add_status_update(f"Improved {capability_area} score from {current_score:.2f} to {new_score:.2f}")
                else:
                    # Small decrease if failed
                    new_score = max(0.0, current_score - 0.05)
                    self.capability_scores[capability_area] = new_score
                    
                    self._add_status_update(f"Reduced {capability_area} score from {current_score:.2f} to {new_score:.2f} due to failure")
                
                # Save updated scores
                self._save_capability_scores()
                
                # Update any active goals for this capability area
                self._update_goals_for_capability(capability_area)
            
            # Record the application in training history
            application_entry = {
                'type': 'training_application',
                'timestamp': time.time(),
                'thread_id': thread_id,
                'topic': topic,
                'capability_area': capability_area,
                'success': success
            }
            
            self.training_history.append(application_entry)
            self._save_training_history()
            
            # Schedule a new capability assessment
            self._schedule_task({
                'type': 'capability_assessment',
                'priority': 3,
                'scheduled_time': time.time() + 300  # 5 minutes later
            })
            
            self._add_status_update(f"Applied training results from {topic}")
            
        except Exception as e:
            self._add_status_update(f"Error applying training results: {str(e)}", level='error')
    
    def _update_goals_for_capability(self, capability_area):
        """
        Update active goals for a specific capability area
        
        Args:
            capability_area (str): The capability area that was trained
        """
        updated = False
        
        for goal in self.active_goals:
            if goal['area'] == capability_area:
                current_score = self.capability_scores[capability_area]
                target_score = goal['target_score']
                
                # Check if goal has been met
                if current_score >= target_score:
                    goal['status'] = 'completed'
                    goal['completed_at'] = time.time()
                    updated = True
                    
                    self._add_status_update(f"Training goal for {capability_area} has been completed")
                elif goal['status'] == 'in_progress':
                    # Still in progress, but let's update
                    goal['last_updated'] = time.time()
                    updated = True
        
        if updated:
            self._save_active_goals()
            
            # If we completed some goals, check if we need to schedule training for other goals
            active_in_progress = [g for g in self.active_goals if g['status'] == 'in_progress']
            remaining_planned = [g for g in self.active_goals if g['status'] == 'planned']
            
            if not active_in_progress and remaining_planned:
                # Schedule the next goal
                next_goal = remaining_planned[0]
                self._schedule_training_for_goal(next_goal)
    
    def get_status(self):
        """
        Get the current status of the self-training system
        
        Returns:
            dict: Status information
        """
        # Count active goals by status
        goal_counts = Counter()
        for goal in self.active_goals:
            goal_counts[goal['status']] += 1
        
        # Get recent status updates
        recent_updates = self.status_updates[-10:] if self.status_updates else []
        
        # Count training sessions
        training_count = sum(1 for entry in self.training_history if entry.get('type') == 'training_session')
        success_count = sum(1 for entry in self.training_history 
                          if entry.get('type') == 'training_session' and entry.get('success', False))
        
        # Calculate success rate
        success_rate = success_count / training_count if training_count > 0 else 0
        
        return {
            'is_running': self.is_running,
            'current_task': self.current_task,
            'task_queue_size': self.task_queue.qsize(),
            'capability_areas': len(self.capability_scores),
            'avg_capability_score': sum(self.capability_scores.values()) / len(self.capability_scores) if self.capability_scores else 0,
            'identified_gaps': len(self.identified_gaps),
            'active_goals': {
                'total': len(self.active_goals),
                'planned': goal_counts['planned'],
                'in_progress': goal_counts['in_progress'],
                'completed': goal_counts['completed']
            },
            'training_sessions': {
                'total': training_count,
                'successful': success_count,
                'success_rate': success_rate
            },
            'recent_updates': recent_updates
        }
    
    def get_capability_report(self):
        """
        Get a detailed report on current capabilities
        
        Returns:
            dict: Capability report
        """
        # Get the latest capability assessment
        latest_assessment = None
        for entry in reversed(self.training_history):
            if entry.get('type') == 'capability_assessment':
                latest_assessment = entry
                break
        
        # Get recent training sessions
        recent_sessions = [entry for entry in self.training_history 
                          if entry.get('type') == 'training_session'][-5:]
        
        # Get recent training applications
        recent_applications = [entry for entry in self.training_history 
                              if entry.get('type') == 'training_application'][-5:]
        
        return {
            'capability_scores': self.capability_scores,
            'latest_assessment': latest_assessment,
            'identified_gaps': self.identified_gaps,
            'active_goals': self.active_goals,
            'recent_sessions': recent_sessions,
            'recent_applications': recent_applications
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
    
    def update_configuration(self, config):
        """
        Update self-training configuration
        
        Args:
            config (dict): New configuration settings
            
        Returns:
            bool: Success status
        """
        try:
            updated = False
            
            if 'training_frequency' in config:
                self.training_frequency = config['training_frequency']
                updated = True
                
            if 'max_consecutive_sessions' in config:
                self.max_consecutive_sessions = config['max_consecutive_sessions']
                updated = True
                
            if 'min_success_threshold' in config:
                self.min_success_threshold = config['min_success_threshold']
                updated = True
            
            if updated:
                self._save_config()
                self._add_status_update("Self-training configuration updated")
                
            return True
        except Exception as e:
            self.logger.error(f"Error updating configuration: {str(e)}")
            return False
    
    def manually_trigger_training(self, topic, mode=None, platforms=None, goal=None):
        """
        Manually trigger a training session
        
        Args:
            topic (str): Training topic
            mode (str, optional): Training mode
            platforms (list, optional): AI platforms to use
            goal (str, optional): Training goal
            
        Returns:
            dict: Task information or error
        """
        try:
            if not topic:
                return {'status': 'error', 'message': 'Topic is required'}
                
            # Use defaults if not specified
            if not mode:
                mode = 'all_ais_train'
                
            if not goal:
                goal = f"Manually triggered training on {topic}"
            
            # Schedule the training task
            task = {
                'type': 'training_session',
                'topic': topic,
                'mode': mode,
                'platforms': platforms,
                'goal': goal,
                'priority': 1,
                'scheduled_time': time.time() + 10  # Start soon
            }
            
            success = self._schedule_task(task)
            
            if success:
                self._add_status_update(f"Manually triggered training for {topic}")
                return {'status': 'success', 'task': task}
            else:
                return {'status': 'error', 'message': 'Failed to schedule training task'}
        except Exception as e:
            self.logger.error(f"Error triggering manual training: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def manually_assess_capabilities(self):
        """
        Manually trigger a capability assessment
        
        Returns:
            dict: Task information or error
        """
        try:
            # Schedule the assessment task
            task = {
                'type': 'capability_assessment',
                'priority': 1,
                'scheduled_time': time.time() + 10  # Start soon
            }
            
            success = self._schedule_task(task)
            
            if success:
                self._add_status_update("Manually triggered capability assessment")
                return {'status': 'success', 'task': task}
            else:
                return {'status': 'error', 'message': 'Failed to schedule assessment task'}
        except Exception as e:
            self.logger.error(f"Error triggering manual assessment: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def __del__(self):
        """Clean up resources on deletion"""
        # Stop the self-training system if running
        if self.is_running:
            self.stop()
            
        # Save all data
        self._save_training_history()
        self._save_capability_scores()
        self._save_active_goals()
        self._save_config()