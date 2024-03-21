
from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from email_validator import validate_email, EmailNotValidError
from authors_app.models.user import User
from authors_app import db



auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
bcrypt = Bcrypt()

# Get all users
@auth.route('/users/', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'contact': user.contact,
            'user_type': user.user_type,
            'biography': user.biography
        }
        output.append(user_data)
    return jsonify({'users': output})

# Get a specific user
@auth.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    user_data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'contact': user.contact,
        'user_type': user.user_type,
        'biography': user.biography
    }
    return jsonify(user_data)

# Register a user
@auth.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email or password is missing
        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        # Validate email format
        validate_email(email)

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            contact=data.get('contact'),
            user_type=data.get('user_type', 'author'),
            password=hashed_password,
            biography=data.get('biography', '')
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except EmailNotValidError:
        return jsonify({'error': 'Invalid email format'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@auth.route('/user/<int:id>/edit', methods=['PATCH'])
def update_user_patch(id):
    try:
        user = User.query.get_or_404(id)
        data = request.get_json()

        # Update user attributes based on the provided data
        for key, value in data.items():
            if key == 'password' and value:  # Check if password is provided and not empty
                user.password = bcrypt.generate_password_hash(value).decode('utf-8')
            elif hasattr(user, key):  # Check if the attribute exists in the User model
                setattr(user, key, value)
        
        # Commit changes to the database
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
# Delete a user
@auth.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
