import os
import logging
import json
import datetime
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class RecommendationEngine:
    """
    Intelligent recommendation engine for Synapse Chamber
    Provides personalized training recommendations, resource suggestions,
    and optimization tips based on user behavior and training history
    """
    
    def __init__(self, memory_system):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.recommendations_dir = "data/recommendations"
        self.user_profile = self._load_user_profile()
        self.training_history = []
        
        # Ensure recommendations directory exists
        os.makedirs(self.recommendations_dir, exist_ok=True)
        
        # Load history data
        self.refresh_training_history()
    
    def refresh_training_history(self):
        """Refresh the training history data from memory system"""
        try:
            # Get all training threads
            threads = self.memory_system.get_threads(limit=100)
            if threads:
                self.training_history = threads
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error refreshing training history: {str(e)}")
            return False
    
    def get_personal_recommendations(self, limit=5):
        """
        Generate personalized recommendations based on user history and profile
        
        Returns:
            list: Top recommendation objects with title, description, type, and relevance score
        """
        if not self.training_history:
            self.refresh_training_history()
            
        if not self.training_history:
            # If still no history, return default recommendations
            return self._get_default_recommendations(limit)
        
        # Analyze training history
        completed_topics = set()
        topic_frequencies = Counter()
        all_goals = []
        
        for thread in self.training_history:
            subject = thread.get('subject', '')
            goal = thread.get('goal', '')
            final_plan = thread.get('final_plan', '')
            
            # Extract topics from thread
            if subject:
                topic_key = subject.lower().replace(' ', '_')
                if thread.get('final_plan'):  # If completed
                    completed_topics.add(topic_key)
                topic_frequencies[topic_key] += 1
            
            # Collect goals for content analysis
            if goal:
                all_goals.append(goal)
        
        # Generate recommendations based on patterns
        recommendations = []
        
        # 1. Suggest topics not yet explored
        all_topics = set(self._get_all_available_topics().keys())
        unexplored_topics = all_topics - completed_topics
        
        for topic in unexplored_topics:
            topic_info = self._get_topic_info(topic)
            if topic_info:
                relevance = self._calculate_topic_relevance(topic, topic_frequencies)
                recommendations.append({
                    'type': 'new_topic',
                    'title': f"Explore {topic_info['name']}",
                    'description': f"You haven't trained AutoDev on {topic_info['name']} yet. This could enhance its capabilities in {topic_info['description']}",
                    'action': 'start_training',
                    'action_params': {'topic': topic},
                    'relevance': relevance
                })
        
        # 2. Suggest advanced training on frequent topics
        common_topics = [topic for topic, count in topic_frequencies.most_common(3)]
        for topic in common_topics:
            if topic in completed_topics:
                topic_info = self._get_topic_info(topic)
                if topic_info:
                    recommendations.append({
                        'type': 'advanced_training',
                        'title': f"Advanced {topic_info['name']} Training",
                        'description': f"You've shown interest in {topic_info['name']}. Consider an advanced training session focused on specific use cases.",
                        'action': 'start_advanced_training',
                        'action_params': {'topic': topic},
                        'relevance': 0.85
                    })
        
        # 3. Analyze content for skill gap recommendations
        if all_goals:
            skill_gaps = self._analyze_content_for_skill_gaps(' '.join(all_goals))
            for skill, confidence in skill_gaps:
                recommendations.append({
                    'type': 'skill_gap',
                    'title': f"Enhance {skill} Skills",
                    'description': f"Based on your training goals, improving AutoDev's {skill} capabilities would be beneficial.",
                    'action': 'learn_skill',
                    'action_params': {'skill': skill},
                    'relevance': confidence
                })
        
        # 4. Add system improvement recommendations
        if len(self.training_history) > 5:
            recommendations.append({
                'type': 'system_improvement',
                'title': "Optimize Training Pipeline",
                'description': "With your training volume, optimizing the training pipeline could improve efficiency.",
                'action': 'optimize_system',
                'action_params': {'aspect': 'training_pipeline'},
                'relevance': 0.7
            })
        
        # Sort by relevance and return top recommendations
        sorted_recommendations = sorted(recommendations, key=lambda x: x['relevance'], reverse=True)
        return sorted_recommendations[:limit]
    
    def get_topic_recommendations(self, current_topic, limit=3):
        """
        Get recommendations for related topics based on the current topic
        
        Args:
            current_topic (str): The current topic key
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: Related topic recommendations
        """
        all_topics = self._get_all_available_topics()
        if current_topic not in all_topics:
            return []
            
        # Create a simple topic similarity map
        topic_similarities = {
            'natural_language': ['api_handling', 'error_handling'],
            'api_handling': ['natural_language', 'error_handling', 'automation'],
            'file_handling': ['error_handling', 'automation'],
            'automation': ['api_handling', 'file_handling'],
            'error_handling': ['natural_language', 'api_handling', 'file_handling']
        }
        
        # Get similar topics
        similar_topics = topic_similarities.get(current_topic, [])
        
        recommendations = []
        for topic in similar_topics:
            if topic in all_topics:
                topic_info = all_topics[topic]
                recommendations.append({
                    'type': 'related_topic',
                    'title': f"Related: {topic_info['name']}",
                    'description': f"{topic_info['name']} builds on concepts from {all_topics[current_topic]['name']}. {topic_info['description']}",
                    'action': 'start_training',
                    'action_params': {'topic': topic},
                    'relevance': 0.9
                })
                
        return recommendations[:limit]
    
    def get_performance_insights(self):
        """
        Analyze training performance and provide insights
        
        Returns:
            dict: Performance insights and recommendations
        """
        if not self.training_history:
            self.refresh_training_history()
            
        if not self.training_history:
            return {
                'insights': [],
                'performance_score': 0,
                'recommendation': "Start your first training session to get performance insights."
            }
        
        # Calculate success rate
        completed_threads = [t for t in self.training_history if t.get('final_plan')]
        success_rate = len(completed_threads) / len(self.training_history) if self.training_history else 0
        
        # Calculate average contributions per session
        total_contributions = sum(len(t.get('ai_contributions', {})) for t in self.training_history)
        avg_contributions = total_contributions / len(self.training_history) if self.training_history else 0
        
        # Generate insights
        insights = []
        
        if success_rate < 0.7:
            insights.append({
                'aspect': 'Success Rate',
                'status': 'needs_improvement',
                'message': f"Training success rate is {success_rate:.0%}. Consider simplifying training goals or reviewing error patterns."
            })
        else:
            insights.append({
                'aspect': 'Success Rate',
                'status': 'good',
                'message': f"Strong training completion rate of {success_rate:.0%}."
            })
            
        if avg_contributions < 2:
            insights.append({
                'aspect': 'AI Contributions',
                'status': 'needs_improvement',
                'message': f"Low average AI contributions ({avg_contributions:.1f}/session). Consider enabling more AI platforms in your sessions."
            })
        else:
            insights.append({
                'aspect': 'AI Contributions',
                'status': 'good',
                'message': f"Good diversity of AI input with {avg_contributions:.1f} contributions per session."
            })
        
        # Check platform diversity
        platforms_used = set()
        for thread in self.training_history:
            for conv in thread.get('conversations', []):
                if 'platform' in conv:
                    platforms_used.add(conv['platform'])
        
        if len(platforms_used) < 3:
            insights.append({
                'aspect': 'Platform Diversity',
                'status': 'needs_improvement',
                'message': f"Limited AI platform diversity. You're using {len(platforms_used)} out of 5 available platforms."
            })
        else:
            insights.append({
                'aspect': 'Platform Diversity',
                'status': 'good',
                'message': f"Good platform diversity with {len(platforms_used)} different AI platforms."
            })
        
        # Calculate overall performance score (0-100)
        performance_score = int((success_rate * 40) + (min(avg_contributions, 5)/5 * 30) + (min(len(platforms_used), 5)/5 * 30))
        
        # Generate overall recommendation
        if performance_score < 50:
            recommendation = "Focus on completing training sessions successfully and increasing AI platform diversity."
        elif performance_score < 75:
            recommendation = "You're on the right track. Consider exploring more advanced topics and specialized training modes."
        else:
            recommendation = "Excellent training performance. Consider contributing your successful approaches to AutoDev's own training methods."
        
        return {
            'insights': insights,
            'performance_score': performance_score,
            'recommendation': recommendation
        }
    
    def record_user_interaction(self, interaction_type, details):
        """
        Record user interaction to improve recommendations
        
        Args:
            interaction_type (str): Type of interaction (e.g., 'topic_selected', 'recommendation_clicked')
            details (dict): Details about the interaction
        """
        try:
            if not self.user_profile:
                self.user_profile = {
                    'interactions': [],
                    'preferences': {},
                    'last_updated': datetime.datetime.now().isoformat()
                }
            
            # Add the interaction
            interaction = {
                'type': interaction_type,
                'timestamp': datetime.datetime.now().isoformat(),
                'details': details
            }
            
            self.user_profile['interactions'].append(interaction)
            
            # Update preferences based on interaction
            if interaction_type == 'topic_selected':
                topic = details.get('topic')
                if topic:
                    self.user_profile['preferences'].setdefault('topics', {})
                    self.user_profile['preferences']['topics'].setdefault(topic, 0)
                    self.user_profile['preferences']['topics'][topic] += 1
            
            # Save the updated profile
            self._save_user_profile()
            
            return True
        except Exception as e:
            self.logger.error(f"Error recording user interaction: {str(e)}")
            return False
    
    def _load_user_profile(self):
        """Load user profile from file"""
        profile_path = os.path.join(self.recommendations_dir, "user_profile.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading user profile: {str(e)}")
        
        # Return empty profile if none exists or error
        return {
            'interactions': [],
            'preferences': {},
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def _save_user_profile(self):
        """Save user profile to file"""
        profile_path = os.path.join(self.recommendations_dir, "user_profile.json")
        try:
            # Update last_updated timestamp
            self.user_profile['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(profile_path, 'w') as f:
                json.dump(self.user_profile, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving user profile: {str(e)}")
            return False
    
    def _get_default_recommendations(self, limit=5):
        """Get default recommendations for new users"""
        recommendations = [
            {
                'type': 'new_topic',
                'title': "Start with Natural Language Processing",
                'description': "Begin training AutoDev with NLP capabilities, a foundational skill for AI interactions.",
                'action': 'start_training',
                'action_params': {'topic': 'natural_language'},
                'relevance': 0.95
            },
            {
                'type': 'system_setup',
                'title': "Complete Your AI Platform Setup",
                'description': "Ensure your AI platform credentials are configured for optimal training diversity.",
                'action': 'setup_platforms',
                'action_params': {},
                'relevance': 0.9
            },
            {
                'type': 'tutorial',
                'title': "Training Engine Tutorial",
                'description': "Learn how to get the most out of the Synapse Chamber training capabilities.",
                'action': 'view_tutorial',
                'action_params': {'tutorial': 'training_basics'},
                'relevance': 0.85
            },
            {
                'type': 'new_feature',
                'title': "Explore the Visualization Dashboard",
                'description': "Check out the new visualization dashboard for insights into your training sessions.",
                'action': 'view_dashboard',
                'action_params': {},
                'relevance': 0.8
            },
            {
                'type': 'community',
                'title': "Share Your Training Experience",
                'description': "Connect with others using Synapse Chamber to share training strategies.",
                'action': 'view_community',
                'action_params': {},
                'relevance': 0.7
            }
        ]
        
        return recommendations[:limit]
    
    def _get_all_available_topics(self):
        """Get all available training topics"""
        # This would normally fetch from a database or API
        # For now, return a hardcoded set of topics
        return {
            'natural_language': {
                'name': "Natural Language Processing",
                'description': "Training on text parsing, tokenization, and language understanding"
            },
            'api_handling': {
                'name': "API Integration & Authentication",
                'description': "Training on robust API connections, auth flows, and error handling"
            },
            'file_handling': {
                'name': "File System Operations",
                'description': "Training on file manipulation, parsing, and transformation"
            },
            'automation': {
                'name': "Browser & UI Automation",
                'description': "Training on browser control, CAPTCHA solving, and UI interaction"
            },
            'error_handling': {
                'name': "Error Detection & Recovery",
                'description': "Training on robust error handling, debugging, and self-recovery"
            }
        }
    
    def _get_topic_info(self, topic_key):
        """Get information about a specific topic"""
        return self._get_all_available_topics().get(topic_key)
    
    def _calculate_topic_relevance(self, topic, topic_frequencies):
        """Calculate relevance score for a topic based on user history"""
        # Simple algorithm: invert frequency (less used topics are more relevant as recommendations)
        total_sessions = sum(topic_frequencies.values())
        if total_sessions == 0:
            return 0.9  # High relevance for first-time users
            
        topic_frequency = topic_frequencies.get(topic, 0)
        # Topics never used get higher relevance
        if topic_frequency == 0:
            return 0.9
            
        # Otherwise, less frequently used topics get higher relevance
        return 0.9 - (topic_frequency / total_sessions * 0.5)
    
    def _analyze_content_for_skill_gaps(self, content):
        """
        Analyze content using NLP to identify potential skill gaps
        
        Args:
            content (str): The text content to analyze
            
        Returns:
            list: Tuples of (skill, confidence) sorted by confidence
        """
        if not content:
            return []
            
        # Tokenize and clean text
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(content.lower())
        filtered_tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
        
        # Simple keyword matching for skills
        skill_keywords = {
            'natural language processing': ['nlp', 'text', 'language', 'parsing', 'tokenization', 'sentiment'],
            'api integration': ['api', 'rest', 'endpoint', 'request', 'response', 'authentication'],
            'error handling': ['error', 'exception', 'try', 'catch', 'debugging', 'logging'],
            'data processing': ['data', 'processing', 'analysis', 'pandas', 'dataframe', 'visualization'],
            'automation': ['automation', 'browser', 'selenium', 'scraping', 'bot', 'captcha']
        }
        
        # Count keyword matches for each skill
        skill_matches = {}
        for skill, keywords in skill_keywords.items():
            matches = sum(1 for token in filtered_tokens if token in keywords)
            if matches > 0:
                skill_matches[skill] = matches
        
        # Normalize to confidence scores (0-1)
        max_matches = max(skill_matches.values()) if skill_matches else 1
        skill_scores = [(skill, min(matches / max_matches, 0.95)) for skill, matches in skill_matches.items()]
        
        # Sort by confidence (highest first)
        return sorted(skill_scores, key=lambda x: x[1], reverse=True)