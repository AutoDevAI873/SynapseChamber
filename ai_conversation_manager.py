import os
import logging
import json
import time
import datetime
import random
from browser_automation import BrowserAutomation

class AIConversationManager:
    """
    AI-to-AI Conversation Manager for Synapse Chamber
    
    Enables AI platforms to talk to each other through browser automation.
    Implements:
    - Cross-platform AI conversations
    - Response parsing and memory storage
    - Conversation scheduling and orchestration
    - Knowledge transfer between AI systems
    """
    
    def __init__(self, memory_system, browser_automation=None):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.browser_automation = browser_automation or BrowserAutomation()
        
        # Create conversations directory
        self.conversations_dir = "data/ai_conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        # Load platforms and prompts
        self.available_platforms = ["claude", "gemini", "gpt", "grok", "deepseek"]
        self.conversation_history = []
        self.conversation_logs = []
        self.insights = []
        
        # Define conversation templates for different scenarios
        self.conversation_templates = {
            "knowledge_sharing": "I'd like you to act as an expert on {topic}. Please provide your most insightful understanding of {specific_aspect}. Include key concepts, best practices, and any recent developments.",
            "problem_solving": "Please help solve this problem: {problem_description}. Think step by step and explain your reasoning thoroughly.",
            "creative_ideation": "Generate innovative ideas for {topic}. Be specific, original, and explain why each idea would be valuable.",
            "critical_analysis": "Analyze the following concept critically: {concept}. Identify strengths, weaknesses, and potential improvements."
        }
        
        # Default prompt options
        self.default_prompt_options = {
            "max_tokens": 500,
            "temperature": 0.7,
            "include_references": True,
            "format": "detailed"
        }
    
    def start_conversation(self, topic, template_type="knowledge_sharing", platforms=None, specific_params=None):
        """
        Start a new AI-to-AI conversation on a given topic
        
        Args:
            topic (str): The conversation topic
            template_type (str): Type of conversation to initiate (knowledge_sharing, problem_solving, etc.)
            platforms (list): List of AI platforms to include, defaults to all available
            specific_params (dict): Additional parameters for the template
            
        Returns:
            dict: Conversation metadata including ID
        """
        try:
            # Set up conversation parameters
            conversation_id = f"conv_{int(time.time())}"
            platforms = platforms or self.available_platforms
            
            # Validate platforms
            valid_platforms = [p for p in platforms if p in self.available_platforms]
            if not valid_platforms:
                self.logger.error("No valid AI platforms specified")
                return {"error": "No valid AI platforms specified"}
            
            # Create initial prompt using template
            params = specific_params or {}
            params["topic"] = topic
            
            template = self.conversation_templates.get(template_type, self.conversation_templates["knowledge_sharing"])
            initial_prompt = self._fill_template(template, params)
            
            # Create conversation metadata
            conversation_data = {
                "id": conversation_id,
                "topic": topic,
                "template_type": template_type,
                "platforms": valid_platforms,
                "start_time": datetime.datetime.now().isoformat(),
                "status": "in_progress",
                "initial_prompt": initial_prompt,
                "responses": {},
                "insights": [],
                "summary": ""
            }
            
            # Save initial conversation data
            self._save_conversation(conversation_data)
            self.conversation_history.append(conversation_data)
            
            self.logger.info(f"Started new AI conversation on topic: {topic}")
            
            # Start the actual conversation process in a structured way
            return self._conduct_conversation(conversation_data)
            
        except Exception as e:
            self.logger.error(f"Error starting AI conversation: {str(e)}")
            return {"error": str(e)}
    
    def _conduct_conversation(self, conversation_data):
        """
        Conduct the actual conversation between AI platforms
        
        Args:
            conversation_data (dict): The conversation metadata
            
        Returns:
            dict: Updated conversation data with responses
        """
        try:
            conversation_id = conversation_data["id"]
            topic = conversation_data["topic"]
            platforms = conversation_data["platforms"]
            initial_prompt = conversation_data["initial_prompt"]
            
            self.logger.info(f"Conducting conversation {conversation_id} on {topic} with platforms: {', '.join(platforms)}")
            
            # Phase 1: Get initial responses from all platforms
            self._log_conversation_step(conversation_id, "Starting initial response collection from all platforms")
            
            for platform in platforms:
                try:
                    self._log_conversation_step(conversation_id, f"Querying {platform}...")
                    
                    # Send the initial prompt to the platform
                    response = self.browser_automation.send_prompt_to_platform(platform, initial_prompt)
                    
                    if response:
                        # Store the response
                        conversation_data["responses"][platform] = [{
                            "prompt": initial_prompt,
                            "response": response,
                            "timestamp": datetime.datetime.now().isoformat()
                        }]
                        
                        self._log_conversation_step(conversation_id, f"Received response from {platform}")
                        
                        # Store in memory system
                        self._store_response_in_memory(conversation_id, platform, initial_prompt, response)
                    else:
                        self._log_conversation_step(conversation_id, f"Failed to get response from {platform}")
                
                except Exception as e:
                    self.logger.error(f"Error querying {platform}: {str(e)}")
                    self._log_conversation_step(conversation_id, f"Error with {platform}: {str(e)}")
            
            # Phase 2: Cross-pollinate responses between platforms
            if len(platforms) > 1 and len(conversation_data["responses"]) > 1:
                self._cross_pollinate_responses(conversation_data)
            
            # Phase 3: Extract insights
            conversation_data["insights"] = self._extract_insights(conversation_data)
            
            # Phase 4: Generate summary
            conversation_data["summary"] = self._generate_summary(conversation_data)
            
            # Mark as completed
            conversation_data["status"] = "completed"
            conversation_data["end_time"] = datetime.datetime.now().isoformat()
            
            # Save final conversation data
            self._save_conversation(conversation_data)
            
            return conversation_data
            
        except Exception as e:
            self.logger.error(f"Error conducting conversation: {str(e)}")
            conversation_data["status"] = "error"
            conversation_data["error"] = str(e)
            self._save_conversation(conversation_data)
            return conversation_data
    
    def _cross_pollinate_responses(self, conversation_data):
        """
        Cross-pollinate responses between platforms to generate more insights
        
        Args:
            conversation_data (dict): The conversation data
        """
        try:
            conversation_id = conversation_data["id"]
            platforms = conversation_data["platforms"]
            
            self._log_conversation_step(conversation_id, "Starting cross-pollination of responses")
            
            # For each platform that responded
            for source_platform, responses in conversation_data["responses"].items():
                if not responses:
                    continue
                    
                source_response = responses[0]["response"]  # Get the initial response
                
                # Create a cross-pollination prompt
                cross_prompt = f"""Another AI assistant, {source_platform.upper()}, provided this response to our question about {conversation_data['topic']}:

{source_response}

Please review this response and add your own insights, corrections, or extensions. What would you add or modify to make this information more complete, accurate, or useful?"""
                
                # Send to other platforms
                for target_platform in platforms:
                    # Skip sending to the same platform
                    if target_platform == source_platform:
                        continue
                        
                    # Skip if the target platform didn't respond initially
                    if target_platform not in conversation_data["responses"]:
                        continue
                        
                    self._log_conversation_step(conversation_id, f"Sending {source_platform}'s response to {target_platform} for feedback")
                    
                    try:
                        response = self.browser_automation.send_prompt_to_platform(target_platform, cross_prompt)
                        
                        if response:
                            # Add this response to the conversation
                            if target_platform in conversation_data["responses"]:
                                conversation_data["responses"][target_platform].append({
                                    "prompt": cross_prompt,
                                    "response": response,
                                    "source_platform": source_platform,
                                    "timestamp": datetime.datetime.now().isoformat()
                                })
                            else:
                                conversation_data["responses"][target_platform] = [{
                                    "prompt": cross_prompt,
                                    "response": response,
                                    "source_platform": source_platform,
                                    "timestamp": datetime.datetime.now().isoformat()
                                }]
                            
                            self._log_conversation_step(conversation_id, f"Received feedback from {target_platform} on {source_platform}'s response")
                            
                            # Store in memory
                            self._store_response_in_memory(conversation_id, target_platform, cross_prompt, response, context={
                                "source_platform": source_platform,
                                "feedback_type": "cross_pollination"
                            })
                    
                    except Exception as e:
                        self.logger.error(f"Error in cross-pollination from {source_platform} to {target_platform}: {str(e)}")
                        self._log_conversation_step(conversation_id, f"Error in cross-pollination: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error in cross-pollination phase: {str(e)}")
    
    def _extract_insights(self, conversation_data):
        """
        Extract key insights from the conversation
        
        Args:
            conversation_data (dict): The conversation data
            
        Returns:
            list: Extracted insights
        """
        insights = []
        
        try:
            # Extract one key insight from each response
            for platform, responses in conversation_data["responses"].items():
                for response_data in responses:
                    response = response_data["response"]
                    
                    # Split response into sentences (simple approach)
                    sentences = response.split('.')
                    
                    # Find sentences that might contain insights (looking for indicators)
                    insight_indicators = ["important", "key", "critical", "essential", "significant", 
                                         "notably", "interestingly", "crucially", "fundamentally"]
                    
                    potential_insights = []
                    for sentence in sentences:
                        # Skip short sentences
                        if len(sentence.strip()) < 30:
                            continue
                            
                        # Check if sentence contains any insight indicators
                        if any(indicator in sentence.lower() for indicator in insight_indicators):
                            potential_insights.append(sentence.strip())
                    
                    # If no sentences with indicators found, just take a substantial sentence
                    if not potential_insights:
                        substantial_sentences = [s.strip() for s in sentences if len(s.strip()) > 60]
                        if substantial_sentences:
                            potential_insights = [substantial_sentences[0]]
                    
                    # Add the insights with attribution
                    for insight in potential_insights[:2]:  # Limit to 2 insights per response
                        if insight:
                            insights.append({
                                "platform": platform,
                                "text": insight + ".",  # Ensure period at end
                                "timestamp": response_data["timestamp"],
                                "source_type": "cross_pollination" if "source_platform" in response_data else "initial"
                            })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting insights: {str(e)}")
            return insights
    
    def _generate_summary(self, conversation_data):
        """
        Generate a summary of the entire conversation
        
        Args:
            conversation_data (dict): The conversation data
            
        Returns:
            str: Summary text
        """
        try:
            # Get stats
            platform_count = len(conversation_data["responses"])
            total_responses = sum(len(responses) for responses in conversation_data["responses"].values())
            insight_count = len(conversation_data["insights"])
            
            # Build summary text
            summary = f"AI Conversation on {conversation_data['topic']} included {platform_count} AI platforms with {total_responses} total exchanges. "
            
            # Add platform list
            platforms_list = ", ".join(conversation_data["responses"].keys())
            summary += f"Participating platforms: {platforms_list}. "
            
            # Add info about cross-pollination
            cross_responses = sum(1 for platform, responses in conversation_data["responses"].items() 
                               for response in responses if "source_platform" in response)
            if cross_responses > 0:
                summary += f"Included {cross_responses} cross-platform exchanges. "
            
            # Add insight count
            if insight_count > 0:
                summary += f"Generated {insight_count} key insights. "
            
            # Note strongest contributor (platform with most content)
            max_content = 0
            max_platform = None
            for platform, responses in conversation_data["responses"].items():
                content_length = sum(len(r["response"]) for r in responses)
                if content_length > max_content:
                    max_content = content_length
                    max_platform = platform
                    
            if max_platform:
                summary += f"{max_platform.capitalize()} provided the most extensive contributions. "
            
            return summary.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return f"Conversation on {conversation_data.get('topic', 'unknown topic')} completed with {len(conversation_data.get('responses', {}))} AI platforms."
    
    def _fill_template(self, template, params):
        """
        Fill a template string with parameters
        
        Args:
            template (str): Template string with {param} placeholders
            params (dict): Parameters to fill in
            
        Returns:
            str: Filled template
        """
        try:
            return template.format(**params)
        except KeyError as e:
            self.logger.error(f"Missing parameter for template: {e}")
            # Return template with missing parameters marked
            return template
        except Exception as e:
            self.logger.error(f"Error filling template: {str(e)}")
            return template
    
    def _save_conversation(self, conversation_data):
        """
        Save conversation data to file
        
        Args:
            conversation_data (dict): Conversation data to save
        """
        try:
            conversation_id = conversation_data["id"]
            file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
            
            with open(file_path, 'w') as f:
                json.dump(conversation_data, f, indent=2)
                
            self.logger.info(f"Saved conversation data to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving conversation data: {str(e)}")
    
    def _store_response_in_memory(self, conversation_id, platform, prompt, response, context=None):
        """
        Store an AI response in the memory system
        
        Args:
            conversation_id (str): The conversation ID
            platform (str): The AI platform name
            prompt (str): The prompt sent to the AI
            response (str): The AI's response
            context (dict, optional): Additional context
        """
        try:
            # Prepare metadata
            metadata = {
                "conversation_id": conversation_id,
                "platform": platform,
                "prompt": prompt,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add additional context if provided
            if context:
                metadata.update(context)
            
            # Store in memory system
            if hasattr(self.memory_system, 'store_memory'):
                memory_id = self.memory_system.store_memory(
                    content=response,
                    memory_type="ai_conversation",
                    metadata=metadata,
                    source=f"ai_platform:{platform}",
                    importance=0.7  # AI-to-AI conversations are important
                )
                
                self.logger.info(f"Stored {platform} response in memory with ID: {memory_id}")
                
        except Exception as e:
            self.logger.error(f"Error storing response in memory: {str(e)}")
    
    def _log_conversation_step(self, conversation_id, message):
        """
        Log a step in the conversation process
        
        Args:
            conversation_id (str): The conversation ID
            message (str): The log message
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "conversation_id": conversation_id,
            "timestamp": timestamp,
            "message": message
        }
        
        self.conversation_logs.append(log_entry)
        self.logger.info(f"[Conv: {conversation_id}] {message}")
    
    def get_conversation(self, conversation_id):
        """
        Get data for a specific conversation
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            dict: Conversation data, or None if not found
        """
        try:
            # Check in memory first
            for conv in self.conversation_history:
                if conv["id"] == conversation_id:
                    return conv
            
            # Check on disk
            file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
            return None
    
    def get_recent_conversations(self, limit=10):
        """
        Get a list of recent conversations
        
        Args:
            limit (int): Maximum number of conversations to return
            
        Returns:
            list: Recent conversations with basic metadata
        """
        try:
            conversations = []
            
            # Get conversations from history first
            conversations.extend(self.conversation_history)
            
            # Get additional conversations from disk if needed
            if len(conversations) < limit:
                try:
                    files = os.listdir(self.conversations_dir)
                    json_files = [f for f in files if f.endswith('.json')]
                    
                    # Sort by modification time (most recent first)
                    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.conversations_dir, x)), reverse=True)
                    
                    for json_file in json_files:
                        # Skip files we already have in memory
                        conv_id = json_file.replace('.json', '')
                        if any(c["id"] == conv_id for c in conversations):
                            continue
                            
                        # Load conversation data
                        file_path = os.path.join(self.conversations_dir, json_file)
                        with open(file_path, 'r') as f:
                            conv_data = json.load(f)
                            conversations.append(conv_data)
                            
                        # Stop if we have enough
                        if len(conversations) >= limit:
                            break
                
                except Exception as e:
                    self.logger.error(f"Error loading conversations from disk: {str(e)}")
            
            # Sort by start time (most recent first) and limit
            conversations.sort(key=lambda x: x.get("start_time", ""), reverse=True)
            
            # Return with only basic metadata for listings
            return [{
                "id": c["id"],
                "topic": c["topic"],
                "status": c["status"],
                "start_time": c["start_time"],
                "end_time": c.get("end_time"),
                "platforms": c["platforms"],
                "response_count": sum(len(responses) for responses in c.get("responses", {}).values()),
                "insight_count": len(c.get("insights", [])),
                "summary": c.get("summary", "")
            } for c in conversations[:limit]]
            
        except Exception as e:
            self.logger.error(f"Error retrieving recent conversations: {str(e)}")
            return []
    
    def get_insights_by_topic(self, topic, limit=20):
        """
        Get insights from conversations related to a specific topic
        
        Args:
            topic (str): The topic to search for
            limit (int): Maximum number of insights to return
            
        Returns:
            list: Relevant insights
        """
        try:
            all_insights = []
            topic_lower = topic.lower()
            
            # Go through conversation files
            files = os.listdir(self.conversations_dir)
            json_files = [f for f in files if f.endswith('.json')]
            
            for json_file in json_files:
                try:
                    # Load conversation data
                    file_path = os.path.join(self.conversations_dir, json_file)
                    with open(file_path, 'r') as f:
                        conv_data = json.load(f)
                    
                    # Check if related to topic
                    conv_topic = conv_data.get("topic", "").lower()
                    if topic_lower in conv_topic or any(topic_lower in keyword.lower() for keyword in conv_topic.split()):
                        # Add insights with conversation context
                        for insight in conv_data.get("insights", []):
                            insight_copy = dict(insight)
                            insight_copy["conversation_id"] = conv_data["id"]
                            insight_copy["conversation_topic"] = conv_data["topic"]
                            all_insights.append(insight_copy)
                
                except Exception as e:
                    self.logger.error(f"Error processing file {json_file}: {str(e)}")
            
            # Sort by timestamp (newest first) and limit
            all_insights.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return all_insights[:limit]
            
        except Exception as e:
            self.logger.error(f"Error retrieving insights for topic {topic}: {str(e)}")
            return []
    
    def schedule_conversation(self, topic, template_type="knowledge_sharing", platforms=None, 
                            specific_params=None, schedule_time=None):
        """
        Schedule an AI-to-AI conversation for future execution
        
        Args:
            topic (str): The conversation topic
            template_type (str): Type of conversation template
            platforms (list): List of AI platforms to include
            specific_params (dict): Additional parameters
            schedule_time (datetime): When to run the conversation, or None for immediate
            
        Returns:
            dict: Scheduled conversation info
        """
        try:
            # Create schedule entry
            schedule_id = f"sched_{int(time.time())}"
            
            scheduled_item = {
                "id": schedule_id,
                "topic": topic,
                "template_type": template_type,
                "platforms": platforms or self.available_platforms,
                "params": specific_params or {},
                "created_at": datetime.datetime.now().isoformat(),
                "scheduled_time": schedule_time.isoformat() if schedule_time else None,
                "status": "scheduled" if schedule_time else "pending",
                "conversation_id": None
            }
            
            # Save to schedule file
            schedule_file = os.path.join(self.conversations_dir, "scheduled_conversations.json")
            
            scheduled_items = []
            if os.path.exists(schedule_file):
                try:
                    with open(schedule_file, 'r') as f:
                        scheduled_items = json.load(f)
                except:
                    scheduled_items = []
            
            scheduled_items.append(scheduled_item)
            
            with open(schedule_file, 'w') as f:
                json.dump(scheduled_items, f, indent=2)
            
            self.logger.info(f"Scheduled conversation on topic {topic} with ID {schedule_id}")
            
            # If no specific time, run immediately
            if not schedule_time:
                conversation_data = self.start_conversation(
                    topic=topic,
                    template_type=template_type,
                    platforms=platforms,
                    specific_params=specific_params
                )
                
                # Update schedule with conversation ID
                if "id" in conversation_data and not "error" in conversation_data:
                    for item in scheduled_items:
                        if item["id"] == schedule_id:
                            item["status"] = "completed"
                            item["conversation_id"] = conversation_data["id"]
                            break
                    
                    # Save updated schedule
                    with open(schedule_file, 'w') as f:
                        json.dump(scheduled_items, f, indent=2)
                
                return {
                    "schedule_id": schedule_id,
                    "conversation_id": conversation_data.get("id"),
                    "status": "completed",
                    "message": "Conversation executed immediately"
                }
            
            return {
                "schedule_id": schedule_id,
                "status": "scheduled",
                "scheduled_time": schedule_time.isoformat() if schedule_time else None,
                "message": f"Conversation scheduled for {schedule_time.isoformat() if schedule_time else 'immediate execution'}"
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling conversation: {str(e)}")
            return {"error": str(e)}
    
    def process_scheduled_conversations(self):
        """
        Process any scheduled conversations that are due to run
        
        Returns:
            int: Number of conversations processed
        """
        try:
            schedule_file = os.path.join(self.conversations_dir, "scheduled_conversations.json")
            if not os.path.exists(schedule_file):
                return 0
                
            with open(schedule_file, 'r') as f:
                scheduled_items = json.load(f)
            
            now = datetime.datetime.now()
            processed_count = 0
            updated = False
            
            for item in scheduled_items:
                # Skip items that are not scheduled or already completed
                if item["status"] not in ["scheduled", "pending"]:
                    continue
                    
                # Check if it's time to run
                if item["scheduled_time"]:
                    scheduled_time = datetime.datetime.fromisoformat(item["scheduled_time"])
                    if scheduled_time > now:
                        continue  # Not time yet
                
                try:
                    # Run the conversation
                    self.logger.info(f"Running scheduled conversation: {item['id']}")
                    
                    conversation_data = self.start_conversation(
                        topic=item["topic"],
                        template_type=item["template_type"],
                        platforms=item["platforms"],
                        specific_params=item["params"]
                    )
                    
                    # Update schedule
                    item["status"] = "completed"
                    item["conversation_id"] = conversation_data.get("id")
                    item["completed_at"] = datetime.datetime.now().isoformat()
                    updated = True
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing scheduled conversation {item['id']}: {str(e)}")
                    item["status"] = "error"
                    item["error"] = str(e)
                    updated = True
            
            # Save updated schedule
            if updated:
                with open(schedule_file, 'w') as f:
                    json.dump(scheduled_items, f, indent=2)
            
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error processing scheduled conversations: {str(e)}")
            return 0