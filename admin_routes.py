from flask import Blueprint, jsonify, request
from extensions import db
from models import User, Conversation, Message
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Middleware to check if user is admin (simplified for now, assumes userId passed in headers or body)
# In a real app, this would use JWT claims.
def check_admin(user_id):
    user = User.query.get(user_id)
    return user and user.is_admin

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    # userId = request.args.get('userId')
    # if not check_admin(userId):
    #     return jsonify({"error": "Unauthorized"}), 403

    total_users = User.query.count()
    total_conversations = Conversation.query.count()
    
    # Active users in last 24h (based on message activity)
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users_count = db.session.query(Conversation.user_id).join(Message).filter(Message.created_at >= yesterday).distinct().count()

    # Cases by type/status
    risk_cases = Conversation.query.filter_by(status='risk_detected').count()
    
    return jsonify({
        "totalUsers": total_users,
        "totalConversations": total_conversations,
        "activeUsers24h": active_users_count,
        "riskCases": risk_cases
    })

@admin_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for u in users:
        conv_count = Conversation.query.filter_by(user_id=u.id).count()
        user_list.append({
            "id": u.id,
            "email": u.email,
            "name": u.full_name,
            "role": u.role,
            "isAdmin": u.is_admin,
            "joinedAt": u.created_at.isoformat(),
            "conversationCount": conv_count
        })
    return jsonify({"users": user_list})

@admin_bp.route('/conversations', methods=['GET'])
def get_recent_conversations():
    # Get recent 50 conversations
    convs = Conversation.query.order_by(Conversation.updated_at.desc()).limit(50).all()
    result = []
    for c in convs:
        user = User.query.get(c.user_id) if c.user_id else None
        result.append({
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "updatedAt": c.updated_at.isoformat(),
            "userEmail": user.email if user else "Anonymous"
        })
    return jsonify({"conversations": result})

@admin_bp.route('/knowledge', methods=['POST'])
def upload_knowledge():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported currently"}), 400

    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Save to DB
        from models import KnowledgeBase
        kb_item = KnowledgeBase(
            title=file.filename,
            content=text_content,
            file_type='pdf'
        )
        db.session.add(kb_item)
        db.session.commit()
        
        return jsonify({"message": "File uploaded and processed successfully", "id": kb_item.id})
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@admin_bp.route('/knowledge', methods=['GET'])
def get_knowledge_base():
    from models import KnowledgeBase
    items = KnowledgeBase.query.order_by(KnowledgeBase.created_at.desc()).all()
    
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "title": item.title,
            "fileType": item.file_type,
            "createdAt": item.created_at.isoformat(),
            "contentPreview": item.content[:100] + "..." if len(item.content) > 100 else item.content
        })
    return jsonify({"documents": result})

@admin_bp.route('/knowledge/<int:id>', methods=['DELETE'])
def delete_knowledge(id):
    from models import KnowledgeBase
    item = db.session.get(KnowledgeBase, id)
    if not item:
        return jsonify({"error": "Document not found"}), 404
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Document deleted"})
