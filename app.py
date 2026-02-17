from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)

    @app.route('/')
    def index():
         return "LegalTech Backend API is running. Use /api/health or /api/login."
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "ok", "message": "Backend is running"}

    
    @app.route('/api/login', methods=['POST'])
    def login():
        from flask import request
        from models import User
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # In a real app, hash password and compare
        user = User.query.filter_by(email=email).first()
        
        if user and user.password_hash == password:
             return {"status": "success", "token": "dummy-jwt-token", "user": {"id": user.id, "email": user.email, "name": user.full_name}}, 200
            
        return {"status": "error", "message": "Credenciales inválidas"}, 401

    @app.route('/api/chat', methods=['POST'])
    def chat():
        from flask import request
        from models import Conversation, Message
        from services.chat_engine import generate_response
        
        data = request.get_json()
        user_id = data.get('userId') # Optional if anonymous
        message_text = data.get('message')
        conversation_id = data.get('conversationId')
        
        if not message_text:
            return {"error": "Message required"}, 400
            
        # 1. Get or Create Conversation
        if not conversation_id:
            title = message_text[:40] + "..." if len(message_text) > 40 else message_text
            conv = Conversation(user_id=user_id, title=title)
            db.session.add(conv)
            db.session.commit()
            conversation_id = conv.id
        else:
            conv = db.session.get(Conversation, conversation_id)
            if not conv:
                return {"error": "Conversation not found"}, 404
        
        # 2. Save User Message
        user_msg = Message(conversation_id=conversation_id, sender_role='user', content=message_text)
        db.session.add(user_msg)
        
        # 3. Generate AI Response
        ai_result = generate_response(message_text, conversation_id)
        ai_text = ai_result['text']
        # status = ai_result['status'] # Could update conversation status
        
        # 4. Save AI Message
        ai_msg = Message(conversation_id=conversation_id, sender_role='assistant', content=ai_text)
        db.session.add(ai_msg)
        
        db.session.commit()
        
        
        return {
            "conversationId": conversation_id,
            "response": ai_text,
            "status": ai_result['status'],
            "title": conv.title
        }

    @app.route('/api/conversations/<int:user_id>', methods=['GET'])
    def get_conversations(user_id):
        from models import Conversation
        convs = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
        
        result = []
        for c in convs:
            # Get last message / simple summary
            result.append({
                "id": c.id,
                "title": c.title,
                "updated_at": c.updated_at.isoformat()
            })
        return {"conversations": result}
        
    @app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
    def get_messages(conversation_id):
        from models import Message
        msgs = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        result = []
        for m in msgs:
            result.append({
                "id": m.id,
                "role": m.sender_role,
                "content": m.content,
                "timestamp": m.created_at.isoformat()
            })
        return {"messages": result}

        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
