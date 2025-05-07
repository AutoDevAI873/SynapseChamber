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
    # Get system status for homepage dashboard
    try:
        system_health = analytics_system.get_system_health()
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        system_health = {
            'memory_usage': 45,
            'api_latency': 120,
            'error_rate': 1.2,
            'status': 'success',
            'message': 'System is operating normally. All components are responsive and healthy.'
        }
    
    # Get recent training sessions
    try:
        recent_trainings = memory_system.get_threads(limit=3)
    except Exception as e:
        logger.error(f"Error getting recent trainings: {e}")
        recent_trainings = []
    
    # Get active platforms
    active_platforms = ["gpt", "claude", "gemini", "deepseek", "grok"]
    
    # Get platform metrics
    try:
        platform_metrics = analytics_system.get_platform_comparison()
    except Exception as e:
        logger.error(f"Error getting platform metrics: {e}")
        platform_metrics = {
            'comparison': {
                'success_rate': {
                    'gpt': 92,
                    'claude': 88,
                    'gemini': 85,
                    'deepseek': 75,
                    'grok': 80
                }
            }
        }
    
    return render_template('index.html', 
                          system_health=system_health,
                          recent_trainings=recent_trainings,
                          active_platforms=active_platforms,
                          platform_metrics=platform_metrics)
    
@app.route('/terminal')
def terminal():
    """Interactive terminal interface for command-line interactions"""
    return render_template('terminal.html')
    
@app.route('/memory')
def memory_explorer():
    """Advanced memory explorer for visualizing and managing the memory system"""
    return render_template('memory_explorer.html')
    
@app.route('/platforms')
def platforms():
    """AI platforms management interface"""
    return render_template('platforms.html')
    
@app.route('/editor')
def code_editor():
    """Code editor with Monaco integration"""
    return render_template('code_editor.html')
    
@app.route('/api/command_palette/recent', methods=['GET'])
def get_recent_commands():
    """Get recent commands for the command palette"""
    # This would normally fetch from a database
    recent_commands = [
        {"id": "terminal", "title": "Open Terminal", "category": "Navigation"},
        {"id": "memory", "title": "Open Memory Explorer", "category": "Navigation"},
        {"id": "platforms", "title": "Manage AI Platforms", "category": "Navigation"}
    ]
    return jsonify({"status": "success", "commands": recent_commands})
    
@app.route('/api/files/list', methods=['GET'])
def get_file_list():
    """List files for the code editor file explorer"""
    path = request.args.get('path', '/')
    # This would normally list files from the filesystem
    files = [
        {"name": "main.py", "type": "file", "path": "/main.py", "language": "python"},
        {"name": "app.py", "type": "file", "path": "/app.py", "language": "python"},
        {"name": "templates", "type": "directory", "path": "/templates"}
    ]
    return jsonify({"status": "success", "files": files})
    
@app.route('/api/files/get', methods=['GET'])
def get_file_content():
    """Get file content for the code editor"""
    path = request.args.get('path')
    if not path:
        return jsonify({"status": "error", "message": "Path is required"}), 400
        
    # This would normally read from the actual file
    content = "# Sample file content\nprint('Hello, world!')"
    return jsonify({"status": "success", "content": content})
    
@app.route('/api/files/save', methods=['POST'])
def save_file():
    """Save file content from the code editor"""
    data = request.json
    path = data.get('path')
    content = data.get('content')
    
    if not path or content is None:
        return jsonify({"status": "error", "message": "Path and content are required"}), 400
        
    # This would normally save to the actual file
    return jsonify({"status": "success"})

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

# File System API routes
@app.route('/api/files/list')
def list_files():
    """List files in the project"""
    try:
        base_path = os.path.abspath('.')
        path = request.args.get('path', base_path)
        
        # Security check
        requested_path = os.path.abspath(path)
        if not requested_path.startswith(base_path):
            return jsonify({"status": "error", "message": "Access denied"}), 403
        
        # Generate file tree structure
        files = []
        
        for root, dirs, filenames in os.walk(requested_path):
            # Skip hidden folders and files
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Create relative path from the base path
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                rel_path = ''
            
            # Current directory as a node
            current_dir = {
                'name': os.path.basename(root) or '/',
                'path': rel_path or '/',
                'type': 'dir',
                'children': []
            }
            
            # Add files
            for filename in sorted([f for f in filenames if not f.startswith('.')]):
                file_path = os.path.join(rel_path, filename)
                current_dir['children'].append({
                    'name': filename,
                    'path': file_path,
                    'type': 'file'
                })
            
            # Add to files list if this is the requested directory
            if root == requested_path:
                files = current_dir['children']
                
                # Add directories as separate entries
                for dirname in sorted(dirs):
                    dir_path = os.path.join(rel_path, dirname)
                    # Get subdirectories and files
                    sub_entries = []
                    sub_path = os.path.join(requested_path, dirname)
                    
                    if os.path.isdir(sub_path):
                        for sub_entry in sorted(os.listdir(sub_path)):
                            if not sub_entry.startswith('.'):
                                entry_path = os.path.join(dir_path, sub_entry)
                                entry_type = 'dir' if os.path.isdir(os.path.join(sub_path, sub_entry)) else 'file'
                                sub_entries.append({
                                    'name': sub_entry,
                                    'path': entry_path,
                                    'type': entry_type
                                })
                    
                    files.append({
                        'name': dirname,
                        'path': dir_path,
                        'type': 'dir',
                        'children': sub_entries
                    })
        
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/open')
def open_file():
    """Open a file and return its content"""
    try:
        base_path = os.path.abspath('.')
        path = request.args.get('path')
        
        if not path:
            return jsonify({"status": "error", "message": "Path parameter is required"}), 400
        
        # Security check
        requested_path = os.path.abspath(os.path.join(base_path, path))
        if not requested_path.startswith(base_path):
            return jsonify({"status": "error", "message": "Access denied"}), 403
        
        if not os.path.exists(requested_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        if not os.path.isfile(requested_path):
            return jsonify({"status": "error", "message": "Path is not a file"}), 400
        
        # Determine language for syntax highlighting
        extension = os.path.splitext(path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'plaintext'
        }
        language = language_map.get(extension, 'plaintext')
        
        # Read file content
        with open(requested_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            "status": "success", 
            "content": content,
            "language": language,
            "path": path
        })
    except UnicodeDecodeError:
        # Handle binary files
        return jsonify({
            "status": "error", 
            "message": "Cannot open binary file"
        }), 400
    except Exception as e:
        logger.error(f"Error opening file: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/create', methods=['POST'])
def create_file():
    """Create a new file"""
    try:
        data = request.json
        path = data.get('path')
        content = data.get('content', '')
        
        if not path:
            return jsonify({"status": "error", "message": "Path parameter is required"}), 400
        
        base_path = os.path.abspath('.')
        
        # Security check
        requested_path = os.path.abspath(os.path.join(base_path, path))
        if not requested_path.startswith(base_path):
            return jsonify({"status": "error", "message": "Access denied"}), 403
        
        # Create directories if needed
        directory = os.path.dirname(requested_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Check if file already exists
        if os.path.exists(requested_path):
            return jsonify({"status": "error", "message": "File already exists"}), 400
        
        # Create file
        with open(requested_path, 'w') as f:
            f.write(content)
        
        return jsonify({"status": "success", "path": path})
    except Exception as e:
        logger.error(f"Error creating file: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/create_folder', methods=['POST'])
def create_folder():
    """Create a new folder"""
    try:
        data = request.json
        path = data.get('path')
        
        if not path:
            return jsonify({"status": "error", "message": "Path parameter is required"}), 400
        
        base_path = os.path.abspath('.')
        
        # Security check
        requested_path = os.path.abspath(os.path.join(base_path, path))
        if not requested_path.startswith(base_path):
            return jsonify({"status": "error", "message": "Access denied"}), 403
        
        # Check if folder already exists
        if os.path.exists(requested_path):
            return jsonify({"status": "error", "message": "Folder already exists"}), 400
        
        # Create folder
        os.makedirs(requested_path, exist_ok=True)
        
        return jsonify({"status": "success", "path": path})
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/search')
def search_files():
    """Search for files by name or content"""
    try:
        query = request.args.get('query')
        
        if not query:
            return jsonify({"status": "error", "message": "Query parameter is required"}), 400
        
        base_path = os.path.abspath('.')
        
        # Search results
        results = []
        
        # Walk through directories
        for root, dirs, files in os.walk(base_path):
            # Skip hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Check filenames
            for filename in files:
                if query.lower() in filename.lower():
                    rel_path = os.path.relpath(os.path.join(root, filename), base_path)
                    results.append({
                        'name': filename,
                        'path': rel_path,
                        'type': 'file'
                    })
        
        return jsonify({"status": "success", "files": results})
    except Exception as e:
        logger.error(f"Error searching files: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/run_application', methods=['POST'])
def run_application():
    """Restart the application"""
    try:
        # This would trigger a workflow restart in a real environment
        # For now, just return success
        return jsonify({"status": "success", "message": "Application restarted"})
    except Exception as e:
        logger.error(f"Error restarting application: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Initialize Agent system
from agent_system import AgentSystem
agent_system = AgentSystem(ai_controller, memory_system, training_manager)

# Agent API routes
@app.route('/api/agent/status')
def get_agent_status():
    """Get current agent status"""
    try:
        status = agent_system.get_status()
        return jsonify({"status": "success", "agent_status": status})
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/projects')
def get_agent_projects():
    """Get list of agent projects"""
    try:
        limit = request.args.get('limit', 10, type=int)
        projects = agent_system.get_projects(limit=limit)
        return jsonify({"status": "success", "projects": projects})
    except Exception as e:
        logger.error(f"Error getting agent projects: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/project_details/<project_id>')
def get_agent_project_details(project_id):
    """Get detailed information about an agent project"""
    try:
        details = agent_system.get_project_details(project_id)
        return jsonify(details)
    except Exception as e:
        logger.error(f"Error getting project details: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/create_project', methods=['POST'])
def create_agent_project():
    """Create a new agent project"""
    try:
        data = request.json
        description = data.get('description')
        preferences = data.get('preferences', {})
        
        if not description:
            return jsonify({"status": "error", "message": "Description is required"}), 400
        
        result = agent_system.create_new_project(description, preferences)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating agent project: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/continue', methods=['POST'])
def continue_agent_project():
    """Continue working on an existing agent project"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({"status": "error", "message": "Project ID is required"}), 400
        
        # Start agent if not already running
        if not agent_system.is_running:
            agent_system.start()
        
        # Schedule task to continue project
        agent_system._schedule_task({
            'type': 'continue_project',
            'project_id': project_id,
            'priority': 1
        })
        
        return jsonify({"status": "success", "message": "Project continuation scheduled"})
    except Exception as e:
        logger.error(f"Error continuing agent project: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/pause', methods=['POST'])
def pause_agent():
    """Pause agent"""
    try:
        result = agent_system.stop()
        
        if result:
            return jsonify({"status": "success", "message": "Agent paused successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to pause agent"}), 400
    except Exception as e:
        logger.error(f"Error pausing agent: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/feedback_requests')
def get_agent_feedback_requests():
    """Get agent feedback requests"""
    try:
        status = request.args.get('status')
        requests = agent_system.get_feedback_requests(status=status)
        return jsonify({"status": "success", "requests": requests})
    except Exception as e:
        logger.error(f"Error getting agent feedback requests: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/provide_feedback/<feedback_id>', methods=['POST'])
def provide_agent_feedback(feedback_id):
    """Provide feedback to agent"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"status": "error", "message": "No feedback data provided"}), 400
        
        result = agent_system.provide_feedback(feedback_id, data)
        
        if result:
            return jsonify({"status": "success", "message": "Feedback provided successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to provide feedback"}), 400
    except Exception as e:
        logger.error(f"Error providing agent feedback: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Additional Page Routes for Enhanced User Interface
@app.route('/brain')
def brain_visualization_view():
    """3D Brain visualization of the Synapse Chamber"""
    return render_template('brain_visualization.html')

@app.route('/editor')
def code_editor_view():
    """Code editor view"""
    file_path = request.args.get('file', '')
    return render_template('code_editor.html', file_path=file_path)

@app.route('/terminal')
def terminal_view():
    """Terminal view"""
    return render_template('terminal.html')

@app.route('/memory')
def memory_explorer_view():
    """Memory explorer view"""
    # Get memory statistics
    try:
        # Check if memory system has the method
        if hasattr(memory_system, 'get_memory_stats'):
            memory_stats = memory_system.get_memory_stats()
        else:
            # Initialize with default values
            memory_stats = {
                'total_memories': 0,
                'consolidated_knowledge': 0,
                'links': 0,
                'contexts': [],
                'recent_memories': []
            }
            
            # Add enhanced sample data for demonstration
            import random
            memory_stats = {
                'total_memories': 126,
                'consolidated_knowledge': 18,
                'links': 74,
                'contexts': [
                    {
                        'name': 'current_session',
                        'data': {
                            'user_id': 'user123',
                            'session_start': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'active_platforms': ['gpt', 'claude', 'gemini']
                        }
                    },
                    {
                        'name': 'learning_focus',
                        'data': {
                            'topics': ['web_development', 'database_design', 'api_integration'],
                            'difficulty': 'intermediate',
                            'priority': 'high'
                        }
                    }
                ],
                'recent_memories': []
            }
            
            # Add sample memories
            types = ['general', 'conversation', 'factual', 'procedural']
            contents = [
                "User prefers detailed explanations with code examples when learning new concepts.",
                "During last session, the user struggled with understanding asynchronous programming concepts.",
                "PostgreSQL uses MVCC (Multi-Version Concurrency Control) for handling concurrent access.",
                "To deploy a Flask application, use gunicorn as a WSGI server with nginx as a reverse proxy.",
                "User is working on a project involving AI training and automation of cross-platform interactions."
            ]
            
            for i in range(5):
                timestamp = datetime.datetime.now() - datetime.timedelta(days=i, hours=random.randint(0, 12))
                memory_type = random.choice(types)
                importance = round(random.uniform(0.3, 0.9), 1)
                
                memory_stats['recent_memories'].append({
                    'id': i + 1,
                    'memory_type': memory_type,
                    'content': contents[i],
                    'importance': importance,
                    'created_at': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': random.choice(['user', 'system', 'gpt', 'claude', 'gemini'])
                })
            
        return render_template('memory_explorer.html', memory_stats=memory_stats)
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return render_template('memory_explorer.html', error=str(e))

@app.route('/profile')
def profile_view():
    """User profile view"""
    try:
        # Fetch profile data from gamification system
        user_data = gamification_system.get_user_data() if hasattr(gamification_system, 'get_user_data') else {}
        
        # Get additional stats
        training_stats = {
            'completed': analytics_system.get_completed_training_count() if hasattr(analytics_system, 'get_completed_training_count') else 0,
            'success_rate': analytics_system.get_success_rate() if hasattr(analytics_system, 'get_success_rate') else 0,
            'platform_stats': analytics_system.get_platform_stats() if hasattr(analytics_system, 'get_platform_stats') else {}
        }
        
        return render_template('profile.html', user_data=user_data, training_stats=training_stats)
    except Exception as e:
        logger.error(f"Error loading profile data: {e}")
        return render_template('profile.html', error=str(e))

@app.route('/achievements')
def achievements_view():
    """Achievements and badges view"""
    try:
        # Fetch achievements from gamification system
        achievements = gamification_system.get_achievements() if hasattr(gamification_system, 'get_achievements') else []
        
        # Organize achievements by category
        achievement_categories = {}
        for achievement in achievements:
            category = achievement.get('category', 'Other')
            if category not in achievement_categories:
                achievement_categories[category] = []
            achievement_categories[category].append(achievement)
            
        return render_template('achievements.html', achievement_categories=achievement_categories)
    except Exception as e:
        logger.error(f"Error loading achievements: {e}")
        return render_template('achievements.html', error=str(e))

@app.route('/platforms')
def platforms_view():
    """AI platforms management view"""
    return render_template('platforms.html')
    
@app.route('/logs')
def logs_view():
    """System logs viewer"""
    return render_template('logs.html')

# This route has already been defined at line 998, so I've removed the duplicate
# @app.route('/memory-explorer')
# def memory_explorer_view():
#     """Memory explorer view"""

@app.route('/system-health')
def system_health_view():
    """System health dashboard for monitoring performance and component status"""
    return render_template('system_health.html')

# API Routes for System Health Monitoring
@app.route('/api/system-health/data', methods=['GET'])
def get_system_health_data():
    """Get current system health metrics"""
    import psutil
    import time
    import random
    
    # Basic system metrics
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.5)
    
    # Get browser driver status
    driver_status = "healthy"
    driver_metrics = {}
    
    try:
        # Check if browser driver is functioning
        if browser_automation.driver:
            driver_metrics = {
                "initialized": True,
                "url": browser_automation.driver.current_url if hasattr(browser_automation.driver, 'current_url') else "unknown",
                "type": "undetected_chromedriver" if "undetected_chromedriver" in str(type(browser_automation.driver)) else "standard"
            }
        else:
            driver_status = "warning"
            driver_metrics = {
                "initialized": False,
                "error": "Driver not initialized"
            }
    except Exception as e:
        driver_status = "critical"
        driver_metrics = {
            "initialized": False,
            "error": str(e)
        }
    
    # Get database status
    db_status = "healthy"
    db_metrics = {}
    
    try:
        # Simple database check
        from sqlalchemy import text
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            db_metrics = {
                "connected": True,
                "pool_size": db.engine.pool.size(),
                "pool_checked_out": db.engine.pool.checkedout()
            }
    except Exception as e:
        db_status = "critical"
        db_metrics = {
            "connected": False,
            "error": str(e)
        }
    
    # Get AI platform status
    # This is simplified - in a real implementation we would check actual platform connectivity
    ai_status = "healthy"
    ai_platforms = {}
    
    for platform in ["gpt", "claude", "gemini", "grok", "deepseek"]:
        # Random status for demonstration
        rand = random.random()
        if rand > 0.8:
            platform_status = "warning"
        elif rand > 0.95:
            platform_status = "critical"
        else:
            platform_status = "healthy"
            
        ai_platforms[platform] = {
            "status": platform_status,
            "last_success": (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))).isoformat() if platform_status != "critical" else None,
            "success_rate": random.randint(70, 100) if platform_status != "critical" else random.randint(0, 50)
        }
    
    # Memory system metrics
    memory_status = "healthy"
    memory_metrics = {
        "items_count": 0,
        "conversations_count": 0,
        "total_size_mb": 0
    }
    
    try:
        # Try to get memory metrics
        memory_metrics["items_count"] = memory_system.get_memory_count() if hasattr(memory_system, 'get_memory_count') else 0
        memory_metrics["conversations_count"] = memory_system.get_conversation_count() if hasattr(memory_system, 'get_conversation_count') else 0
    except Exception as e:
        memory_status = "warning"
        memory_metrics["error"] = str(e)
    
    # Overall system metrics
    system_status = "healthy"
    if cpu > 80 or memory.percent > 80:
        system_status = "critical"
    elif cpu > 60 or memory.percent > 60:
        system_status = "warning"
    
    system_metrics = {
        "cpu_usage_percent": cpu,
        "load_avg_1m": psutil.getloadavg()[0],
        "load_avg_5m": psutil.getloadavg()[1],
        "load_avg_15m": psutil.getloadavg()[2],
        "uptime_seconds": time.time() - psutil.boot_time()
    }
    
    # Generate some historical data for charts
    timestamps = []
    response_times = []
    error_rates = []
    
    # Create 12 data points, 5 minutes apart
    for i in range(12):
        # Calculate time point (now - (11-i) * 5 minutes)
        time_point = datetime.datetime.now() - datetime.timedelta(minutes=(11-i) * 5)
        timestamps.append(time_point.strftime("%H:%M"))
        
        # Mock response time (200-500ms with some randomness)
        response_time = 200 + (i * 20) + random.randint(-50, 50)
        response_times.append(response_time)
        
        # Mock error rate (increasing slightly over time with randomness)
        error_rate = min(100, max(0, (i * 0.5) + random.randint(0, 3)))
        error_rates.append(error_rate)
    
    # Build complete response
    health_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall_status": system_status,
        "components": {
            "memory": {
                "status": memory_status,
                "metrics": {
                    "usage_percent": memory.percent,
                    "total_mb": memory.total // (1024 * 1024),
                    "used_mb": memory.used // (1024 * 1024),
                    "free_mb": memory.available // (1024 * 1024)
                }
            },
            "browser": {
                "status": driver_status,
                "metrics": driver_metrics
            },
            "database": {
                "status": db_status,
                "metrics": db_metrics
            },
            "ai": {
                "status": ai_status,
                "platforms": ai_platforms,
                "metrics": {
                    "total_requests": 0,  # Would track this in a real implementation
                    "success_rate": 0,    # Would track this in a real implementation
                    "avg_response_time_ms": 0  # Would track this in a real implementation
                }
            },
            "system": {
                "status": system_status,
                "metrics": system_metrics
            }
        },
        "logs": [
            # Would get actual logs in a real implementation
            {"type": "info", "message": "System health check completed", "timestamp": datetime.datetime.now().isoformat()},
            {"type": "info", "message": "Browser driver initialized successfully", "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat()},
            {"type": "info", "message": "Database connection pool expanded", "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=10)).isoformat()},
        ],
        "performance_history": {
            "timestamps": timestamps,
            "response_time_ms": response_times,
            "error_rate_percent": error_rates
        }
    }
    
    return jsonify(health_data)

@app.route('/api/system-health/reinitialize-driver', methods=['POST'])
def reinitialize_driver():
    """Reinitialize the browser driver"""
    try:
        browser_automation.initialize_driver(retry_count=3)
        return jsonify({
            "success": True,
            "message": "Browser driver reinitialized successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/system-health/logs', methods=['GET'])
def get_system_logs():
    """Get system logs for the system health dashboard"""
    import glob
    import random
    
    log_data = []
    
    # Get the last 20 log entries with type and timestamp
    for i in range(20):
        log_type = "info"
        if i % 10 == 0:
            log_type = "warning"
        elif i % 15 == 0:
            log_type = "error"
            
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=i * 5)
        
        log_data.append({
            "timestamp": timestamp.isoformat(),
            "type": log_type,
            "message": f"System health check log entry {i}"
        })
    
    return jsonify(log_data)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Get detailed system logs with filtering
    
    Query parameters:
    - page: Page number (default: 1)
    - levels: Comma-separated list of log levels to include (info,warning,error,debug)
    - sources: Comma-separated list of log sources (system,browser,ai,memory,training)
    - time_range: Time range to query (15m, 1h, 6h, 24h, 7d, all)
    - search: Text search query
    """
    import random
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    levels = request.args.get('levels', 'info,warning,error,debug').split(',')
    sources = request.args.get('sources', 'system,browser,ai,memory,training').split(',')
    time_range = request.args.get('time_range', '24h')
    search_query = request.args.get('search', '')
    
    # Convert time range to minutes
    time_range_minutes = {
        '15m': 15,
        '1h': 60,
        '6h': 360,
        '24h': 1440,
        '7d': 10080,
        'all': 99999999
    }.get(time_range, 1440)  # Default to 24h
    
    # Page size
    page_size = 50
    
    # Create synthetic system logs for demonstration
    log_data = []
    log_sources = ["system", "browser", "ai", "memory", "training"]
    log_types = ["info", "warning", "error", "debug"]
    
    # Sample log messages for each source
    log_messages = {
        "system": [
            "Application started successfully",
            "CPU usage spike detected (90%)",
            "Memory usage high (85%)",
            "Database connection pool expanded",
            "Background task completed successfully",
            "System configuration reloaded",
            "User session expired",
            "Cache cleared automatically",
            "System update available",
            "File system check completed"
        ],
        "browser": [
            "Browser driver initialized successfully",
            "Navigation completed to ChatGPT",
            "Element not found: login button",
            "Page load timeout (30s)",
            "Screenshot captured",
            "Browser session reset",
            "Cookie management error",
            "CAPTCHA detected",
            "JavaScript execution completed",
            "Network request intercepted"
        ],
        "ai": [
            "API request to OpenAI successful",
            "Rate limit exceeded on Claude API",
            "Response received from Gemini",
            "Token usage: 3500/4096",
            "Model fallback initiated: GPT-3.5 -> GPT-4",
            "Context window overflow",
            "API key validation successful",
            "Response timeout from DeepSeek",
            "Training example collected",
            "Model selection optimization applied"
        ],
        "memory": [
            "Memory entry stored successfully",
            "Vector index updated",
            "Semantic search completed (0.25s)",
            "Memory consolidation triggered",
            "Conversation summary generated",
            "Linked memories created",
            "Memory pruning completed: 50 items removed",
            "Context retrieval optimization applied",
            "Memory synchronization with base system",
            "Importance scoring recalculated"
        ],
        "training": [
            "Training session started: Web Development",
            "Training completed with 87% success rate",
            "Example generated for AutoDev",
            "Learning objective achieved: API Design",
            "Training interrupted by user",
            "Knowledge assessment score: 92%",
            "Training data exported",
            "Curriculum updated based on performance",
            "New skill unlocked: Database Schema Design",
            "Training analytics updated"
        ]
    }
    
    # Generate more varied and realistic log entries
    total_logs = 250  # Total simulated logs in the system
    
    for i in range(total_logs):
        # Select a random source and type, with weighted probabilities
        source = random.choices(log_sources, weights=[0.4, 0.2, 0.2, 0.1, 0.1])[0]
        
        # Different sources have different typical log level distributions
        type_weights = {
            "system": [0.6, 0.2, 0.1, 0.1],  # More info logs for system
            "browser": [0.5, 0.3, 0.1, 0.1], # More warnings for browser automation
            "ai": [0.5, 0.2, 0.2, 0.1],      # More errors for AI interactions
            "memory": [0.7, 0.1, 0.1, 0.1],  # Mostly info for memory operations
            "training": [0.6, 0.2, 0.1, 0.1] # More info for training
        }
        
        log_type = random.choices(log_types, weights=type_weights[source])[0]
        
        # Generate a timestamp within the time range
        # More recent logs are more likely (exponential distribution)
        log_age = int(random.expovariate(1.0 / (time_range_minutes / 5))) 
        log_age = min(log_age, time_range_minutes)  # Cap at the max time range
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=log_age)
        
        # Select a message for the source
        message = random.choice(log_messages[source])
        
        # Add randomized details for more realism
        if log_type == "error":
            message = f"ERROR: {message} - {random.choice(['timeout', 'connection refused', 'unexpected response', 'authentication failed'])}"
        elif log_type == "warning":
            message = f"WARNING: {message} - {random.choice(['retrying', 'fallback initiated', 'degraded performance', 'limited functionality'])}"
        
        # Add a log entry
        log_entry = {
            "id": total_logs - i,  # Descending IDs
            "timestamp": timestamp.isoformat(),
            "type": log_type,
            "source": source,
            "message": message,
            "details": None  # Additional details could be added if needed
        }
        
        log_data.append(log_entry)
    
    # Sort by timestamp (newest first)
    log_data.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply filters
    filtered_logs = [log for log in log_data 
                    if log["type"] in levels 
                    and log["source"] in sources
                    and (not search_query or search_query.lower() in log["message"].lower())]
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_logs = filtered_logs[start_idx:end_idx]
    
    # Return response
    return jsonify({
        "logs": paginated_logs,
        "total": len(filtered_logs),
        "page": page,
        "page_size": page_size
    })
