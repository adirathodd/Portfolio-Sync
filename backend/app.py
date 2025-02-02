from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
JWT_SECRET = os.getenv("JWT_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert user into the database
    response = supabase.table('users').insert({
        'username': username,
        'password': hashed_password,
        'email': email,
        'joined_at': datetime.utcnow().isoformat()
    }).execute()

    if response.status_code != 200:
        return jsonify({'error': 'Failed to register user'}), 500

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    # Retrieve user from the database
    user = supabase.table('users').select('*').eq('email', email).execute()
    if not user.data:
        return jsonify({'error': 'Invalid credentials'}), 401

    user = user.data[0]
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user['id'])
    return jsonify({'access_token': access_token}), 200

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_path = f"resumes/{user_id}/{file.filename}"

    try:
        # Upload to Supabase bucket
        response = supabase.storage.from_(BUCKET_NAME).upload(file_path, file.read())
        if response.status_code != 200:
            return jsonify({'error': 'Failed to upload file'}), 500

        # Save file details in database
        supabase.table('resumes').insert({
            'user_id': user_id,
            'resume_pdf': file_path,
            'parsed_resume': None,  # This would be filled after parsing
            'uploaded_at': datetime.utcnow().isoformat()
        }).execute()

        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()

    # Get user details
    user = supabase.table('users').select('*').eq('id', user_id).execute()
    if not user.data:
        return jsonify({'error': 'User not found'}), 404

    # Get user's resumes
    resumes = supabase.table('resumes').select('*').eq('user_id', user_id).execute()

    return jsonify({
        'user': user.data[0],
        'resumes': resumes.data
    }), 200

if __name__ == '__main__':
    app.run(debug=True)