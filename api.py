from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from functools import wraps
import os
from datetime import datetime, timedelta

# Import the main app
from app import app

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# API credentials (in production, use environment variables)
API_USERS = {
    'admin': 'admin123',
    'yigal': 'yigal2025',
    'manager': 'manager123'
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY', 'yigal-law-api-2025'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def api_login():
    """Login endpoint for API access"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if username in API_USERS and API_USERS[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 86400,  # 24 hours
            'user': username
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Blog management endpoints
@app.route('/api/blog/posts', methods=['GET'])
@require_api_key
def get_blog_posts():
    """Get all blog posts"""
    posts = [
        {
            'id': 1,
            'title': 'נזיקין תביעות',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '15/01/2025 14:30',
            'content': 'מידע על תביעות נזיקין...',
            'image': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop'
        },
        {
            'id': 2,
            'title': 'תאונת עבודה מול הביטוח הלאומי',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '22/01/2025 11:15',
            'content': 'מידע על תאונות עבודה...',
            'image': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&h=250&fit=crop'
        },
        {
            'id': 3,
            'title': 'תאונות עם מעורבות של אופניים חשמליים',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '28/01/2025 16:45',
            'content': 'מידע על תאונות אופניים...',
            'image': 'https://images.unsplash.com/photo-1581578731548-c7e3d1c1c9d9?w=400&h=250&fit=crop'
        }
    ]
    return jsonify({'posts': posts}), 200

@app.route('/api/blog/posts', methods=['POST'])
@jwt_required()
def create_blog_post():
    """Create a new blog post"""
    data = request.get_json()
    
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # In a real application, you would save this to a database
    new_post = {
        'id': datetime.now().timestamp(),
        'title': data['title'],
        'author': 'יגאל סופר עורך דין ונוטריון',
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'content': data['content'],
        'image': data.get('image', 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop')
    }
    
    return jsonify({'message': 'Post created successfully', 'post': new_post}), 201

@app.route('/api/blog/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_blog_post(post_id):
    """Update an existing blog post"""
    data = request.get_json()
    
    # In a real application, you would update this in a database
    updated_post = {
        'id': post_id,
        'title': data.get('title', 'Updated Title'),
        'author': 'יגאל סופר עורך דין ונוטריון',
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'content': data.get('content', 'Updated content'),
        'image': data.get('image', 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop')
    }
    
    return jsonify({'message': 'Post updated successfully', 'post': updated_post}), 200

@app.route('/api/blog/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_blog_post(post_id):
    """Delete a blog post"""
    # In a real application, you would delete this from a database
    return jsonify({'message': f'Post {post_id} deleted successfully'}), 200

# Contact form submissions endpoint
@app.route('/api/contacts', methods=['GET'])
@require_api_key
def get_contacts():
    """Get all contact form submissions"""
    # In a real application, you would fetch this from a database
    contacts = [
        {
            'id': 1,
            'name': 'דוגמה שם',
            'phone': '050-1234567',
            'email': 'example@email.com',
            'service': 'נזיקין',
            'message': 'הודעה לדוגמה',
            'date': '15/01/2025 14:30'
        }
    ]
    return jsonify({'contacts': contacts}), 200

# Statistics endpoint
@app.route('/api/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Get website statistics"""
    stats = {
        'years_experience': 30,
        'total_visits': 1250,
        'contact_submissions': 45,
        'blog_posts': 3
    }
    return jsonify({'stats': stats}), 200

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
