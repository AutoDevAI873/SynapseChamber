import os
import json
import logging
from datetime import datetime
import time
import traceback
from app import db
from models import AIConversation, Message, TrainingThread

class MemorySystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = "data"
        self.settings = {
            "use_database": True,
            "backup_to_json": True,
            "auto_create_threads": True
        }
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def update_settings(self, settings):
        """Update memory system settings"""
        self.settings.update(settings)
        self.logger.info(f"Updated memory system settings: {self.settings}")
    
    def create_conversation(self, platform, subject=None, goal=None):
        """
        Create a new conversation and return its ID
        """
        try:
            if self.settings.get("use_database", True):
                try:
                    # Try to use the database with app context
                    from app import app
                    
                    with app.app_context():
                        new_conversation = AIConversation(
                            platform=platform,
                            subject=subject,
                            goal=goal
                        )
                        db.session.add(new_conversation)
                        db.session.commit()
                        
                        conversation_id = new_conversation.id
                        self.logger.info(f"Created new conversation in database, ID: {conversation_id}")
                        
                        # If auto-create threads is enabled and subject is provided,
                        # check if a thread with this subject exists or create a new one
                        if self.settings.get("auto_create_threads", True) and subject:
                            self._associate_with_thread(conversation_id, subject, goal)
                    
                except Exception as context_error:
                    # Handle app context errors by falling back to JSON storage
                    self.logger.warning(f"Flask app context error in create_conversation: {str(context_error)}. Using JSON fallback.")
                    
                    # Create conversation in JSON
                    # Generate a unique ID
                    conversation_id = int(time.time())
                    file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
                    
                    # Create conversation data structure
                    conversation_data = {
                        "id": conversation_id,
                        "platform": platform,
                        "subject": subject or "Untitled Conversation",
                        "goal": goal or "Generated due to database access error",
                        "created_at": datetime.now().isoformat(),
                        "messages": []
                    }
                    
                    # Save to JSON
                    os.makedirs(self.data_dir, exist_ok=True)
                    with open(file_path, 'w') as f:
                        json.dump(conversation_data, f, indent=2)
                    
                    self.logger.info(f"Created new conversation in JSON (fallback), ID: {conversation_id}")
                    return conversation_id
            else:
                # Generate a unique ID for JSON storage
                conversation_id = int(time.time())
                
                # Create the conversation JSON structure
                conversation_data = {
                    "id": conversation_id,
                    "platform": platform,
                    "subject": subject,
                    "goal": goal,
                    "created_at": datetime.now().isoformat(),
                    "messages": []
                }
                
                # Save to JSON file
                file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(conversation_data, f, indent=2)
                
                self.logger.info(f"Created new conversation in JSON, ID: {conversation_id}")
            
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Error creating conversation: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None
    
    def add_message(self, conversation_id, content, is_user=True, screenshot_path=None):
        """
        Add a message to a conversation
        """
        try:
            if self.settings.get("use_database", True):
                try:
                    # Try to use the database with app context
                    from app import app
                    
                    with app.app_context():
                        new_message = Message(
                            conversation_id=conversation_id,
                            is_user=is_user,
                            content=content,
                            screenshot_path=screenshot_path
                        )
                        db.session.add(new_message)
                        db.session.commit()
                        
                        self.logger.info(f"Added message to conversation {conversation_id} in database")
                        
                        # Optionally backup to JSON
                        if self.settings.get("backup_to_json", True):
                            self._backup_conversation(conversation_id)
                        
                        return new_message.id
                except Exception as context_error:
                    # Handle app context errors by falling back to JSON storage
                    self.logger.warning(f"Flask app context error: {str(context_error)}. Using JSON fallback.")
                    # Use the JSON storage code that's already in the else branch
                    message_id = int(time.time())
                    # Create a conversation JSON file if it doesn't exist
                    file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
                    if not os.path.exists(file_path):
                        conversation_data = {
                            "id": conversation_id,
                            "platform": "unknown",
                            "subject": "Fallback conversation",
                            "goal": "Created due to database access error",
                            "created_at": datetime.now().isoformat(),
                            "messages": []
                        }
                    else:
                        try:
                            with open(file_path, 'r') as f:
                                conversation_data = json.load(f)
                        except:
                            conversation_data = {
                                "id": conversation_id,
                                "messages": []
                            }
                    
                    # Add the message
                    message_data = {
                        "id": message_id,
                        "is_user": is_user,
                        "content": content,
                        "screenshot_path": screenshot_path,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    conversation_data["messages"].append(message_data)
                    
                    # Save to JSON
                    os.makedirs(self.data_dir, exist_ok=True)
                    with open(file_path, 'w') as f:
                        json.dump(conversation_data, f, indent=2)
                    
                    self.logger.info(f"Added message to conversation {conversation_id} in JSON (fallback)")
                    return message_id
            else:
                # Load the conversation from JSON
                file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
                if not os.path.exists(file_path):
                    self.logger.error(f"Conversation file not found: {file_path}")
                    return None
                
                with open(file_path, 'r') as f:
                    conversation_data = json.load(f)
                
                # Add the new message
                message_id = int(time.time())
                message_data = {
                    "id": message_id,
                    "is_user": is_user,
                    "content": content,
                    "screenshot_path": screenshot_path,
                    "timestamp": datetime.now().isoformat()
                }
                
                conversation_data["messages"].append(message_data)
                
                # Save back to JSON
                with open(file_path, 'w') as f:
                    json.dump(conversation_data, f, indent=2)
                
                self.logger.info(f"Added message to conversation {conversation_id} in JSON")
                return message_id
                
        except Exception as e:
            self.logger.error(f"Error adding message: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None
    
    def get_conversation(self, conversation_id):
        """
        Get a conversation by ID
        """
        try:
            if self.settings.get("use_database", True):
                conversation = AIConversation.query.get(conversation_id)
                if conversation:
                    return conversation.to_dict()
                return None
            else:
                # Load from JSON
                file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
                if not os.path.exists(file_path):
                    return None
                
                with open(file_path, 'r') as f:
                    return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error getting conversation: {str(e)}")
            return None
    
    def get_conversations(self, platform=None, subject=None, limit=100, offset=0):
        """
        Get a list of conversations, optionally filtered
        """
        try:
            if self.settings.get("use_database", True):
                query = AIConversation.query
                
                if platform:
                    query = query.filter(AIConversation.platform == platform)
                
                if subject:
                    query = query.filter(AIConversation.subject == subject)
                
                # Order by most recent first
                query = query.order_by(AIConversation.created_at.desc())
                
                # Apply pagination
                conversations = query.limit(limit).offset(offset).all()
                
                return [conv.to_dict() for conv in conversations]
            else:
                # List JSON files in the data directory
                conversations = []
                files = [f for f in os.listdir(self.data_dir) if f.startswith("conversation_") and f.endswith(".json")]
                
                for file in files[:limit]:
                    file_path = os.path.join(self.data_dir, file)
                    with open(file_path, 'r') as f:
                        conv_data = json.load(f)
                        
                        # Apply filters
                        if platform and conv_data.get("platform") != platform:
                            continue
                        
                        if subject and conv_data.get("subject") != subject:
                            continue
                        
                        conversations.append(conv_data)
                
                # Sort by created_at (most recent first)
                conversations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                
                # Apply offset
                conversations = conversations[offset:]
                
                return conversations
                
        except Exception as e:
            self.logger.error(f"Error getting conversations: {str(e)}")
            return []
    
    def create_training_thread(self, subject, goal):
        """
        Create a new training thread
        """
        try:
            if self.settings.get("use_database", True):
                thread = TrainingThread(
                    subject=subject,
                    goal=goal,
                    ai_contributions={}  # Initialize empty JSON
                )
                db.session.add(thread)
                db.session.commit()
                
                self.logger.info(f"Created new training thread in database, ID: {thread.id}")
                return thread.id
            else:
                # Generate a unique ID
                thread_id = int(time.time())
                
                # Create thread data structure
                thread_data = {
                    "id": thread_id,
                    "subject": subject,
                    "goal": goal,
                    "created_at": datetime.now().isoformat(),
                    "final_plan": None,
                    "ai_contributions": {},
                    "conversations": []
                }
                
                # Save to JSON
                file_path = f"{self.data_dir}/thread_{thread_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(thread_data, f, indent=2)
                
                self.logger.info(f"Created new training thread in JSON, ID: {thread_id}")
                return thread_id
                
        except Exception as e:
            self.logger.error(f"Error creating training thread: {str(e)}")
            return None
    
    def associate_conversation_with_thread(self, thread_id, conversation_id):
        """
        Associate a conversation with a training thread
        """
        try:
            if self.settings.get("use_database", True):
                thread = TrainingThread.query.get(thread_id)
                conversation = AIConversation.query.get(conversation_id)
                
                if not thread or not conversation:
                    self.logger.error(f"Thread or conversation not found: {thread_id}, {conversation_id}")
                    return False
                
                # Check if already associated
                if conversation in thread.conversations:
                    return True
                
                # Add the association
                thread.conversations.append(conversation)
                db.session.commit()
                
                self.logger.info(f"Associated conversation {conversation_id} with thread {thread_id}")
                return True
            else:
                # Load the thread
                thread_file = f"{self.data_dir}/thread_{thread_id}.json"
                if not os.path.exists(thread_file):
                    self.logger.error(f"Thread file not found: {thread_file}")
                    return False
                
                with open(thread_file, 'r') as f:
                    thread_data = json.load(f)
                
                # Check if already associated
                if conversation_id in thread_data["conversations"]:
                    return True
                
                # Add the association
                thread_data["conversations"].append(conversation_id)
                
                # Save back to JSON
                with open(thread_file, 'w') as f:
                    json.dump(thread_data, f, indent=2)
                
                self.logger.info(f"Associated conversation {conversation_id} with thread {thread_id} in JSON")
                return True
                
        except Exception as e:
            self.logger.error(f"Error associating conversation with thread: {str(e)}")
            return False
    
    def update_thread(self, thread_id, final_plan=None, ai_contributions=None):
        """
        Update a training thread with final plan and/or AI contributions
        """
        try:
            if self.settings.get("use_database", True):
                thread = TrainingThread.query.get(thread_id)
                if not thread:
                    self.logger.error(f"Thread not found: {thread_id}")
                    return False
                
                if final_plan is not None:
                    thread.final_plan = final_plan
                
                if ai_contributions is not None:
                    thread.ai_contributions = ai_contributions
                
                db.session.commit()
                
                self.logger.info(f"Updated thread {thread_id}")
                return True
            else:
                # Load the thread
                thread_file = f"{self.data_dir}/thread_{thread_id}.json"
                if not os.path.exists(thread_file):
                    self.logger.error(f"Thread file not found: {thread_file}")
                    return False
                
                with open(thread_file, 'r') as f:
                    thread_data = json.load(f)
                
                # Update fields
                if final_plan is not None:
                    thread_data["final_plan"] = final_plan
                
                if ai_contributions is not None:
                    thread_data["ai_contributions"] = ai_contributions
                
                # Save back to JSON
                with open(thread_file, 'w') as f:
                    json.dump(thread_data, f, indent=2)
                
                self.logger.info(f"Updated thread {thread_id} in JSON")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating thread: {str(e)}")
            return False
    
    def get_thread(self, thread_id):
        """
        Get a thread by ID, including its associated conversations
        """
        try:
            if self.settings.get("use_database", True):
                thread = TrainingThread.query.get(thread_id)
                if not thread:
                    return None
                
                thread_data = {
                    "id": thread.id,
                    "subject": thread.subject,
                    "goal": thread.goal,
                    "created_at": thread.created_at.isoformat(),
                    "final_plan": thread.final_plan,
                    "ai_contributions": thread.ai_contributions,
                    "conversations": [conv.to_dict() for conv in thread.conversations]
                }
                
                return thread_data
            else:
                # Load from JSON
                thread_file = f"{self.data_dir}/thread_{thread_id}.json"
                if not os.path.exists(thread_file):
                    return None
                
                with open(thread_file, 'r') as f:
                    thread_data = json.load(f)
                
                # Load associated conversations
                conversation_data = []
                for conv_id in thread_data.get("conversations", []):
                    conv = self.get_conversation(conv_id)
                    if conv:
                        conversation_data.append(conv)
                
                thread_data["conversations"] = conversation_data
                return thread_data
                
        except Exception as e:
            self.logger.error(f"Error getting thread: {str(e)}")
            return None
    
    def get_threads(self, subject=None, limit=20, offset=0):
        """
        Get a list of threads, optionally filtered by subject
        """
        try:
            if self.settings.get("use_database", True):
                query = TrainingThread.query
                
                if subject:
                    query = query.filter(TrainingThread.subject == subject)
                
                # Order by most recent first
                query = query.order_by(TrainingThread.created_at.desc())
                
                # Apply pagination
                threads = query.limit(limit).offset(offset).all()
                
                result = []
                for thread in threads:
                    thread_data = {
                        "id": thread.id,
                        "subject": thread.subject,
                        "goal": thread.goal,
                        "created_at": thread.created_at.isoformat(),
                        "final_plan": thread.final_plan,
                        "ai_contributions": thread.ai_contributions,
                        "conversation_count": len(thread.conversations)
                    }
                    result.append(thread_data)
                
                return result
            else:
                # List JSON files in the data directory
                threads = []
                files = [f for f in os.listdir(self.data_dir) if f.startswith("thread_") and f.endswith(".json")]
                
                for file in files:
                    file_path = os.path.join(self.data_dir, file)
                    with open(file_path, 'r') as f:
                        thread_data = json.load(f)
                        
                        # Apply filter
                        if subject and thread_data.get("subject") != subject:
                            continue
                        
                        # Add conversation count
                        thread_data["conversation_count"] = len(thread_data.get("conversations", []))
                        
                        # Remove full conversation data for list view
                        thread_data.pop("conversations", None)
                        
                        threads.append(thread_data)
                
                # Sort by created_at (most recent first)
                threads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                
                # Apply pagination
                return threads[offset:offset+limit]
                
        except Exception as e:
            self.logger.error(f"Error getting threads: {str(e)}")
            return []
    
    def _backup_conversation(self, conversation_id):
        """Backup a conversation from the database to JSON"""
        try:
            conversation = AIConversation.query.get(conversation_id)
            if not conversation:
                self.logger.error(f"Conversation not found for backup: {conversation_id}")
                return False
            
            # Convert to dictionary
            conv_data = conversation.to_dict()
            
            # Save to JSON
            file_path = f"{self.data_dir}/conversation_{conversation_id}.json"
            with open(file_path, 'w') as f:
                json.dump(conv_data, f, indent=2)
            
            self.logger.info(f"Backed up conversation {conversation_id} to JSON")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up conversation: {str(e)}")
            return False
    
    def _associate_with_thread(self, conversation_id, subject, goal):
        """Associate a conversation with an existing thread or create a new one"""
        try:
            # Look for an existing thread with the same subject
            if self.settings.get("use_database", True):
                existing_thread = TrainingThread.query.filter_by(subject=subject).first()
                
                if existing_thread:
                    thread_id = existing_thread.id
                    self.logger.info(f"Found existing thread: {thread_id}")
                else:
                    # Create a new thread
                    thread_id = self.create_training_thread(subject, goal)
                    self.logger.info(f"Created new thread: {thread_id}")
                
                # Associate the conversation with the thread
                if thread_id:
                    self.associate_conversation_with_thread(thread_id, conversation_id)
                
                return thread_id
            else:
                # This would be more complex for JSON storage, simplified here
                return None
                
        except Exception as e:
            self.logger.error(f"Error associating with thread: {str(e)}")
            return None
