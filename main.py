from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
import datetime
from models import User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(minutes=30)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        if BlacklistToken.query.filter_by(token=token).first():
            return jsonify({'error': 'Token is revoked'}), 401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = data['id']
            g.user_id = user_id
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return func(*args, **kwargs)
    return wrapper

# Route for admin signup
@app.route('/auth/admin/signup', methods=['POST'])
def admin_signup():
    data = request.get_json()
    # Check if the user is already an admin
    existing_admin = User.query.filter_by(email=data['email'], is_admin=True).first()
    if existing_admin:
        return jsonify({'error': 'Admin already exists'}), 400

    # Create a new admin user
    new_admin = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        is_admin=True  # Set the user as admin
    )
    db.session.add(new_admin)
    db.session.commit()

    # Generate JWT token for admin
    token = jwt.encode({'id': new_admin.id, 'exp': datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'message': 'Admin registered successfully.', 'token': token.decode('utf-8')}), 201

#allow user to sign up
@app.route('/auth/signup', methods=['POST'])
def user_signup():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode({'id': new_user.id, 'exp': datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'message': 'User registered successfully. Pending admin approval.', 'token': token.decode('utf-8')}), 201

#allow admin to view list of pending user status
@app.route('/admin/users/pending', methods=['GET'])
@token_required(role='admin')
def pending_signups():
    pending_users = User.query.filter_by(status='pending').all()
    return jsonify([{'id': user.id, 'email': user.email} for user in pending_users]), 200

#allow admin to approve user sign in
@app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@token_required(role='admin')
def approve_signup(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'approved'
        db.session.commit()
        return jsonify({'message': 'User sign-up approved successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

##allow admin to disapprove user sign in
@app.route('/admin/users/disapprove/<int:user_id>', methods=['POST'])
@token_required(role='admin')
def disapprove_signup(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'disapproved'
        db.session.commit()
        return jsonify({'message': 'User sign-up disapproved successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

#@app.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization')
    if token:
        # Add the token to the blacklist
        blacklisted_token = BlacklistToken(token=token)
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify({'message': 'Logged out successfully'}), 200
    else:
        return jsonify({'error': 'Token is missing'}), 401
if __name__ == '__main__':
    app.run(debug=True)
