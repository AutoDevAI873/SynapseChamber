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
