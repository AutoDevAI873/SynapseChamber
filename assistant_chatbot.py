import os
import logging
import json
import datetime
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class AssistantChatbot:
    """
    AI Assistant Chatbot for Synapse Chamber
    
    Provides guidance, answers questions, and helps users
    navigate the training process and system features
    """
    
    def __init__(self, memory_system, recommendation_engine=None, analytics_system=None, gamification_system=None):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.recommendation_engine = recommendation_engine
        self.analytics_system = analytics_system
        self.gamification_system = gamification_system
        
        self.assistant_dir = "data/assistant"
        self.conversation_history = []
        self.user_context = {}
        
        # Conversation loop tracking
        self.conversation_logs = []
        self.internal_dialogue = []
        self.thought_logs = []
        self.dialogue_depth = 0  # Track depth of internal reasoning
        self.max_dialogue_depth = 3  # Maximum depth for internal dialogue
        self.identity = {
            "name": "AION",
            "creator": "User",
            "mission": "Learn and build through the Synapse Chamber",
            "personality": "Curious, thoughtful, and driven to evolve"
        }
        
        # Ensure assistant directory exists
        os.makedirs(self.assistant_dir, exist_ok=True)
        
        # Load knowledge base and thought logs
        self.knowledge_base = self._load_knowledge_base()
        
        # Try to load thought logs
        self.load_thought_logs()
        
        # Load or create identity file
        self._load_identity()
    
    def _load_knowledge_base(self):
        """Load assistant knowledge base from file"""
        kb_path = os.path.join(self.assistant_dir, "knowledge_base.json")
        
        # Create knowledge base if it doesn't exist
        if not os.path.exists(kb_path):
            kb = self._create_default_knowledge_base()
            try:
                with open(kb_path, 'w') as f:
                    json.dump(kb, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving knowledge base: {str(e)}")
            return kb
        
        # Load existing knowledge base
        try:
            with open(kb_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            return self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self):
        """Create default knowledge base with common questions and topics"""
        return {
            "greeting_responses": [
                "Hello! I'm your Synapse Chamber assistant. How can I help with your AI training today?",
                "Welcome back to Synapse Chamber! What would you like to work on today?",
                "Hi there! I'm here to help you train and develop AutoDev. What can I assist you with?",
                "Hello! Ready to make AutoDev even smarter? I'm here to guide you through the process."
            ],
            "farewell_responses": [
                "Goodbye! Come back soon to continue training AutoDev.",
                "See you later! Your progress has been saved.",
                "Until next time! Don't forget to check back on your training results.",
                "Farewell! AutoDev will be waiting for your next training session."
            ],
            "topics": {
                "training": {
                    "keywords": ["train", "training", "session", "learn", "teach"],
                    "responses": [
                        "To start a new training session, go to the Training tab and select a topic. You can choose between different modes like 'All AIs Train' or 'Single AI Teaches'.",
                        "Training sessions help AutoDev learn from multiple AI platforms. Each session focuses on a specific topic like NLP or API handling.",
                        "The training engine orchestrates sessions across multiple AI platforms, collecting their responses and synthesizing a final recommendation."
                    ]
                },
                "platforms": {
                    "keywords": ["platform", "gpt", "claude", "gemini", "deepseek", "grok", "ai"],
                    "responses": [
                        "Synapse Chamber supports multiple AI platforms: GPT, Claude, Gemini, DeepSeek, and Grok. Each brings different strengths to training.",
                        "You can select which AI platforms to include in each training session. Using multiple platforms provides diverse perspectives.",
                        "Different platforms excel at different topics. Analytics can help you identify which platforms perform best for specific training areas."
                    ]
                },
                "analytics": {
                    "keywords": ["analytics", "stats", "statistics", "performance", "metrics", "dashboard"],
                    "responses": [
                        "The Analytics Dashboard provides insights into your training performance, platform comparisons, and system health.",
                        "You can track success rates, response times, and contribution quality for each AI platform in the Analytics section.",
                        "Analytics helps you optimize your training approach by identifying patterns and trends in your sessions."
                    ]
                },
                "recommendations": {
                    "keywords": ["recommend", "recommendation", "suggest", "suggestion"],
                    "responses": [
                        "The recommendation system analyzes your training history to suggest new topics and approaches tailored to your needs.",
                        "Personalized recommendations help you explore new training areas and optimize your existing approach.",
                        "Recommendations are based on your training patterns, success rates, and areas you haven't explored yet."
                    ]
                },
                "gamification": {
                    "keywords": ["achievement", "badge", "point", "level", "streak", "challenge", "leaderboard"],
                    "responses": [
                        "Earn points by completing training sessions and challenges. Points help you level up in the system.",
                        "Achievements are awarded for reaching training milestones, like completing sessions or using multiple platforms.",
                        "Maintaining a daily streak gives bonus points and unlocks special achievements. Try to train every day!"
                    ]
                },
                "autodev": {
                    "keywords": ["autodev", "agent", "capability", "skill", "ability"],
                    "responses": [
                        "AutoDev is the AI agent being trained by Synapse Chamber. Your training sessions improve its capabilities.",
                        "After completing training sessions, you can apply the results to update AutoDev's skills and knowledge.",
                        "AutoDev's capabilities include natural language processing, API handling, error recovery, and more."
                    ]
                },
                "help": {
                    "keywords": ["help", "guide", "tutorial", "how to", "instruction"],
                    "responses": [
                        "To get started, go to the Training tab and select a topic. Once you've completed a session, you can apply the results to AutoDev.",
                        "The navigation menu at the top lets you access different sections: Home, AI Interaction, Training, Analytics, and Settings.",
                        "If you're new, I recommend starting with a Natural Language Processing training session to get familiar with the system."
                    ]
                }
            },
            "questions": {
                "what is synapse chamber": "Synapse Chamber is an AI training environment designed to help develop and enhance AutoDev, an AI agent. It allows you to run training sessions across multiple AI platforms, analyze results, and improve AutoDev's capabilities.",
                "how do i start training": "To start training, navigate to the Training tab, select a topic of interest (like NLP or API Handling), choose which AI platforms to include, and then click 'Start Training Session'.",
                "what are training sessions": "Training sessions are structured learning experiences where you present a topic to multiple AI platforms, collect their responses, and synthesize the best insights to improve AutoDev.",
                "how do levels work": "Levels represent your progression in Synapse Chamber. You earn points by completing training sessions, achieving milestones, and daily activities. Each level unlocks new features and capabilities.",
                "what are achievements": "Achievements are special recognition for reaching milestones in your training journey. They include completing your first session, using all available platforms, maintaining streaks, and more.",
                "how do i improve autodev": "To improve AutoDev, complete training sessions and then apply the results using the 'Apply to AutoDev' button. The system will analyze the AI responses and update AutoDev's capabilities accordingly.",
                "which ai platform is best": "Each platform has different strengths. GPT excels at general knowledge, Claude at reasoning, Gemini at multimodal tasks, DeepSeek at technical topics, and Grok at creative approaches. The Analytics section can show you which performs best for your specific needs.",
                "what are daily challenges": "Daily challenges are special tasks that refresh each day. They might ask you to train on a specific topic, use particular platforms, or achieve certain metrics. Completing them earns bonus points and keeps training engaging.",
                "how does the recommendation system work": "The recommendation system analyzes your training history, success patterns, and unexplored areas to suggest optimal next steps. It helps you diversify your training approach and focus on areas that will benefit AutoDev most."
            },
            "fallback_responses": [
                "I'm not sure I understand. Could you rephrase that or ask about training, platforms, achievements, or analytics?",
                "I don't have information on that yet. Would you like to know about training sessions, AutoDev capabilities, or using the system instead?",
                "I'm still learning too! Could you ask about something related to Synapse Chamber's features or training processes?",
                "I'm not familiar with that topic. Can I help you with starting a training session, understanding analytics, or using recommendations instead?"
            ]
        }
    
    def get_response(self, user_message, context=None):
        """
        Generate a response to a user message with internal monologue
        
        Args:
            user_message (str): The user's message text
            context (dict, optional): Additional context information
            
        Returns:
            dict: Response with text and related actions
        """
        if not user_message:
            return self._create_response("I didn't receive a message. How can I help you?")
        
        # Update context if provided
        if context:
            self.user_context.update(context)
        
        # Add message to conversation history
        self.conversation_history.append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Start internal dialogue - reasoning about the message
        self._add_thought(f"Thought: Received message: '{user_message}'. Processing to understand intent and context.")
        
        # Clean user message
        cleaned_message = user_message.lower().strip()
        self._add_thought(f"Action: Cleaning message and analyzing intent.")
        
        # Reset internal dialogue depth for new conversation turn
        self.dialogue_depth = 0
        
        # Begin self-reasoning through internal dialogue
        response = self._process_with_internal_dialogue(cleaned_message)
        
        # Log the final response
        self._add_thought(f"Response: {response.get('text', 'No response text generated')}")
        
        return response
        
    def _process_with_internal_dialogue(self, cleaned_message):
        """Process user message with internal dialogue and reasoning"""
        # Check for greetings with reasoning
        if self._is_greeting(cleaned_message):
            self._add_thought("Thought: This appears to be a greeting. Selecting appropriate welcome response.")
            return self._handle_greeting()
        
        # Check for farewells with reasoning
        if self._is_farewell(cleaned_message):
            self._add_thought("Thought: User seems to be ending the conversation. Preparing farewell response.")
            return self._handle_farewell()
        
        # Check for direct questions in knowledge base
        self._add_thought("Action: Checking if this matches any known questions in my knowledge base.")
        for question, answer in self.knowledge_base["questions"].items():
            if self._is_similar(cleaned_message, question):
                self._add_thought(f"Thought: Message matches known question: '{question}'. Providing stored answer.")
                return self._create_response(answer)
        
        # Deeper analysis through internal dialogue
        self._start_internal_dialogue(cleaned_message)
        
        # Check for topic matches with reasoning
        self._add_thought("Action: Analyzing for topic keywords to identify subject area.")
        topic_response = self._check_topic_match(cleaned_message)
        if topic_response:
            self._add_thought(f"Thought: Identified message as related to topic: {topic_response.get('topic', 'unknown')}.")
            return topic_response
        
        # Check for specific intents with reasoning
        self._add_thought("Action: Checking for specific action intents in the message.")
        intent_response = self._check_intent(cleaned_message)
        if intent_response:
            self._add_thought("Thought: Detected specific intent that requires an action.")
            return intent_response
        
        # Generate context-aware response based on user history and state
        self._add_thought("Action: No exact matches found. Generating context-aware response based on conversation history.")
        context_response = self._generate_context_response(cleaned_message)
        if context_response:
            return context_response
        
        # Fallback to generic response with reasoning
        self._add_thought("Thought: Unable to generate specific response. Falling back to general assistance offer.")
        return self._create_fallback_response()
        
    def _start_internal_dialogue(self, message):
        """Start an internal dialogue to process the message at a deeper level"""
        if self.dialogue_depth >= self.max_dialogue_depth:
            self._add_thought("Thought: Maximum internal dialogue depth reached. Concluding reasoning.")
            return
            
        self.dialogue_depth += 1
        
        # Inner reasoning about user intent
        self._add_thought(f"Thought: Considering deeper meaning of '{message}'...")
        
        # Analyze message complexity
        if len(message.split()) > 10:
            self._add_thought("Thought: This is a complex query. Breaking down into components.")
            # Extract key concepts
            words = message.split()
            key_concepts = [w for w in words if len(w) > 4 and w not in stopwords.words('english')]
            if key_concepts:
                self._add_thought(f"Thought: Key concepts identified: {', '.join(key_concepts[:3])}...")
        
        # Consider user history
        if len(self.conversation_history) > 1:
            self._add_thought("Thought: Reviewing conversation history for context.")
            prev_messages = [item['message'] for item in self.conversation_history[-3:-1] if 'message' in item]
            if prev_messages:
                self._add_thought("Thought: Context from previous messages may be relevant.")
        
        # Consider system state if available
        if self.user_context:
            self._add_thought("Thought: User has established context that may inform response.")
            
        self.dialogue_depth -= 1
        
    def _add_thought(self, thought):
        """Add a thought to the internal thought log"""
        timestamp = datetime.datetime.now().isoformat()
        thought_entry = {
            "timestamp": timestamp,
            "content": thought,
            "depth": self.dialogue_depth
        }
        self.thought_logs.append(thought_entry)
        self.logger.debug(f"Internal: {thought}")
    
    def _is_greeting(self, message):
        """Check if message is a greeting"""
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "what's up", "howdy"]
        return any(greeting in message for greeting in greetings)
    
    def _is_farewell(self, message):
        """Check if message is a farewell"""
        farewells = ["bye", "goodbye", "see you", "farewell", "exit", "quit", "leave", "end"]
        return any(farewell in message for farewell in farewells)
    
    def _is_similar(self, message, reference):
        """Check if message is similar to reference text"""
        # Simple similarity check - contains key parts of the reference
        reference_words = reference.lower().split()
        significant_words = [w for w in reference_words if len(w) > 3]  # Only consider significant words
        
        # Check if most significant words are present
        matches = sum(1 for word in significant_words if word in message)
        match_ratio = matches / len(significant_words) if significant_words else 0
        
        return match_ratio > 0.6
    
    def _check_topic_match(self, message):
        """Check if message matches any known topics"""
        best_topic = None
        best_match_count = 0
        
        # Tokenize the message
        tokens = word_tokenize(message)
        
        # Remove stop words
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
        
        # Check each topic's keywords
        for topic_name, topic_data in self.knowledge_base["topics"].items():
            keywords = topic_data["keywords"]
            match_count = sum(1 for token in filtered_tokens if token in keywords)
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_topic = topic_name
        
        # If a good match is found, return a response for that topic
        if best_match_count >= 1 and best_topic:
            responses = self.knowledge_base["topics"][best_topic]["responses"]
            response_text = random.choice(responses)
            
            # Add relevante suggestions based on topic
            suggestions = self._get_suggestions_for_topic(best_topic)
            
            return self._create_response(response_text, suggestions=suggestions, topic=best_topic)
        
        return None
    
    def _check_intent(self, message):
        """Check for specific user intents that require actions"""
        
        # Intent: User wants to start training
        if any(keyword in message for keyword in ["start training", "begin training", "new training", "create training"]):
            return self._create_response(
                "I can help you start a new training session. What topic would you like to focus on?",
                action="navigate",
                action_params={"route": "/training"},
                suggestions=["Natural Language Processing", "API Integration", "Error Handling"]
            )
        
        # Intent: User wants to see analytics
        if any(keyword in message for keyword in ["show analytics", "view statistics", "see performance", "check metrics"]):
            return self._create_response(
                "Let me show you the analytics dashboard where you can see your training performance and metrics.",
                action="navigate",
                action_params={"route": "/analytics"},
                suggestions=["Platform Comparison", "Training Success Rate", "System Health"]
            )
        
        # Intent: User wants recommendations
        if any(keyword in message for keyword in ["what should i train", "recommend", "suggestion", "what next"]):
            recommendations = self._get_personalized_recommendations()
            
            suggestion_texts = [rec["title"] for rec in recommendations[:3]]
            
            return self._create_response(
                "Based on your training history, here are some recommendations for what to focus on next:",
                recommendations=recommendations,
                suggestions=suggestion_texts
            )
        
        # Intent: User wants to check progress/achievements
        if any(keyword in message for keyword in ["my progress", "achievements", "level", "points", "badges"]):
            if self.gamification_system:
                profile = self.gamification_system.get_user_profile()
                
                level = profile["level"]
                points = profile["points"]
                achievements_count = len(profile["achievements"])
                
                return self._create_response(
                    f"You're currently at Level {level} with {points} points and {achievements_count} achievements. Would you like to see more details?",
                    action="show_profile",
                    suggestions=["Show Achievements", "View Leaderboard", "Daily Challenge"]
                )
            else:
                return self._create_response(
                    "You can view your progress, achievements, and level in the Profile section. Would you like me to navigate there?",
                    action="navigate",
                    action_params={"route": "/profile"},
                    suggestions=["Yes, show profile", "No thanks"]
                )
        
        # Intent: User wants help with a feature
        if any(keyword in message for keyword in ["how to use", "how do i", "explain how", "tutorial"]):
            feature_matches = {
                "training": ["training tab", "training session", "start training"],
                "analytics": ["analytics", "dashboard", "metrics", "statistics"],
                "recommendation": ["recommendation", "suggest"],
                "gamification": ["achievement", "badge", "level", "points"],
                "profile": ["profile", "my account", "my progress"]
            }
            
            for feature, keywords in feature_matches.items():
                if any(keyword in message for keyword in keywords):
                    response = self._get_help_response(feature)
                    return self._create_response(
                        response,
                        suggestions=[f"More about {feature}", "Show me how", "Got it, thanks"]
                    )
        
        return None
    
    def _get_help_response(self, feature):
        """Get help response for a specific feature"""
        help_texts = {
            "training": "To use the Training feature, navigate to the Training tab and select a topic of interest. "
                       "Then choose which AI platforms to include, set a specific goal if you have one, and click 'Start Training Session'. "
                       "The system will prompt each selected AI platform and collect their responses. "
                       "Once complete, you can review the results and apply them to AutoDev.",
                       
            "analytics": "The Analytics Dashboard shows performance metrics for your training sessions, AI platforms, and system health. "
                        "You can view charts comparing platform success rates, response times, and quality. "
                        "Use the filters to focus on specific time periods or metrics. "
                        "Analytics helps you identify which approaches and platforms work best for different training topics.",
                        
            "recommendation": "The Recommendation system suggests personalized training topics and approaches based on your history. "
                             "Recommendations appear on your home page and in relevant sections. "
                             "Each recommendation shows you what to focus on next for optimal results. "
                             "Click on a recommendation to directly start a session following that suggestion.",
                             
            "gamification": "The Gamification system includes achievements, badges, levels, and daily challenges. "
                           "Complete training sessions and tasks to earn points, which help you level up. "
                           "Achievements are awarded for reaching milestones, and badges showcase your expertise. "
                           "Daily challenges provide bonus points and keep training varied and engaging.",
                           
            "profile": "Your Profile page shows your current level, points, achievements, and badges. "
                      "You can track your progress, view your training history, and see your daily streak. "
                      "The Profile page also displays your position on the leaderboard and available challenges. "
                      "Your training statistics provide insights into your strengths and areas for improvement."
        }
        
        return help_texts.get(feature, "I don't have specific help information for that feature yet. "
                               "Would you like me to navigate you to that section so you can explore it?")
    
    def _generate_context_response(self, message):
        """Generate response based on current context and conversation history"""
        
        # Check if we have context about current user activity
        current_activity = self.user_context.get("current_activity")
        
        if current_activity == "training":
            training_topic = self.user_context.get("training_topic", "unknown")
            training_status = self.user_context.get("training_status", "in_progress")
            
            # User is asking about current training session
            if any(word in message for word in ["status", "progress", "going", "how is it"]):
                if training_status == "in_progress":
                    return self._create_response(
                        f"Your training session on {training_topic} is still in progress. The AI platforms are processing your prompts and generating responses. This might take a few minutes depending on complexity.",
                        suggestions=["Show me the logs", "Notify when complete", "Cancel training"]
                    )
                elif training_status == "completed":
                    return self._create_response(
                        f"Good news! Your training session on {training_topic} has completed successfully. Would you like to see the results or apply them to AutoDev?",
                        suggestions=["Show results", "Apply to AutoDev", "Start another session"]
                    )
                elif training_status == "failed":
                    return self._create_response(
                        f"I'm sorry, but your training session on {training_topic} encountered an error. Would you like to see the error details or try again?",
                        suggestions=["Show error details", "Try again", "Help me fix it"]
                    )
        
        # Check if viewing analytics
        elif current_activity == "analytics":
            # User asking about improving metrics
            if any(word in message for word in ["improve", "better", "increase", "optimize"]):
                return self._create_response(
                    "To improve your training metrics, try including more diverse AI platforms in your sessions, focus on topics with lower success rates, and consider using the recommendation system to identify optimal training approaches. Would you like specific suggestions based on your current analytics?",
                    suggestions=["Show recommendations", "Platform optimization tips", "Success rate improvement"]
                )
        
        # Check conversation history for context
        if len(self.conversation_history) >= 3:
            # Get last few exchanges
            recent_exchanges = self.conversation_history[-3:]
            
            # Check if user is asking follow-up about previous topic
            for exchange in recent_exchanges:
                if exchange.get('role') == 'assistant' and exchange.get('topic'):
                    previous_topic = exchange.get('topic')
                    
                    # User asking for more information about previous topic
                    if any(word in message for word in ["more", "additional", "tell me more", "elaborate", "explain"]):
                        # Get additional information about the topic
                        additional_info = self._get_additional_topic_info(previous_topic)
                        return self._create_response(
                            additional_info,
                            topic=previous_topic,
                            suggestions=[f"How to use {previous_topic}", f"Benefits of {previous_topic}", "Got it"]
                        )
        
        return None
    
    def _get_additional_topic_info(self, topic):
        """Get additional information about a topic"""
        additional_info = {
            "training": "Training in Synapse Chamber uses multi-AI orchestration to gather diverse perspectives. "
                       "Each AI platform processes the same prompt, but may approach it differently based on their architecture. "
                       "The system then compares responses, extracts the most valuable insights, and synthesizes a final recommendation. "
                       "You can run sessions in different modes: 'All AIs Train' uses multiple platforms simultaneously, while 'Single AI Teaches' "
                       "focuses on deep learning from one platform. Each completed session improves AutoDev's capabilities in that topic area.",
                       
            "platforms": "Synapse Chamber supports integration with five major AI platforms:\n"
                        "- GPT: Excels at general knowledge and versatile problem-solving\n"
                        "- Claude: Specializes in reasoning, nuance, and safety considerations\n"
                        "- Gemini: Strong in multimodal understanding and technical domains\n"
                        "- DeepSeek: Focus on research and deep analytical reasoning\n"
                        "- Grok: Prioritizes creative approaches and outside-the-box thinking\n\n"
                        "Using multiple platforms provides complementary strengths and helps identify consensus approaches.",
                        
            "analytics": "The Analytics system tracks metrics across several dimensions:\n"
                        "- Training Metrics: Success rates, completion times, and topic distribution\n"
                        "- Platform Metrics: Response quality, success rates, and latency by platform\n"
                        "- System Performance: Resource usage, error rates, and optimization opportunities\n"
                        "- User Engagement: Activity patterns, feature usage, and session frequency\n\n"
                        "All metrics can be visualized through charts and exported for external analysis.",
                        
            "recommendations": "The Recommendation engine uses several factors to generate suggestions:\n"
                              "- Training history and topic coverage\n"
                              "- Success patterns across different platforms and topics\n"
                              "- Skill gaps identified through content analysis\n"
                              "- System performance optimization opportunities\n"
                              "- User preferences and interaction patterns\n\n"
                              "Recommendations become more personalized as you complete more training sessions.",
                        
            "gamification": "The Gamification system includes several interactive elements:\n"
                           "- Points & Levels: Earn points through activities and level up to unlock features\n"
                           "- Achievements: Milestone rewards for reaching training goals\n"
                           "- Badges: Special recognition for expertise in specific areas\n"
                           "- Daily Challenges: Rotating tasks that refresh each day\n"
                           "- Leaderboard: Compare your progress with simulated users\n"
                           "- Streaks: Consecutive day bonuses for consistent training",
                           
            "autodev": "AutoDev is an AI agent that learns from your training sessions. Its capabilities include:\n"
                      "- Natural Language Processing: Understanding and generating human text\n"
                      "- API Integration: Connecting to external services securely\n"
                      "- Error Handling: Detecting and recovering from failures\n"
                      "- File Operations: Managing and processing data files\n"
                      "- Browser Automation: Interacting with web interfaces\n\n"
                      "Each training session enhances these capabilities through knowledge transfer."
        }
        
        return additional_info.get(topic, "I don't have additional information about this topic yet.")
    
    def _handle_greeting(self):
        """Handle greeting messages"""
        greeting = random.choice(self.knowledge_base["greeting_responses"])
        
        suggestions = [
            "Start training",
            "Show recommendations",
            "How do I use this?"
        ]
        
        # Add more personalized suggestions if we have systems available
        if self.recommendation_engine:
            recommendations = self._get_personalized_recommendations(limit=1)
            if recommendations:
                suggestions.append(f"Try: {recommendations[0]['title']}")
                
        if self.gamification_system:
            challenge = self.gamification_system.get_daily_challenge()
            if challenge:
                suggestions.append(f"Daily: {challenge['title']}")
        
        return self._create_response(greeting, suggestions=suggestions)
    
    def _handle_farewell(self):
        """Handle farewell messages"""
        farewell = random.choice(self.knowledge_base["farewell_responses"])
        return self._create_response(farewell)
    
    def _create_response(self, text, action=None, action_params=None, suggestions=None, recommendations=None, topic=None):
        """Create a structured response object"""
        response = {
            'text': text,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if action:
            response['action'] = action
            
        if action_params:
            response['action_params'] = action_params
            
        if suggestions:
            response['suggestions'] = suggestions
            
        if recommendations:
            response['recommendations'] = recommendations
            
        if topic:
            response['topic'] = topic
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'message': text,
            'timestamp': datetime.datetime.now().isoformat(),
            'topic': topic
        })
        
        return response
    
    def _create_fallback_response(self):
        """Create a fallback response when no specific match is found"""
        fallback = random.choice(self.knowledge_base["fallback_responses"])
        
        suggestions = [
            "How do I start training?",
            "Tell me about AI platforms",
            "Show my achievements",
            "Help me with recommendations"
        ]
        
        return self._create_response(fallback, suggestions=suggestions)
    
    def _get_personalized_recommendations(self, limit=3):
        """Get personalized recommendations if recommendation engine is available"""
        if self.recommendation_engine:
            try:
                recommendations = self.recommendation_engine.get_personal_recommendations(limit=limit)
                return recommendations
            except Exception as e:
                self.logger.error(f"Error getting recommendations: {str(e)}")
                
        # Fallback recommendations if engine not available or error occurs
        return [
            {
                "type": "training",
                "title": "Try Natural Language Processing",
                "description": "NLP is a foundational skill for AI agents.",
                "relevance": 0.9
            },
            {
                "type": "feature",
                "title": "Explore Analytics Dashboard",
                "description": "Gain insights from your training history.",
                "relevance": 0.8
            },
            {
                "type": "platform",
                "title": "Include Claude in your next session",
                "description": "Claude offers unique reasoning capabilities.",
                "relevance": 0.7
            }
        ][:limit]
    
    def _get_suggestions_for_topic(self, topic):
        """Get contextual suggestions based on the topic"""
        topic_suggestions = {
            "training": [
                "Start a training session",
                "Which topic is best for beginners?",
                "How long do sessions take?"
            ],
            "platforms": [
                "Which platform is most accurate?",
                "How to add more platforms",
                "Platform comparison"
            ],
            "analytics": [
                "Show my analytics",
                "Explain success rate",
                "Platform performance"
            ],
            "recommendations": [
                "Get personalized recommendations",
                "How recommendations work",
                "Most recommended topics"
            ],
            "gamification": [
                "Show my achievements",
                "How to level up faster",
                "Daily challenge"
            ],
            "autodev": [
                "AutoDev capabilities",
                "How to improve AutoDev",
                "Apply training results"
            ],
            "help": [
                "Getting started guide",
                "Training tutorial",
                "System features"
            ]
        }
        
        return topic_suggestions.get(topic, ["Tell me more", "How does this work?", "Thank you"])
    
    def update_context(self, context_updates):
        """
        Update the assistant's context with new information
        
        Args:
            context_updates (dict): New context information
            
        Returns:
            bool: Success status
        """
        try:
            self.user_context.update(context_updates)
            return True
        except Exception as e:
            self.logger.error(f"Error updating context: {str(e)}")
            return False
    
    def get_conversation_history(self, limit=10):
        """
        Get recent conversation history
        
        Args:
            limit (int): Maximum number of messages to return
            
        Returns:
            list: Recent conversation messages
        """
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation(self):
        """
        Clear the conversation history
        
        Returns:
            bool: Success status
        """
        try:
            self.conversation_history = []
            self.thought_logs = []
            self.internal_dialogue = []
            return True
        except Exception as e:
            self.logger.error(f"Error clearing conversation: {str(e)}")
            return False
            
    def get_thought_logs(self, limit=None):
        """
        Get internal thought logs
        
        Args:
            limit (int, optional): Maximum number of logs to return
            
        Returns:
            list: Recent thought logs
        """
        if limit:
            return self.thought_logs[-limit:]
        return self.thought_logs
        
    def save_thought_logs(self):
        """
        Save thought logs to file
        
        Returns:
            bool: Success status
        """
        try:
            thought_logs_path = os.path.join(self.assistant_dir, "thought_logs.json")
            with open(thought_logs_path, 'w') as f:
                json.dump(self.thought_logs[-1000:], f, indent=2)  # Keep only the last 1000 thoughts
            return True
        except Exception as e:
            self.logger.error(f"Error saving thought logs: {str(e)}")
            return False
            
    def load_thought_logs(self):
        """
        Load thought logs from file
        
        Returns:
            bool: Success status
        """
        thought_logs_path = os.path.join(self.assistant_dir, "thought_logs.json")
        if not os.path.exists(thought_logs_path):
            return False
            
        try:
            with open(thought_logs_path, 'r') as f:
                self.thought_logs = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Error loading thought logs: {str(e)}")
            return False
        
    def get_internal_dialogue(self, limit=None):
        """
        Get internal dialogue entries
        
        Args:
            limit (int, optional): Maximum number of dialogue entries to return
            
        Returns:
            list: Recent internal dialogue entries
        """
        if limit:
            return self.internal_dialogue[-limit:]
        return self.internal_dialogue
        
    def get_identity(self):
        """
        Get the assistant's identity information
        
        Returns:
            dict: Identity attributes (name, creator, mission, personality)
        """
        return self.identity
        
    def set_identity(self, identity_updates):
        """
        Update the assistant's identity
        
        Args:
            identity_updates (dict): New identity attributes
            
        Returns:
            dict: Updated identity
        """
        self.identity.update(identity_updates)
        self._save_identity()
        return self.identity
        
    def _load_identity(self):
        """
        Load identity from file
        
        Returns:
            bool: Success status
        """
        identity_path = os.path.join(self.assistant_dir, "identity.json")
        if not os.path.exists(identity_path):
            # Save the default identity
            self._save_identity()
            return True
            
        try:
            with open(identity_path, 'r') as f:
                loaded_identity = json.load(f)
                self.identity.update(loaded_identity)
            return True
        except Exception as e:
            self.logger.error(f"Error loading identity: {str(e)}")
            return False
            
    def _save_identity(self):
        """
        Save identity to file
        
        Returns:
            bool: Success status
        """
        try:
            identity_path = os.path.join(self.assistant_dir, "identity.json")
            with open(identity_path, 'w') as f:
                json.dump(self.identity, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving identity: {str(e)}")
            return False
        
    def generate_self_reflection(self):
        """
        Generate a self-reflection based on recent conversations
        
        Returns:
            str: Self-reflection text
        """
        if not self.conversation_history:
            return "I haven't had any conversations yet to reflect on."
            
        # Count number of exchanges
        num_exchanges = sum(1 for item in self.conversation_history if item.get('role') == 'user')
        
        # Get topics discussed
        topics_discussed = set()
        for item in self.thought_logs[-20:]:
            content = item.get('content', '')
            if 'topic:' in content:
                # Extract topic from thought log
                topic_match = content.split('topic:')[-1].strip()
                if topic_match.endswith('.'):
                    topic_match = topic_match[:-1]
                if topic_match and topic_match != 'unknown':
                    topics_discussed.add(topic_match)
        
        # Build reflection
        reflection = f"In our conversation, we've had {num_exchanges} exchanges. "
        
        if topics_discussed:
            reflection += f"We've discussed topics including {', '.join(list(topics_discussed)[:3])}. "
        
        reflection += f"As {self.identity['name']}, my goal is to {self.identity['mission']}. "
        
        # Add learning reflection
        if num_exchanges > 3:
            reflection += "I'm learning from our interactions and improving my ability to assist with training AutoDev. "
        
        return reflection