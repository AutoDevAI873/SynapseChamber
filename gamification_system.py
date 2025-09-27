import os
import logging
import json
import datetime
import random
import time
from collections import defaultdict

class GamificationSystem:
    """
    Gamification system for Synapse Chamber
    
    Tracks achievements, points, levels, and badges to make
    the training process more engaging and rewarding
    """
    
    def __init__(self, memory_system):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self.gamification_dir = "data/gamification"
        self.user_data = {}
        
        # Ensure gamification directory exists
        os.makedirs(self.gamification_dir, exist_ok=True)
        
        # Load user data
        self._load_user_data()
        
        # Initialize achievements, badges, etc. if needed
        self._init_gamification_elements()
    
    def _load_user_data(self):
        """Load user gamification data from file"""
        user_data_path = os.path.join(self.gamification_dir, "user_data.json")
        if os.path.exists(user_data_path):
            try:
                with open(user_data_path, 'r') as f:
                    self.user_data = json.load(f)
                self.logger.info("Loaded user gamification data")
            except Exception as e:
                self.logger.error(f"Error loading user gamification data: {str(e)}")
                self._init_user_data()
        else:
            self._init_user_data()
    
    def _init_user_data(self):
        """Initialize user data structure"""
        self.user_data = {
            'points': 0,
            'level': 1,
            'achievements': [],
            'badges': [],
            'streaks': {
                'current': 0,
                'max': 0,
                'last_activity': None
            },
            'progress': {
                'topics_trained': [],
                'platforms_used': [],
                'sessions_completed': 0
            },
            'last_updated': datetime.datetime.now().isoformat()
        }
        self._save_user_data()
    
    def _save_user_data(self):
        """Save user data to file"""
        user_data_path = os.path.join(self.gamification_dir, "user_data.json")
        try:
            # Update timestamp
            self.user_data['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(user_data_path, 'w') as f:
                json.dump(self.user_data, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving user gamification data: {str(e)}")
            return False
    
    def _init_gamification_elements(self):
        """Initialize achievements, badges, and other elements"""
        # Define achievements if not already defined
        achievements_path = os.path.join(self.gamification_dir, "achievements.json")
        if not os.path.exists(achievements_path):
            achievements = [
                {
                    'id': 'first_training',
                    'name': 'First Steps',
                    'description': 'Complete your first training session',
                    'icon': 'baby-steps.svg',
                    'points': 50,
                    'condition': {
                        'type': 'sessions_completed',
                        'threshold': 1
                    }
                },
                {
                    'id': 'training_master',
                    'name': 'Training Master',
                    'description': 'Complete 10 training sessions',
                    'icon': 'master.svg',
                    'points': 200,
                    'condition': {
                        'type': 'sessions_completed',
                        'threshold': 10
                    }
                },
                {
                    'id': 'topic_explorer',
                    'name': 'Topic Explorer',
                    'description': 'Train on 3 different topics',
                    'icon': 'explorer.svg',
                    'points': 100,
                    'condition': {
                        'type': 'unique_topics',
                        'threshold': 3
                    }
                },
                {
                    'id': 'ai_diplomat',
                    'name': 'AI Diplomat',
                    'description': 'Use all available AI platforms',
                    'icon': 'diplomat.svg',
                    'points': 150,
                    'condition': {
                        'type': 'all_platforms',
                        'threshold': 5
                    }
                },
                {
                    'id': 'streak_week',
                    'name': 'Consistent Trainer',
                    'description': 'Maintain a 7-day training streak',
                    'icon': 'streak.svg',
                    'points': 300,
                    'condition': {
                        'type': 'streak',
                        'threshold': 7
                    }
                },
                {
                    'id': 'nlp_expert',
                    'name': 'NLP Expert',
                    'description': 'Complete 5 Natural Language Processing training sessions',
                    'icon': 'nlp.svg',
                    'points': 250,
                    'condition': {
                        'type': 'topic_sessions',
                        'topic': 'Natural Language Processing',
                        'threshold': 5
                    }
                },
                {
                    'id': 'api_master',
                    'name': 'API Master',
                    'description': 'Complete 5 API Integration training sessions',
                    'icon': 'api.svg',
                    'points': 250,
                    'condition': {
                        'type': 'topic_sessions',
                        'topic': 'API Integration',
                        'threshold': 5
                    }
                },
                {
                    'id': 'error_handler',
                    'name': 'Error Handler',
                    'description': 'Complete 5 Error Handling training sessions',
                    'icon': 'error.svg',
                    'points': 250,
                    'condition': {
                        'type': 'topic_sessions',
                        'topic': 'Error Handling',
                        'threshold': 5
                    }
                },
                {
                    'id': 'perfect_score',
                    'name': 'Perfect Score',
                    'description': 'Achieve a 100% success rate in training sessions (minimum 5 sessions)',
                    'icon': 'perfect.svg',
                    'points': 500,
                    'condition': {
                        'type': 'success_rate',
                        'threshold': 1.0,
                        'min_sessions': 5
                    }
                },
                {
                    'id': 'analytics_lover',
                    'name': 'Analytics Lover',
                    'description': 'View the analytics dashboard 10 times',
                    'icon': 'analytics.svg',
                    'points': 100,
                    'condition': {
                        'type': 'view_dashboard',
                        'threshold': 10
                    }
                }
            ]
            
            try:
                with open(achievements_path, 'w') as f:
                    json.dump(achievements, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving achievements data: {str(e)}")
        
        # Define badges if not already defined
        badges_path = os.path.join(self.gamification_dir, "badges.json")
        if not os.path.exists(badges_path):
            badges = [
                {
                    'id': 'novice',
                    'name': 'Novice Trainer',
                    'description': 'Awarded to users who reach level 5',
                    'icon': 'novice.svg',
                    'condition': {
                        'type': 'level',
                        'threshold': 5
                    }
                },
                {
                    'id': 'expert',
                    'name': 'Expert Trainer',
                    'description': 'Awarded to users who reach level 15',
                    'icon': 'expert.svg',
                    'condition': {
                        'type': 'level',
                        'threshold': 15
                    }
                },
                {
                    'id': 'master',
                    'name': 'Master Trainer',
                    'description': 'Awarded to users who reach level 30',
                    'icon': 'master.svg',
                    'condition': {
                        'type': 'level',
                        'threshold': 30
                    }
                },
                {
                    'id': 'achievement_hunter',
                    'name': 'Achievement Hunter',
                    'description': 'Earn 5 achievements',
                    'icon': 'hunter.svg',
                    'condition': {
                        'type': 'achievements_count',
                        'threshold': 5
                    }
                },
                {
                    'id': 'platform_master_gpt',
                    'name': 'GPT Master',
                    'description': 'Complete 10 sessions using GPT',
                    'icon': 'gpt.svg',
                    'condition': {
                        'type': 'platform_sessions',
                        'platform': 'gpt',
                        'threshold': 10
                    }
                },
                {
                    'id': 'platform_master_claude',
                    'name': 'Claude Master',
                    'description': 'Complete 10 sessions using Claude',
                    'icon': 'claude.svg',
                    'condition': {
                        'type': 'platform_sessions',
                        'platform': 'claude',
                        'threshold': 10
                    }
                },
                {
                    'id': 'platform_master_gemini',
                    'name': 'Gemini Master',
                    'description': 'Complete 10 sessions using Gemini',
                    'icon': 'gemini.svg',
                    'condition': {
                        'type': 'platform_sessions',
                        'platform': 'gemini',
                        'threshold': 10
                    }
                },
                {
                    'id': 'top_contributor',
                    'name': 'Top Contributor',
                    'description': 'Have one of your training sessions significantly improve AutoDev',
                    'icon': 'contributor.svg',
                    'condition': {
                        'type': 'special',
                        'special_type': 'top_contribution'
                    }
                }
            ]
            
            try:
                with open(badges_path, 'w') as f:
                    json.dump(badges, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving badges data: {str(e)}")
        
        # Define levels if not already defined
        levels_path = os.path.join(self.gamification_dir, "levels.json")
        if not os.path.exists(levels_path):
            # Create exponential level requirements
            levels = []
            for i in range(1, 51):  # 50 levels
                # Base XP is 100, each level requires 20% more than the previous
                required_points = int(100 * (1.2 ** (i-1)))
                levels.append({
                    'level': i,
                    'name': f"Level {i}",
                    'points_required': required_points,
                    'reward': {
                        'type': 'feature_unlock' if i <= 10 else 'points_bonus',
                        'value': f"feature_{i}" if i <= 10 else i * 10
                    }
                })
            
            try:
                with open(levels_path, 'w') as f:
                    json.dump(levels, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving levels data: {str(e)}")
    
    def _get_achievements(self):
        """Load all achievements from file"""
        achievements_path = os.path.join(self.gamification_dir, "achievements.json")
        try:
            with open(achievements_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading achievements: {str(e)}")
            return []
    
    def _get_badges(self):
        """Load all badges from file"""
        badges_path = os.path.join(self.gamification_dir, "badges.json")
        try:
            with open(badges_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading badges: {str(e)}")
            return []
    
    def _get_levels(self):
        """Load all level definitions from file"""
        levels_path = os.path.join(self.gamification_dir, "levels.json")
        try:
            with open(levels_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading levels: {str(e)}")
            return []
    
    def update_from_training_session(self, session_data):
        """
        Update gamification based on a completed training session
        
        Args:
            session_data (dict): Data about the completed training session
            
        Returns:
            dict: Updates including points, achievements, etc.
        """
        updates = {
            'points_earned': 0,
            'new_achievements': [],
            'new_badges': [],
            'level_up': False,
            'streak_update': None
        }
        
        # Award points for completing a session
        base_points = 50
        success_bonus = 50 if session_data.get('status') == 'completed' else 0
        complexity_bonus = len(session_data.get('conversations', [])) * 5
        
        points_earned = base_points + success_bonus + complexity_bonus
        updates['points_earned'] = points_earned
        
        # Update user data
        self.user_data['points'] += points_earned
        
        # Update progress tracking
        if session_data.get('status') == 'completed':
            self.user_data['progress']['sessions_completed'] += 1
            
            # Track topic
            topic = session_data.get('subject', '')
            if topic and topic not in self.user_data['progress']['topics_trained']:
                self.user_data['progress']['topics_trained'].append(topic)
            
            # Track platforms
            for conv in session_data.get('conversations', []):
                if 'platform' in conv and conv['platform'] not in self.user_data['progress']['platforms_used']:
                    self.user_data['progress']['platforms_used'].append(conv['platform'])
        
        # Update streak
        streak_update = self._update_streak()
        if streak_update:
            updates['streak_update'] = streak_update
        
        # Check for new achievements
        new_achievements = self._check_achievements()
        if new_achievements:
            updates['new_achievements'] = new_achievements
            
            # Add achievement points
            for achievement_id in new_achievements:
                achievement = self._get_achievement_by_id(achievement_id)
                if achievement:
                    self.user_data['points'] += achievement.get('points', 0)
                    updates['points_earned'] += achievement.get('points', 0)
        
        # Check for level up
        old_level = self.user_data['level']
        new_level = self._calculate_level()
        if new_level > old_level:
            self.user_data['level'] = new_level
            updates['level_up'] = True
            updates['new_level'] = new_level
        
        # Check for new badges
        new_badges = self._check_badges()
        if new_badges:
            updates['new_badges'] = new_badges
        
        # Save updated user data
        self._save_user_data()
        
        return updates
    
    def _update_streak(self):
        """
        Update the user's activity streak
        
        Returns:
            dict: Streak update information if there's a change
        """
        today = datetime.date.today().isoformat()
        
        # Get last activity date
        last_activity = self.user_data['streaks']['last_activity']
        
        if not last_activity or last_activity == today:
            # Already logged today, no change
            self.user_data['streaks']['last_activity'] = today
            return None
        
        # Convert last activity to date object
        try:
            last_date = datetime.date.fromisoformat(last_activity)
            today_date = datetime.date.today()
            
            # Check if yesterday
            if (today_date - last_date).days == 1:
                # Streak continues
                self.user_data['streaks']['current'] += 1
                if self.user_data['streaks']['current'] > self.user_data['streaks']['max']:
                    self.user_data['streaks']['max'] = self.user_data['streaks']['current']
                    
                self.user_data['streaks']['last_activity'] = today
                return {
                    'type': 'continue',
                    'current': self.user_data['streaks']['current'],
                    'is_record': self.user_data['streaks']['current'] == self.user_data['streaks']['max']
                }
            elif (today_date - last_date).days > 1:
                # Streak broken
                old_streak = self.user_data['streaks']['current']
                self.user_data['streaks']['current'] = 1
                self.user_data['streaks']['last_activity'] = today
                return {
                    'type': 'reset',
                    'old_streak': old_streak,
                    'current': 1
                }
        except Exception as e:
            self.logger.error(f"Error updating streak: {str(e)}")
            
        # Default: set today as last activity
        self.user_data['streaks']['last_activity'] = today
        return None
    
    def _calculate_level(self):
        """
        Calculate user level based on points
        
        Returns:
            int: Current level based on points
        """
        levels = self._get_levels()
        current_points = self.user_data['points']
        
        # Find the highest level where the user has enough points
        current_level = 1
        for level in levels:
            if current_points >= level['points_required']:
                current_level = level['level']
            else:
                break
        
        return current_level
    
    def _check_achievements(self):
        """
        Check for newly unlocked achievements
        
        Returns:
            list: IDs of newly unlocked achievements
        """
        achievements = self._get_achievements()
        already_earned = self.user_data['achievements']
        newly_earned = []
        
        for achievement in achievements:
            # Skip already earned achievements
            if achievement['id'] in already_earned:
                continue
                
            # Check if conditions are met
            if self._check_achievement_condition(achievement['condition']):
                newly_earned.append(achievement['id'])
                self.user_data['achievements'].append(achievement['id'])
        
        return newly_earned
    
    def _check_achievement_condition(self, condition):
        """
        Check if a specific achievement condition is met
        
        Args:
            condition (dict): The achievement condition
            
        Returns:
            bool: Whether the condition is met
        """
        condition_type = condition.get('type')
        threshold = condition.get('threshold', 0)
        
        if condition_type == 'sessions_completed':
            return self.user_data['progress']['sessions_completed'] >= threshold
            
        elif condition_type == 'unique_topics':
            return len(self.user_data['progress']['topics_trained']) >= threshold
            
        elif condition_type == 'all_platforms':
            return len(self.user_data['progress']['platforms_used']) >= threshold
            
        elif condition_type == 'streak':
            return self.user_data['streaks']['current'] >= threshold or self.user_data['streaks']['max'] >= threshold
            
        elif condition_type == 'topic_sessions':
            topic = condition.get('topic', '')
            # Would need more detailed tracking to implement this properly
            # For now, we'll simulate with random numbers
            topic_sessions = random.randint(0, 10)  # Simulated
            return topic_sessions >= threshold
            
        elif condition_type == 'success_rate':
            min_sessions = condition.get('min_sessions', 1)
            if self.user_data['progress']['sessions_completed'] < min_sessions:
                return False
                
            # Would need more detailed tracking for actual calculation
            # For now, we'll simulate with random success rate
            success_rate = random.uniform(0.7, 1.0)  # Simulated
            return success_rate >= threshold
            
        elif condition_type == 'view_dashboard':
            # Would need to track dashboard views
            # For now, return False (will be implemented when dashboard is viewed)
            return False
            
        return False
    
    def _check_badges(self):
        """
        Check for newly unlocked badges
        
        Returns:
            list: IDs of newly unlocked badges
        """
        badges = self._get_badges()
        already_earned = self.user_data['badges']
        newly_earned = []
        
        for badge in badges:
            # Skip already earned badges
            if badge['id'] in already_earned:
                continue
                
            # Check if conditions are met
            if self._check_badge_condition(badge['condition']):
                newly_earned.append(badge['id'])
                self.user_data['badges'].append(badge['id'])
        
        return newly_earned
    
    def get_user_data(self):
        """
        Get current user gamification data
        
        Returns:
            dict: Complete user gamification data
        """
        return self.user_data.copy()
    
    def get_achievements(self):
        """
        Get available achievements with user progress
        
        Returns:
            dict: Achievements data with user progress
        """
        try:
            all_achievements = self._get_achievements()
            user_achievements = self.user_data.get('achievements', [])
            
            # Add completion status to each achievement
            for achievement in all_achievements:
                achievement['completed'] = achievement['id'] in user_achievements
                achievement['progress'] = self._get_achievement_progress(achievement)
            
            return {
                'achievements': all_achievements,
                'completed_count': len(user_achievements),
                'total_count': len(all_achievements),
                'completion_rate': len(user_achievements) / len(all_achievements) if all_achievements else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting achievements: {str(e)}")
            return {
                'achievements': [],
                'completed_count': 0,
                'total_count': 0,
                'completion_rate': 0
            }
    
    def _get_achievement_progress(self, achievement):
        """
        Get progress towards a specific achievement
        
        Args:
            achievement (dict): Achievement definition
            
        Returns:
            dict: Progress information
        """
        condition = achievement.get('condition', {})
        condition_type = condition.get('type')
        threshold = condition.get('threshold', 0)
        
        progress = {
            'current': 0,
            'target': threshold,
            'percentage': 0,
            'description': 'Not started'
        }
        
        try:
            if condition_type == 'sessions_completed':
                current = self.user_data['progress']['sessions_completed']
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"{current}/{threshold} sessions completed"
                
            elif condition_type == 'unique_topics':
                current = len(self.user_data['progress']['topics_trained'])
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"{current}/{threshold} unique topics"
                
            elif condition_type == 'all_platforms':
                current = len(self.user_data['progress']['platforms_used'])
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"{current}/{threshold} platforms used"
                
            elif condition_type == 'streak':
                current = max(self.user_data['streaks']['current'], self.user_data['streaks']['max'])
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"{current}/{threshold} day streak"
                
            elif condition_type == 'level':
                current = self.user_data['level']
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"Level {current}/{threshold}"
                
            elif condition_type == 'achievements_count':
                current = len(self.user_data['achievements'])
                progress['current'] = current
                progress['percentage'] = min(100, (current / threshold) * 100) if threshold > 0 else 0
                progress['description'] = f"{current}/{threshold} achievements"
                
        except Exception as e:
            self.logger.error(f"Error calculating achievement progress: {str(e)}")
            
        return progress
    
    def _check_badge_condition(self, condition):
        """
        Check if a specific badge condition is met
        
        Args:
            condition (dict): The badge condition
            
        Returns:
            bool: Whether the condition is met
        """
        condition_type = condition.get('type')
        threshold = condition.get('threshold', 0)
        
        if condition_type == 'level':
            return self.user_data['level'] >= threshold
            
        elif condition_type == 'achievements_count':
            return len(self.user_data['achievements']) >= threshold
            
        elif condition_type == 'platform_sessions':
            platform = condition.get('platform', '')
            # Would need more detailed tracking to implement this properly
            # For now, we'll simulate with random numbers
            platform_sessions = random.randint(0, 15)  # Simulated
            return platform_sessions >= threshold
            
        elif condition_type == 'special':
            special_type = condition.get('special_type')
            if special_type == 'top_contribution':
                # Special badges would need custom implementation
                return False
                
        return False
    
    def _get_achievement_by_id(self, achievement_id):
        """Get a specific achievement by ID"""
        achievements = self._get_achievements()
        for achievement in achievements:
            if achievement['id'] == achievement_id:
                return achievement
        return None
    
    def _get_badge_by_id(self, badge_id):
        """Get a specific badge by ID"""
        badges = self._get_badges()
        for badge in badges:
            if badge['id'] == badge_id:
                return badge
        return None
    
    def record_activity(self, activity_type, details=None):
        """
        Record user activity for gamification purposes
        
        Args:
            activity_type (str): Type of activity (e.g., 'view_dashboard', 'start_training')
            details (dict, optional): Additional details about the activity
            
        Returns:
            dict: Updates including points, achievements, etc.
        """
        updates = {
            'points_earned': 0,
            'new_achievements': [],
            'new_badges': [],
            'level_up': False,
            'streak_update': None
        }
        
        # Award points based on activity type
        points_map = {
            'view_dashboard': 5,
            'start_training': 10,
            'apply_training': 15,
            'login': 5,
            'customize_settings': 5
        }
        
        points_earned = points_map.get(activity_type, 0)
        self.user_data['points'] += points_earned
        updates['points_earned'] = points_earned
        
        # Update streak if it's a significant activity
        if activity_type in ['start_training', 'apply_training', 'login']:
            streak_update = self._update_streak()
            if streak_update:
                updates['streak_update'] = streak_update
        
        # Handle specific activity types
        if activity_type == 'view_dashboard':
            # This would be tracked for the analytics_lover achievement
            pass
        
        # Check for new achievements
        new_achievements = self._check_achievements()
        if new_achievements:
            updates['new_achievements'] = new_achievements
            
            # Add achievement points
            for achievement_id in new_achievements:
                achievement = self._get_achievement_by_id(achievement_id)
                if achievement:
                    self.user_data['points'] += achievement.get('points', 0)
                    updates['points_earned'] += achievement.get('points', 0)
        
        # Check for level up
        old_level = self.user_data['level']
        new_level = self._calculate_level()
        if new_level > old_level:
            self.user_data['level'] = new_level
            updates['level_up'] = True
            updates['new_level'] = new_level
        
        # Check for new badges
        new_badges = self._check_badges()
        if new_badges:
            updates['new_badges'] = new_badges
        
        # Save updated user data
        self._save_user_data()
        
        return updates
    
    def get_user_profile(self):
        """
        Get the user's gamification profile
        
        Returns:
            dict: User profile with gamification data
        """
        # Calculate progress to next level
        levels = self._get_levels()
        current_level = self.user_data['level']
        current_points = self.user_data['points']
        
        next_level_points = 0
        current_level_points = 0
        
        for level in levels:
            if level['level'] == current_level:
                current_level_points = level['points_required']
            elif level['level'] == current_level + 1:
                next_level_points = level['points_required']
                break
        
        # Calculate progress percentage
        if next_level_points > current_level_points:
            points_needed = next_level_points - current_level_points
            points_earned = current_points - current_level_points
            level_progress = min(100, max(0, int((points_earned / points_needed) * 100)))
        else:
            level_progress = 100
        
        # Get completed achievements
        achievements = []
        all_achievements = self._get_achievements()
        for achievement_id in self.user_data['achievements']:
            achievement = self._get_achievement_by_id(achievement_id)
            if achievement:
                achievements.append({
                    'id': achievement['id'],
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'icon': achievement['icon'],
                    'points': achievement['points'],
                    'earned_at': "2023-06-15T10:30:00"  # Placeholder, would need actual tracking
                })
        
        # Get earned badges
        badges = []
        for badge_id in self.user_data['badges']:
            badge = self._get_badge_by_id(badge_id)
            if badge:
                badges.append({
                    'id': badge['id'],
                    'name': badge['name'],
                    'description': badge['description'],
                    'icon': badge['icon'],
                    'earned_at': "2023-06-15T10:30:00"  # Placeholder, would need actual tracking
                })
        
        # Get available achievements (not yet earned)
        available_achievements = []
        for achievement in all_achievements:
            if achievement['id'] not in self.user_data['achievements']:
                progress = self._get_achievement_progress(achievement)
                available_achievements.append({
                    'id': achievement['id'],
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'icon': achievement['icon'],
                    'points': achievement['points'],
                    'progress': progress,
                    'progress_text': self._get_achievement_progress_text(achievement)
                })
        
        return {
            'points': self.user_data['points'],
            'level': self.user_data['level'],
            'level_progress': level_progress,
            'points_to_next_level': next_level_points - current_points if next_level_points > current_points else 0,
            'achievements': achievements,
            'available_achievements': available_achievements,
            'badges': badges,
            'streak': {
                'current': self.user_data['streaks']['current'],
                'max': self.user_data['streaks']['max'],
                'last_activity': self.user_data['streaks']['last_activity']
            },
            'stats': {
                'sessions_completed': self.user_data['progress']['sessions_completed'],
                'topics_trained': len(self.user_data['progress']['topics_trained']),
                'platforms_used': len(self.user_data['progress']['platforms_used'])
            }
        }
    
    def _get_achievement_progress(self, achievement):
        """
        Get progress percentage for an achievement
        
        Args:
            achievement (dict): The achievement to check
            
        Returns:
            int: Progress percentage (0-100)
        """
        condition = achievement.get('condition', {})
        condition_type = condition.get('type')
        threshold = condition.get('threshold', 1)
        
        if condition_type == 'sessions_completed':
            current = self.user_data['progress']['sessions_completed']
            return min(100, int((current / threshold) * 100))
            
        elif condition_type == 'unique_topics':
            current = len(self.user_data['progress']['topics_trained'])
            return min(100, int((current / threshold) * 100))
            
        elif condition_type == 'all_platforms':
            current = len(self.user_data['progress']['platforms_used'])
            return min(100, int((current / threshold) * 100))
            
        elif condition_type == 'streak':
            current = max(self.user_data['streaks']['current'], self.user_data['streaks']['max'])
            return min(100, int((current / threshold) * 100))
            
        # For other types, we'd need more detailed tracking
        # For now, return a random progress for demonstration
        return random.randint(0, 90)
    
    def _get_achievement_progress_text(self, achievement):
        """
        Get human-readable progress text for an achievement
        
        Args:
            achievement (dict): The achievement to check
            
        Returns:
            str: Progress text
        """
        condition = achievement.get('condition', {})
        condition_type = condition.get('type')
        threshold = condition.get('threshold', 1)
        
        if condition_type == 'sessions_completed':
            current = self.user_data['progress']['sessions_completed']
            return f"{current}/{threshold} sessions completed"
            
        elif condition_type == 'unique_topics':
            current = len(self.user_data['progress']['topics_trained'])
            return f"{current}/{threshold} unique topics"
            
        elif condition_type == 'all_platforms':
            current = len(self.user_data['progress']['platforms_used'])
            return f"{current}/{threshold} platforms used"
            
        elif condition_type == 'streak':
            current = max(self.user_data['streaks']['current'], self.user_data['streaks']['max'])
            return f"{current}/{threshold} day streak"
            
        # For other types, we'd need more detailed tracking
        # For now, return a generic message
        return "Progress towards achievement"
    
    def get_leaderboard(self, limit=10):
        """
        Get simulated leaderboard data
        
        Args:
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Leaderboard entries
        """
        # In a real system, this would fetch data from multiple users
        # For now, simulate with random data plus the current user
        
        # Current user entry
        user_entry = {
            'id': 'current_user',
            'name': 'You',
            'points': self.user_data['points'],
            'level': self.user_data['level'],
            'achievements': len(self.user_data['achievements']),
            'is_current_user': True
        }
        
        # Generate simulated entries
        leaderboard = []
        for i in range(1, limit + 1):
            # Make simulated users stronger than the current user to encourage growth
            points = int(self.user_data['points'] * (1 + (random.uniform(0.1, 1.5) * (i < 5))))
            level = min(50, int(self.user_data['level'] * (1 + (random.uniform(0.1, 1.0) * (i < 5)))))
            achievements = min(10, int(len(self.user_data['achievements']) * (1 + (random.uniform(0.1, 1.0) * (i < 3)))))
            
            entry = {
                'id': f"user_{i}",
                'name': f"Trainer {i}",
                'points': points,
                'level': level,
                'achievements': achievements,
                'is_current_user': False
            }
            leaderboard.append(entry)
        
        # Add current user
        leaderboard.append(user_entry)
        
        # Sort by points (descending)
        leaderboard.sort(key=lambda x: x['points'], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard, 1):
            entry['rank'] = i
        
        # Limit to requested size
        return leaderboard[:limit]
    
    def get_daily_challenge(self):
        """
        Get a daily challenge for the user
        
        Returns:
            dict: Daily challenge information
        """
        # Get today's date to generate a consistent challenge for the day
        today = datetime.date.today().isoformat()
        
        # Generate a seed for random based on the date
        seed = hash(today) % 10000
        random.seed(seed)
        
        # Challenge categories
        categories = [
            'training',
            'exploration',
            'optimization',
            'analysis'
        ]
        
        # Challenge templates
        templates = {
            'training': [
                {
                    'title': 'Multi-AI Training',
                    'description': 'Complete a training session using at least 3 different AI platforms',
                    'reward': 100,
                    'type': 'multi_platform'
                },
                {
                    'title': 'Topic Master',
                    'description': 'Complete a training session on {topic}',
                    'reward': 75,
                    'type': 'specific_topic'
                }
            ],
            'exploration': [
                {
                    'title': 'Feature Explorer',
                    'description': 'Use the Analytics Dashboard to discover insights about your training patterns',
                    'reward': 50,
                    'type': 'use_feature'
                },
                {
                    'title': 'New Horizons',
                    'description': 'Train on a topic you haven\'t tried before',
                    'reward': 75,
                    'type': 'new_topic'
                }
            ],
            'optimization': [
                {
                    'title': 'Success Streak',
                    'description': 'Complete 2 training sessions with a 100% success rate',
                    'reward': 100,
                    'type': 'perfect_sessions'
                },
                {
                    'title': 'Quick Learner',
                    'description': 'Complete a training session in under 5 minutes',
                    'reward': 50,
                    'type': 'fast_training'
                }
            ],
            'analysis': [
                {
                    'title': 'Insight Finder',
                    'description': 'Review the performance of your AI platforms and identify the most accurate one',
                    'reward': 50,
                    'type': 'platform_analysis'
                },
                {
                    'title': 'Training History',
                    'description': 'Review your training history and apply a previous session to AutoDev',
                    'reward': 75,
                    'type': 'apply_previous'
                }
            ]
        }
        
        # Select a random category and template
        category = random.choice(categories)
        template = random.choice(templates[category])
        
        # Fill in template placeholders if needed
        if 'specific_topic' in template.get('type', ''):
            topics = ['Natural Language Processing', 'API Integration', 'File Handling', 'Error Handling', 'Automation']
            topic = random.choice(topics)
            template['description'] = template['description'].format(topic=topic)
        
        # Check if challenge is completed
        # In a real system, this would track actual completion
        completed = self._is_challenge_completed(template)
        
        return {
            'id': f"challenge_{today}_{category}",
            'title': template['title'],
            'description': template['description'],
            'category': category,
            'reward': template['reward'],
            'completed': completed,
            'expires': self._get_challenge_expiry()
        }
    
    def _is_challenge_completed(self, challenge):
        """
        Check if a challenge is completed
        
        Args:
            challenge (dict): The challenge to check
            
        Returns:
            bool: Whether the challenge is completed
        """
        # In a real system, this would check actual completion criteria
        # For now, return False as challenges need to be completed
        return False
    
    def _get_challenge_expiry(self):
        """
        Get expiry time for the daily challenge
        
        Returns:
            str: ISO format timestamp for challenge expiry
        """
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        midnight = datetime.datetime.combine(tomorrow, datetime.time.min)
        return midnight.isoformat()
    
    def complete_challenge(self, challenge_id):
        """
        Mark a challenge as completed and award points
        
        Args:
            challenge_id (str): ID of the challenge to complete
            
        Returns:
            dict: Result of completing the challenge
        """
        # Get today's challenge
        challenge = self.get_daily_challenge()
        
        # Check if this is the current challenge
        if challenge['id'] != challenge_id:
            return {
                'success': False,
                'message': 'Challenge not found or expired'
            }
        
        # Check if already completed
        if challenge['completed']:
            return {
                'success': False,
                'message': 'Challenge already completed'
            }
        
        # Award points
        points = challenge['reward']
        self.user_data['points'] += points
        
        # Save user data
        self._save_user_data()
        
        return {
            'success': True,
            'message': f"Challenge completed! You earned {points} points.",
            'points': points,
            'total_points': self.user_data['points']
        }