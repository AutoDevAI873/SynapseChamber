import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "synapse_chamber_secret_key")

# Mock AI platforms data
AI_PLATFORMS = ["gpt", "gemini", "deepseek", "claude", "grok"]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai_interaction')
def ai_interaction():
    return render_template('ai_interaction.html', ai_platforms=AI_PLATFORMS)

@app.route('/logs')
def logs():
    # Mock conversation data for demonstration
    mock_conversations = [
        {
            "id": 1,
            "platform": "gpt",
            "subject": "Upwork Automation",
            "goal": "Create a system to automate Upwork job applications",
            "created_at": "2023-06-15T10:30:00",
            "messages": [
                {
                    "id": 1,
                    "is_user": True,
                    "content": "How would you design a system to automate Upwork job applications?",
                    "timestamp": "2023-06-15T10:30:00"
                },
                {
                    "id": 2,
                    "is_user": False,
                    "content": "I'd design a system with these components: 1) Web scraper to find jobs, 2) NLP for relevance scoring, 3) Proposal generator, 4) Application submitter with CAPTCHA handling, and 5) Response tracker.",
                    "timestamp": "2023-06-15T10:31:00"
                }
            ]
        },
        {
            "id": 2,
            "platform": "gemini",
            "subject": "HELB Portal Enhancement",
            "goal": "Analyze HELB website architecture for improvements",
            "created_at": "2023-06-14T15:45:00",
            "messages": [
                {
                    "id": 3,
                    "is_user": True,
                    "content": "What improvements would you suggest for the HELB portal?",
                    "timestamp": "2023-06-14T15:45:00"
                }
            ]
        }
    ]
    
    # Check if specific conversation requested
    conversation_id = request.args.get('conversation')
    if conversation_id:
        # Find the specific conversation or return first one for demo
        for conv in mock_conversations:
            if str(conv["id"]) == conversation_id:
                return render_template('logs.html', conversation=conv)
        
    # Return all conversations
    return render_template('logs.html', conversations=mock_conversations)

@app.route('/settings')
def settings():
    return render_template('settings.html')

# API routes
@app.route('/api/start_interaction', methods=['POST'])
def start_interaction():
    data = request.json
    platform = data.get('platform')
    prompt = data.get('prompt')
    subject = data.get('subject')
    goal = data.get('goal')
    
    logger.info(f"Received interaction request: {platform}, {subject}, {prompt[:50]}...")
    
    # Mock successful response
    response = {
        "status": "success",
        "platform": platform,
        "prompt": prompt,
        "response": f"This is a simulated response from {platform}. The Synapse Chamber is currently in development mode without direct AI connections.",
        "conversation_id": 1,
        "timestamp": "2023-06-15T10:30:00"
    }
    
    return jsonify(response)

@app.route('/api/get_conversation/<conversation_id>')
def get_conversation(conversation_id):
    # Mock conversation data
    conversation = {
        "id": conversation_id,
        "platform": "gpt",
        "subject": "Upwork Automation",
        "goal": "Create a system to automate Upwork job applications",
        "created_at": "2023-06-15T10:30:00",
        "messages": [
            {
                "id": 1,
                "is_user": True,
                "content": "How would you design a system to automate Upwork job applications?",
                "timestamp": "2023-06-15T10:30:00"
            },
            {
                "id": 2,
                "is_user": False,
                "content": "I'd design a system with these components: 1) Web scraper to find jobs, 2) NLP for relevance scoring, 3) Proposal generator, 4) Application submitter with CAPTCHA handling, and 5) Response tracker.",
                "timestamp": "2023-06-15T10:31:00"
            }
        ]
    }
    
    return jsonify({"status": "success", "conversation": conversation})

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    data = request.json
    logger.info(f"Saving settings: {data}")
    return jsonify({"status": "success"})

@app.route('/api/conversations')
def get_conversations():
    # Mock conversation list
    conversations = [
        {
            "id": 1,
            "platform": "gpt",
            "subject": "Upwork Automation",
            "created_at": "2023-06-15T10:30:00"
        },
        {
            "id": 2,
            "platform": "gemini",
            "subject": "HELB Portal Enhancement",
            "created_at": "2023-06-14T15:45:00"
        }
    ]
    
    return jsonify({"status": "success", "conversations": conversations})

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('static/screenshots', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start the application
    app.run(host='0.0.0.0', port=5000, debug=True)