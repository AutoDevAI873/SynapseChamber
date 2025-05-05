from datetime import datetime
from app import db
from flask_login import UserMixin
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    def __repr__(self):
        return f'<User {self.username}>'

class AIConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # gpt, gemini, deepseek, claude, grok
    subject = db.Column(db.String(128))
    goal = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to messages
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<AIConversation {self.id}: {self.platform} - {self.subject}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'subject': self.subject,
            'goal': self.goal,
            'created_at': self.created_at.isoformat(),
            'messages': [message.to_dict() for message in self.messages]
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('ai_conversation.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=True)  # True if from user, False if from AI
    content = db.Column(db.Text, nullable=False)
    screenshot_path = db.Column(db.String(256))  # Path to screenshot if captured
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        sender = "User" if self.is_user else "AI"
        return f'<Message {self.id}: {sender}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'is_user': self.is_user,
            'content': self.content,
            'screenshot_path': self.screenshot_path,
            'timestamp': self.timestamp.isoformat()
        }

class TrainingThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    goal = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    final_plan = db.Column(db.Text)
    
    # Store contributions as JSON
    ai_contributions_json = db.Column(db.Text)
    
    # Relationships
    conversations = db.relationship('AIConversation', secondary='thread_conversation_link', backref='threads')
    
    @property
    def ai_contributions(self):
        if self.ai_contributions_json:
            return json.loads(self.ai_contributions_json)
        return {}
    
    @ai_contributions.setter
    def ai_contributions(self, value):
        self.ai_contributions_json = json.dumps(value)
    
    def __repr__(self):
        return f'<TrainingThread {self.id}: {self.subject}>'

# Association table for Thread and Conversation many-to-many relationship
thread_conversation_link = db.Table('thread_conversation_link',
    db.Column('thread_id', db.Integer, db.ForeignKey('training_thread.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('ai_conversation.id'), primary_key=True)
)
