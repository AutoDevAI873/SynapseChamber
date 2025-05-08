import os
import logging
import json
import time
import datetime
import traceback
import threading
import random
from app import db
from models import TrainingThread, AIConversation, Message

class TrainingSessionManager:
    """
    Orchestrates multi-AI training rounds for AutoDev.
    Collects responses from different AI platforms on the same topic,
    analyzes them, and produces a final recommendation.
    """
    
    def __init__(self, ai_controller, memory_system):
        self.logger = logging.getLogger(__name__)
        self.ai_controller = ai_controller
        self.memory_system = memory_system
        self.data_dir = "data/training"
        self.status_updates = []
        self.current_session = None
        
        # Training topics and their prompts
        self.training_topics = {
            "natural_language": {
                "name": "Natural Language Processing",
                "description": "Training on text parsing, tokenization, and language understanding",
                "prompts": [
                    "What is the most efficient way to implement tokenization for multi-language inputs?",
                    "How would you design a regex-based entity extraction system that's robust against variations?",
                    "What's the best approach to implement sentiment analysis that can handle sarcasm and context?"
                ]
            },
            "api_handling": {
                "name": "API Integration & Authentication",
                "description": "Training on robust API connections, auth flows, and error handling",
                "prompts": [
                    "What's the most secure way to handle OAuth2 authentication flow in a headless environment?",
                    "How would you implement a retry mechanism for unreliable APIs with exponential backoff?",
                    "What's the best strategy for rate limiting and quota management when working with multiple APIs?"
                ]
            },
            "file_handling": {
                "name": "File System Operations",
                "description": "Training on file manipulation, parsing, and transformation",
                "prompts": [
                    "What's the most efficient way to handle large file operations with minimal memory usage?",
                    "How would you implement a reliable file locking mechanism for concurrent access?",
                    "What's the best approach to implement a file watcher that works across different operating systems?"
                ]
            },
            "automation": {
                "name": "Browser & UI Automation",
                "description": "Training on browser control, CAPTCHA solving, and UI interaction",
                "prompts": [
                    "What's the most reliable way to detect and handle dynamic loading elements in a web page?",
                    "How would you implement a system to bypass browser fingerprinting detection?",
                    "What's the best strategy for handling multi-step forms with validation and error states?"
                ]
            },
            "error_handling": {
                "name": "Error Detection & Recovery",
                "description": "Training on robust error handling, debugging, and self-recovery",
                "prompts": [
                    "What's the most comprehensive way to implement error handling in asynchronous operations?",
                    "How would you design a system that can automatically recover from common failure modes?",
                    "What's the best approach to implement logging that helps with automated debugging?"
                ]
            }
        }
        
        # Available training modes
        self.training_modes = [
            "all_ais_train",  # All AIs provide input on the topic
            "single_ai_teaches"  # One AI provides in-depth training
        ]
        
        # Ensure training data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def start_session(self, topic, mode, platforms=None, goal=None):
        """
        Start a new training session on the specified topic.
        
        Args:
            topic (str): The training topic (must be in self.training_topics)
            mode (str): The training mode (must be in self.training_modes)
            platforms (list): List of AI platforms to use, or None for all available
            goal (str): Specific goal for this training session
            
        Returns:
            dict: Session information with ID and status
        """
        if topic not in self.training_topics:
            raise ValueError(f"Unknown training topic: {topic}")
            
        if mode not in self.training_modes:
            raise ValueError(f"Unknown training mode: {mode}")
        
        # If platforms not specified, use all available
        if platforms is None:
            platforms = ["gpt", "gemini", "deepseek", "claude", "grok"]
        
        # Create a training thread in the memory system
        topic_info = self.training_topics[topic]
        thread_subject = f"Training: {topic_info['name']}"
        thread_goal = goal or topic_info['description']
        
        thread_id = self.memory_system.create_training_thread(thread_subject, thread_goal)
        
        # Initialize session data
        self.current_session = {
            "id": thread_id,
            "topic": topic,
            "mode": mode,
            "platforms": platforms,
            "status": "started",
            "start_time": datetime.datetime.now().isoformat(),
            "conversations": [],
            "progress": 0,
            "errors": [],
            "final_recommendation": None
        }
        
        # Log the start of the session
        self._add_status_update(f"✅ Starting training session on {topic_info['name']}")
        self._add_status_update(f"Mode: {mode}")
        self._add_status_update(f"Platforms: {', '.join(platforms)}")
        
        # Start the training in a separate thread to avoid blocking
        training_thread = threading.Thread(target=self._run_training_session)
        training_thread.daemon = True
        training_thread.start()
        
        return {
            "status": "success",
            "session_id": thread_id,
            "message": f"Started training session on {topic_info['name']}",
            "topic": topic_info['name'],
            "mode": mode
        }
    
    def _run_training_session(self):
        """Run the current training session"""
        try:
            topic = self.current_session["topic"]
            mode = self.current_session["mode"]
            platforms = self.current_session["platforms"]
            thread_id = self.current_session["id"]
            
            topic_info = self.training_topics[topic]
            prompts = topic_info["prompts"]
            
            # Determine which prompts to use based on mode
            if mode == "all_ais_train":
                # Use one random prompt for all AIs
                selected_prompts = [random.choice(prompts)]
                self._add_status_update(f"Selected prompt: {selected_prompts[0]}")
            else:  # single_ai_teaches
                # Use all prompts but only with one AI
                selected_prompts = prompts
                platform = random.choice(platforms)
                platforms = [platform]
                self._add_status_update(f"Selected AI teacher: {platform}")
            
            ai_contributions = {}
            
            # Collect responses from each AI platform
            for platform in platforms:
                self._add_status_update(f"🔄 Querying {platform}...")
                
                try:
                    platform_responses = []
                    
                    for prompt in selected_prompts:
                        # Create a specific goal for this interaction
                        interaction_goal = f"Training AutoDev on {topic_info['name']}"
                        
                        # Log that we're sending a prompt
                        self._add_status_update(f"Sending prompt to {platform}: {prompt[:50]}...")
                        
                        # Determine task type from topic
                        task_type = self._get_task_type_from_topic(topic_info)
                        
                        # Check if we should get platform recommendations
                        if mode == 'auto_select' and task_type:
                            # Get platform recommendations
                            recommended_platforms = self.ai_controller.recommend_platform(prompt, task_type)
                            if recommended_platforms:
                                platform = recommended_platforms[0]  # Use the top recommendation
                                self._add_status_update(f"Selected {platform} as optimal platform for {task_type} task")
                        
                        # Interact with the AI platform
                        result = self.ai_controller.interact_with_ai(
                            platform=platform,
                            prompt=prompt,
                            subject=topic_info['name'],
                            goal=interaction_goal,
                            task_type=task_type
                        )
                        
                        if result.get("status") == "success":
                            response = result.get("response", "No response received")
                            conversation_id = result.get("conversation_id")
                            
                            # Associate the conversation with the training thread
                            if conversation_id:
                                self.memory_system.associate_conversation_with_thread(thread_id, conversation_id)
                                self.current_session["conversations"].append(conversation_id)
                            
                            # Log success
                            self._add_status_update(f"✅ Received response from {platform}")
                            platform_responses.append({
                                "prompt": prompt,
                                "response": response,
                                "conversation_id": conversation_id
                            })
                        else:
                            error = result.get("message", "Unknown error")
                            self._add_status_update(f"❌ Error with {platform}: {error}")
                            self.current_session["errors"].append({
                                "platform": platform,
                                "error": error,
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                    
                    # Add to contributions if we got any responses
                    if platform_responses:
                        ai_contributions[platform] = platform_responses
                
                except Exception as e:
                    error_msg = f"Error processing {platform}: {str(e)}"
                    self._add_status_update(f"❌ {error_msg}")
                    self.logger.error(error_msg)
                    self.logger.error(traceback.format_exc())
                    self.current_session["errors"].append({
                        "platform": platform,
                        "error": str(e),
                        "timestamp": datetime.datetime.now().isoformat()
                    })
            
            # Generate a final recommendation based on all responses
            if ai_contributions:
                self._add_status_update("🧠 Generating final recommendation...")
                
                # For now, use a simple approach - in a real implementation this would be more sophisticated
                # and might involve additional AI calls to summarize or evaluate the responses
                final_recommendation = self._generate_recommendation(ai_contributions, topic_info)
                
                self.current_session["final_recommendation"] = final_recommendation
                self._add_status_update(f"✅ Final recommendation generated")
                
                # Update the training thread with the final plan and AI contributions
                self.memory_system.update_thread(
                    thread_id,
                    final_plan=final_recommendation["summary"],
                    ai_contributions=ai_contributions
                )
                
                # Mark as complete
                self.current_session["status"] = "completed"
                self.current_session["end_time"] = datetime.datetime.now().isoformat()
                self._add_status_update("✅ Training session completed successfully")
                
                # Save the session data
                self._save_session_data()
                
                return final_recommendation
            else:
                error_msg = "No AI contributions collected - training failed"
                self._add_status_update(f"❌ {error_msg}")
                self.current_session["status"] = "failed"
                self.current_session["end_time"] = datetime.datetime.now().isoformat()
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Training session error: {str(e)}"
            self._add_status_update(f"❌ {error_msg}")
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.current_session["status"] = "failed"
            self.current_session["end_time"] = datetime.datetime.now().isoformat()
            return {"error": error_msg}
    
    def _generate_recommendation(self, ai_contributions, topic_info):
        """
        Generate a final recommendation based on all AI contributions.
        
        In a real implementation, this would be more sophisticated and might use 
        another AI call to synthesize the responses.
        """
        # Find the most detailed response as a simple heuristic
        best_platform = None
        best_response = ""
        best_length = 0
        
        insights = []
        
        for platform, responses in ai_contributions.items():
            for resp_data in responses:
                response = resp_data["response"]
                if len(response) > best_length:
                    best_length = len(response)
                    best_response = response
                    best_platform = platform
                
                # Extract a key insight from each platform (simplified)
                if response:
                    # Just get the first sentence as an "insight"
                    first_sentence = response.split('.')[0]
                    if len(first_sentence) > 20:  # Only if it's substantial
                        insights.append({
                            "platform": platform,
                            "insight": first_sentence + "."
                        })
        
        # Create a summary
        platforms_str = ", ".join(ai_contributions.keys())
        summary = f"Training completed on {topic_info['name']}. "
        
        if best_platform:
            summary += f"{best_platform.capitalize()} provided the most detailed response. "
        
        if insights:
            summary += "Key insights: "
            for i, insight in enumerate(insights[:3]):  # Top 3 insights
                if i > 0:
                    summary += " "
                summary += f"{insight['platform'].capitalize()}: {insight['insight']}"
        
        # Create the recommendation structure
        recommendation = {
            "best_platform": best_platform,
            "summary": summary,
            "topic": topic_info["name"],
            "insights": insights,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return recommendation
    
    def get_session_status(self, session_id=None):
        """Get the status of a training session"""
        if session_id is None and self.current_session:
            session_id = self.current_session["id"]
            
        if not session_id:
            return {"error": "No session ID provided"}
            
        if self.current_session and str(self.current_session["id"]) == str(session_id):
            return {
                "session_id": session_id,
                "status": self.current_session["status"],
                "topic": self.training_topics[self.current_session["topic"]]["name"],
                "mode": self.current_session["mode"],
                "platforms": self.current_session["platforms"],
                "progress": self.current_session.get("progress", 0),
                "updates": self.status_updates[-20:],  # Last 20 updates
                "error_count": len(self.current_session.get("errors", [])),
                "recommendation": self.current_session.get("final_recommendation")
            }
        else:
            # Try to load from saved data
            session_file = os.path.join(self.data_dir, f"session_{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    
                return {
                    "session_id": session_id,
                    "status": session_data.get("status", "unknown"),
                    "topic": session_data.get("topic_name", "Unknown"),
                    "mode": session_data.get("mode", "unknown"),
                    "platforms": session_data.get("platforms", []),
                    "updates": session_data.get("status_updates", [])[-20:],
                    "error_count": len(session_data.get("errors", [])),
                    "recommendation": session_data.get("final_recommendation")
                }
            else:
                # Try to get from database
                try:
                    thread = self.memory_system.get_thread(session_id)
                    if thread:
                        return {
                            "session_id": session_id,
                            "status": "completed",  # If in DB and not active, must be completed
                            "topic": thread.get("subject", "Unknown"),
                            "goal": thread.get("goal", ""),
                            "final_plan": thread.get("final_plan", "No final plan available"),
                            "ai_contributions": thread.get("ai_contributions", {}),
                            "conversations": [c.get("id") for c in thread.get("conversations", [])]
                        }
                except Exception as e:
                    self.logger.error(f"Error retrieving session from DB: {str(e)}")
                
                return {"error": f"Session {session_id} not found"}
    
    def get_available_topics(self):
        """Get list of available training topics"""
        return {topic_id: {
            "name": info["name"],
            "description": info["description"]
        } for topic_id, info in self.training_topics.items()}
    
    def get_available_modes(self):
        """Get list of available training modes"""
        return self.training_modes
    
    def get_status_updates(self, limit=None):
        """Get status updates from the current session"""
        if limit:
            return self.status_updates[-limit:]
        return self.status_updates
    
    def _add_status_update(self, message):
        """Add a status update with timestamp"""
        timestamp = datetime.datetime.now().isoformat()
        update = {"timestamp": timestamp, "message": message}
        self.status_updates.append(update)
        self.logger.info(f"Training update: {message}")
        return update
    
    def _save_session_data(self):
        """Save the current session data to a file"""
        if not self.current_session:
            return
            
        session_id = self.current_session["id"]
        session_file = os.path.join(self.data_dir, f"session_{session_id}.json")
        
        # Create a copy with additional metadata
        session_data = dict(self.current_session)
        session_data["status_updates"] = self.status_updates
        
        # Add topic name for easier reference
        topic_info = self.training_topics[session_data["topic"]]
        session_data["topic_name"] = topic_info["name"]
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        self.logger.info(f"Saved session data to {session_file}")
        
class AutoDevUpdater:
    """
    Handles updates to AutoDev based on training session results.
    This class is responsible for taking the final recommendations from
    training sessions and applying them to enhance AutoDev's capabilities.
    """
    
    def __init__(self, memory_system):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.updates_dir = "data/autodev_updates"
        self.update_history = []
        
        # Ensure updates directory exists
        os.makedirs(self.updates_dir, exist_ok=True)
        
        # Try to load update history
        history_path = os.path.join(self.updates_dir, "update_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.update_history = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading update history: {str(e)}")
    
    def apply_training_results(self, thread_id):
        """
        Apply the results of a training session to update AutoDev
        
        Args:
            thread_id: The ID of the training thread
            
        Returns:
            dict: Status and description of the update
        """
        try:
            # Get the training thread data
            thread_data = self.memory_system.get_thread(thread_id)
            if not thread_data:
                return {"status": "error", "message": f"Thread {thread_id} not found"}
            
            # Extract relevant information
            subject = thread_data.get("subject", "Unknown topic")
            goal = thread_data.get("goal", "")
            final_plan = thread_data.get("final_plan", "")
            ai_contributions = thread_data.get("ai_contributions", {})
            
            if not final_plan:
                return {"status": "error", "message": "No final plan available in the thread"}
            
            # Generate a unique update ID
            update_id = f"update_{int(time.time())}"
            
            # Create the update record
            update = {
                "id": update_id,
                "thread_id": thread_id,
                "subject": subject,
                "goal": goal,
                "timestamp": datetime.datetime.now().isoformat(),
                "final_plan": final_plan,
                "contributing_platforms": list(ai_contributions.keys() if isinstance(ai_contributions, dict) else []),
                "capabilities_updated": self._extract_capabilities(subject, final_plan),
                "status": "applied"
            }
            
            # Save the update details to a file
            update_file = os.path.join(self.updates_dir, f"{update_id}.json")
            with open(update_file, 'w') as f:
                json.dump(update, f, indent=2)
            
            # Add to update history
            self.update_history.append({
                "id": update_id,
                "subject": subject,
                "timestamp": update["timestamp"],
                "capabilities_updated": update["capabilities_updated"]
            })
            
            # Save the updated history
            history_path = os.path.join(self.updates_dir, "update_history.json")
            with open(history_path, 'w') as f:
                json.dump(self.update_history, f, indent=2)
            
            self.logger.info(f"Applied training results from thread {thread_id} to AutoDev")
            
            return {
                "status": "success",
                "message": f"Successfully applied training results to AutoDev",
                "update_id": update_id,
                "capabilities_updated": update["capabilities_updated"]
            }
        
        except Exception as e:
            error_msg = f"Error applying training results: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"status": "error", "message": error_msg}
    
    def _extract_capabilities(self, subject, final_plan):
        """
        Extract the capabilities that were updated based on the subject and final plan
        """
        # This is a simplified implementation
        # In a real system, this would involve NLP analysis of the final plan
        
        capabilities = []
        
        # Simple keyword matching
        subject_lower = subject.lower()
        plan_lower = final_plan.lower()
        
        if "natural language" in subject_lower or "nlp" in subject_lower:
            capabilities.append("natural_language_processing")
            
            if "tokenization" in plan_lower:
                capabilities.append("text_tokenization")
            if "sentiment" in plan_lower:
                capabilities.append("sentiment_analysis")
            if "entity" in plan_lower or "extraction" in plan_lower:
                capabilities.append("entity_extraction")
                
        elif "api" in subject_lower:
            capabilities.append("api_integration")
            
            if "auth" in plan_lower or "oauth" in plan_lower:
                capabilities.append("authentication")
            if "retry" in plan_lower:
                capabilities.append("error_resilience")
            if "rate" in plan_lower and "limit" in plan_lower:
                capabilities.append("rate_limiting")
                
        elif "file" in subject_lower:
            capabilities.append("file_operations")
            
            if "large" in plan_lower:
                capabilities.append("large_file_handling")
            if "lock" in plan_lower:
                capabilities.append("concurrency_management")
            if "watch" in plan_lower:
                capabilities.append("file_watching")
                
        elif "browser" in subject_lower or "automation" in subject_lower:
            capabilities.append("browser_automation")
            
            if "captcha" in plan_lower:
                capabilities.append("captcha_solving")
            if "fingerprint" in plan_lower:
                capabilities.append("anti_detection")
                
        elif "error" in subject_lower:
            capabilities.append("error_handling")
            
            if "recovery" in plan_lower:
                capabilities.append("auto_recovery")
            if "logging" in plan_lower:
                capabilities.append("advanced_logging")
        
        # If no specific capabilities found, add a generic one
        if not capabilities:
            capabilities.append("general_intelligence")
            
        return capabilities
        
    def get_update_history(self, limit=None):
        """Get the history of updates applied to AutoDev"""
        if limit:
            return self.update_history[-limit:]
        return self.update_history
    
    def get_update_details(self, update_id):
        """Get detailed information about a specific update"""
        update_file = os.path.join(self.updates_dir, f"{update_id}.json")
        if os.path.exists(update_file):
            with open(update_file, 'r') as f:
                return json.load(f)
        return {"status": "error", "message": f"Update {update_id} not found"}