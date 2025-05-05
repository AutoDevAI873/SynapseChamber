import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "synapse_chamber_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Debug info
logger.debug(f"Using database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize SQLAlchemy
db.init_app(app)

# Import components
from browser_automation import BrowserAutomation
from ai_controller import AIController
from captcha_solver import CAPTCHASolver
from memory_system import MemorySystem

# Initialize components
browser_automation = BrowserAutomation()
captcha_solver = CAPTCHASolver()
memory_system = MemorySystem()
ai_controller = AIController(browser_automation, captcha_solver, memory_system)

# Initialize Training Engine components
from training_engine import TrainingSessionManager, AutoDevUpdater
training_manager = TrainingSessionManager(ai_controller, memory_system)
autodev_updater = AutoDevUpdater(memory_system)

# Initialize advanced features
from recommendation_engine import RecommendationEngine
from analytics_system import AnalyticsSystem
from gamification_system import GamificationSystem
from assistant_chatbot import AssistantChatbot
from advanced_memory_system import AdvancedMemorySystem
from self_training_system import SelfTrainingSystem

# Create advanced components
recommendation_engine = RecommendationEngine(memory_system)
analytics_system = AnalyticsSystem(memory_system)
gamification_system = GamificationSystem(memory_system)
advanced_memory = AdvancedMemorySystem(memory_system)
assistant = AssistantChatbot(memory_system, recommendation_engine, analytics_system, gamification_system)
self_training = SelfTrainingSystem(training_manager, memory_system, analytics_system, ai_controller)

# Enable self-training (starts a background thread)
try:
    self_training.start()
    logger.info("Self-training system started")
except Exception as e:
    logger.error(f"Failed to start self-training system: {e}")

with app.app_context():
    import models
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai_interaction')
def ai_interaction():
    ai_platforms = ["gpt", "gemini", "deepseek", "claude", "grok"]
    return render_template('ai_interaction.html', ai_platforms=ai_platforms)

@app.route('/logs')
def logs():
    # Get conversation logs from memory system
    conversations = memory_system.get_conversations()
    return render_template('logs.html', conversations=conversations)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/training')
def training():
    # Get available training topics and modes
    topics = training_manager.get_available_topics()
    modes = training_manager.get_available_modes()
    
    # Get training sessions (threads) from memory system
    training_threads = memory_system.get_threads(limit=10)
    
    return render_template('training.html', 
                          topics=topics, 
                          modes=modes, 
                          training_threads=training_threads)

@app.route('/dashboard')
def dashboard():
    """Analytics Dashboard for visualizing training performance and metrics"""
    return render_template('dashboard.html')

# API Routes
@app.route('/api/start_interaction', methods=['POST'])
def start_interaction():
    data = request.json
    platform = data.get('platform')
    prompt = data.get('prompt')
    
    try:
        # Start the interaction with the specified AI platform
        result = ai_controller.interact_with_ai(platform, prompt)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error in interaction: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_conversation/<conversation_id>')
def get_conversation(conversation_id):
    try:
        conversation = memory_system.get_conversation(conversation_id)
        return jsonify({"status": "success", "conversation": conversation})
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    data = request.json
    try:
        # Update the settings
        browser_automation.update_settings(data.get('browser_settings', {}))
        captcha_solver.update_settings(data.get('captcha_settings', {}))
        memory_system.update_settings(data.get('memory_settings', {}))
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Training API routes
@app.route('/api/training/topics')
def get_training_topics():
    """Get all available training topics"""
    try:
        topics = training_manager.get_available_topics()
        return jsonify({"status": "success", "topics": topics})
    except Exception as e:
        logger.error(f"Error getting training topics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/training/modes')
def get_training_modes():
    """Get all available training modes"""
    try:
        modes = training_manager.get_available_modes()
        return jsonify({"status": "success", "modes": modes})
    except Exception as e:
        logger.error(f"Error getting training modes: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/training/start', methods=['POST'])
def start_training_session():
    """Start a new training session"""
    data = request.json
    try:
        topic = data.get('topic')
        mode = data.get('mode')
        platforms = data.get('platforms')
        goal = data.get('goal')
        
        if not topic:
            return jsonify({"status": "error", "message": "Topic is required"}), 400
        if not mode:
            return jsonify({"status": "error", "message": "Mode is required"}), 400
        
        result = training_manager.start_session(topic, mode, platforms, goal)
        return jsonify({"status": "success", "result": result})
    except ValueError as e:
        logger.error(f"Error in training session parameters: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error starting training session: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/training/status/<session_id>')
def get_training_status(session_id):
    """Get the status of a training session"""
    try:
        status = training_manager.get_session_status(session_id)
        return jsonify({"status": "success", "session_status": status})
    except Exception as e:
        logger.error(f"Error getting training status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/training/updates')
def get_training_updates():
    """Get the latest status updates from the current training session"""
    try:
        limit = request.args.get('limit', type=int)
        updates = training_manager.get_status_updates(limit)
        return jsonify({"status": "success", "updates": updates})
    except Exception as e:
        logger.error(f"Error getting training updates: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/autodev/apply_training', methods=['POST'])
def apply_training_to_autodev():
    """Apply training results to update AutoDev"""
    data = request.json
    try:
        thread_id = data.get('thread_id')
        if not thread_id:
            return jsonify({"status": "error", "message": "Thread ID is required"}), 400
        
        result = autodev_updater.apply_training_results(thread_id)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error applying training to AutoDev: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/autodev/updates')
def get_autodev_updates():
    """Get the history of updates applied to AutoDev"""
    try:
        limit = request.args.get('limit', type=int)
        updates = autodev_updater.get_update_history(limit)
        return jsonify({"status": "success", "updates": updates})
    except Exception as e:
        logger.error(f"Error getting AutoDev updates: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/autodev/update_details/<update_id>')
def get_autodev_update_details(update_id):
    """Get detailed information about a specific AutoDev update"""
    try:
        details = autodev_updater.get_update_details(update_id)
        return jsonify({"status": "success", "details": details})
    except Exception as e:
        logger.error(f"Error getting update details: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Analytics API routes
@app.route('/api/analytics/system_health')
def get_system_health():
    """Get current system health metrics"""
    try:
        health = analytics_system.get_system_health()
        return jsonify({"status": "success", "health": health})
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analytics/training_summary')
def get_training_summary():
    """Get summary of training metrics"""
    try:
        summary = analytics_system.get_training_summary()
        return jsonify({"status": "success", "summary": summary})
    except Exception as e:
        logger.error(f"Error getting training summary: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analytics/platform_comparison')
def get_platform_comparison():
    """Get comparative metrics for AI platforms"""
    try:
        comparison = analytics_system.get_platform_comparison()
        return jsonify({"status": "success", "comparison": comparison})
    except Exception as e:
        logger.error(f"Error getting platform comparison: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analytics/user_activity')
def get_user_activity():
    """Get user activity metrics"""
    try:
        activity = analytics_system.get_user_activity()
        return jsonify({"status": "success", "activity": activity})
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analytics/chart/<chart_type>')
def get_chart_data(chart_type):
    """Get chart data for a specific metric"""
    try:
        time_range = request.args.get('time_range', 'week')
        metric = request.args.get('metric', 'success_rate')
        
        if chart_type == 'performance':
            data = analytics_system.generate_performance_chart(metric, time_range)
        elif chart_type == 'topic_distribution':
            data = analytics_system.generate_topic_distribution_chart()
        elif chart_type == 'platform_comparison':
            data = analytics_system.generate_platform_comparison_chart(metric)
        elif chart_type == 'user_activity':
            data = analytics_system.generate_user_activity_heatmap()
        else:
            return jsonify({"status": "error", "message": f"Unknown chart type: {chart_type}"}), 400
            
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        logger.error(f"Error generating chart data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Recommendation API routes
@app.route('/api/recommendations/personal')
def get_personal_recommendations():
    """Get personalized recommendations"""
    try:
        limit = request.args.get('limit', 5, type=int)
        recommendations = recommendation_engine.get_personal_recommendations(limit=limit)
        return jsonify({"status": "success", "recommendations": recommendations})
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recommendations/topic/<topic>')
def get_topic_recommendations(topic):
    """Get recommendations for a specific topic"""
    try:
        limit = request.args.get('limit', 3, type=int)
        recommendations = recommendation_engine.get_topic_recommendations(topic, limit=limit)
        return jsonify({"status": "success", "recommendations": recommendations})
    except Exception as e:
        logger.error(f"Error getting topic recommendations: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Gamification API routes
@app.route('/api/gamification/profile')
def get_gamification_profile():
    """Get user's gamification profile"""
    try:
        profile = gamification_system.get_user_profile()
        return jsonify({"status": "success", "profile": profile})
    except Exception as e:
        logger.error(f"Error getting gamification profile: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gamification/leaderboard')
def get_leaderboard():
    """Get gamification leaderboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        leaderboard = gamification_system.get_leaderboard(limit=limit)
        return jsonify({"status": "success", "leaderboard": leaderboard})
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gamification/daily_challenge')
def get_daily_challenge():
    """Get daily challenge"""
    try:
        challenge = gamification_system.get_daily_challenge()
        return jsonify({"status": "success", "challenge": challenge})
    except Exception as e:
        logger.error(f"Error getting daily challenge: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gamification/complete_challenge', methods=['POST'])
def complete_challenge():
    """Complete a daily challenge"""
    try:
        data = request.json
        challenge_id = data.get('challenge_id')
        
        if not challenge_id:
            return jsonify({"status": "error", "message": "Challenge ID is required"}), 400
            
        result = gamification_system.complete_challenge(challenge_id)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error completing challenge: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Assistant API routes
@app.route('/api/assistant/chat', methods=['POST'])
def chat_with_assistant():
    """Send a message to the assistant and get a response"""
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context')
        
        if not message:
            return jsonify({"status": "error", "message": "Message is required"}), 400
            
        response = assistant.get_response(message, context)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        logger.error(f"Error chatting with assistant: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/assistant/history')
def get_assistant_history():
    """Get chat history with assistant"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = assistant.get_conversation_history(limit=limit)
        return jsonify({"status": "success", "history": history})
    except Exception as e:
        logger.error(f"Error getting assistant history: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Self-training API routes
@app.route('/api/self_training/status')
def get_self_training_status():
    """Get status of self-training system"""
    try:
        status = self_training.get_status()
        return jsonify({"status": "success", "self_training_status": status})
    except Exception as e:
        logger.error(f"Error getting self-training status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/self_training/capability_report')
def get_capability_report():
    """Get capability report from self-training system"""
    try:
        report = self_training.get_capability_report()
        return jsonify({"status": "success", "report": report})
    except Exception as e:
        logger.error(f"Error getting capability report: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/self_training/trigger', methods=['POST'])
def trigger_self_training():
    """Manually trigger self-training"""
    try:
        data = request.json
        topic = data.get('topic')
        mode = data.get('mode')
        platforms = data.get('platforms')
        goal = data.get('goal')
        
        if not topic:
            return jsonify({"status": "error", "message": "Topic is required"}), 400
            
        result = self_training.manually_trigger_training(topic, mode, platforms, goal)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error triggering self-training: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Advanced Memory API routes
@app.route('/api/memory/search', methods=['POST'])
def search_memory():
    """Search memory with query"""
    try:
        data = request.json
        query = data.get('query')
        memory_type = data.get('memory_type')
        limit = data.get('limit', 5)
        min_similarity = data.get('min_similarity', 0.3)
        
        if not query:
            return jsonify({"status": "error", "message": "Query is required"}), 400
            
        results = advanced_memory.retrieve_memory(query, memory_type, limit, min_similarity)
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/memory/context/<context_name>')
def get_memory_context(context_name):
    """Get memory context"""
    try:
        context = advanced_memory.get_context(context_name)
        if not context:
            return jsonify({"status": "error", "message": f"Context not found: {context_name}"}), 404
            
        return jsonify({"status": "success", "context": context})
    except Exception as e:
        logger.error(f"Error getting memory context: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/memory/sync', methods=['POST'])
def sync_memory():
    """Synchronize advanced memory with base memory"""
    try:
        results = advanced_memory.synchronize_with_base_memory()
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        logger.error(f"Error synchronizing memory: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
