from flask import Flask, request, jsonify, session
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import uuid
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies for localhost
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:8080', 'http://127.0.0.1:8080'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'sqlinjection_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

@app.route('/api/login', methods=['POST'])
def login():
    """Vulnerable login endpoint - SQL injection possible"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # VULNERABLE SQL QUERY - Intentionally vulnerable for educational purposes
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        cursor.execute(query)
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            # Check the ORIGINAL username input (not the database result)
            # This prevents SQL injection from bypassing the check
            original_username = username.strip()
            is_admin_user = original_username.lower() == 'admin'
            
            # Create session
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            session['username'] = user['username']
            session['original_username'] = original_username
            session['is_admin'] = is_admin_user
            session['user_id'] = user['id']
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'session_id': session_id,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'original_username': original_username,  # Return original input
                    'role': user['role'],
                    'is_admin_user': is_admin_user
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/session', methods=['GET'])
def get_session():
    """Get current session information"""
    try:
        if 'session_id' in session:
            return jsonify({
                'success': True,
                'session': {
                    'session_id': session.get('session_id'),
                    'username': session.get('username'),
                    'original_username': session.get('original_username'),
                    'is_admin': session.get('is_admin', False),
                    'user_id': session.get('user_id')
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No active session'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/computers', methods=['GET'])
def get_computers():
    """Get list of computers - requires admin username"""
    try:
        # Check session first, then fall back to username parameter
        username = None
        if 'original_username' in session:
            username = session.get('original_username', '').strip()
        else:
            username = request.args.get('username', '').strip()
        
        # Strictly check if the username is exactly "admin"
        if not username or username.lower() != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = "SELECT id, computer_name, ip_address FROM computers ORDER BY id"
        cursor.execute(query)
        computers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'computers': [dict(comp) for comp in computers]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/search', methods=['GET'])
def search():
    """Vulnerable search endpoint - SQL injection for schema extraction"""
    try:
        # Check session first, then fall back to username parameter
        username = None
        if 'original_username' in session:
            username = session.get('original_username', '').strip()
        else:
            username = request.args.get('username', '').strip()
        
        search_term = request.args.get('q', '')
        
        # Strictly check if the username is exactly "admin"
        if not username or username.lower() != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # VULNERABLE SQL QUERY - Intentionally vulnerable for educational purposes
        # This allows SQL injection to extract schema information
        query = f"SELECT id, computer_name, ip_address FROM computers WHERE computer_name LIKE '%{search_term}%' OR ip_address LIKE '%{search_term}%'"
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'results': [dict(r) for r in results]
        }), 200
        
    except Exception as e:
        # Return error message which might leak information
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'error_details': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
