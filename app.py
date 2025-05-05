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
