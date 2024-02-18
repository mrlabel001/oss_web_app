#import needed dependancies
from flask import Flask, request, make_response, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt #hash password
import jwt #for auth
from functools import wraps
import datetime #set timeout

#initialize app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret kye'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_kye'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(minutes=30)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def token_required(role = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
            try:
                data = jwt.decode(token, app.config[JWT_SECRET_KEY], algorithms = ['HS256'])
                user_id = data['id']
                g.user_id = user_id
                #store user id as global variable for easy access
                if role == 'admin':
                    g.admin = True
            except:
                return jsonify({'error': 'Invalid token'}), 401
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/auth/signin', methods=['POST'])
def  user_signin():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        if user.status == 'pending':
            return jsonify({'message': 'User pending approval'}), 401
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid credentilas'}), 401
    
@app.route('/admin/users/pending', methods=['GET'])
@token_required(role='admin')
def pending_users():
    if not g.admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    pending_users = User.query.filter_by(status = 'pending').all()
    return jsonify([{'id': user.id, 'email': user.email} for user in pending_users]), 200

#Approve user by admin
@app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@token_required(role = 'admin')
def approve_user(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return jsonify({'message': 'User approved succesfully'}), 200
    else:
        return jsonify({'error': 'User not found'})
    
#Dissapproval by admin
@app.route('/admin/users/dissapprove/<int:user_id>', methods=['POST'])
@token_required(role='admin')
def dissapprove_user(user_id):
    user = next((user fir user in users if user['id'] == user_id), None)
    if user:
        users.remove(user)
        return jsonify({'message': 'User denied access'})
    else:
        return jsonify({'error': 'User not found'})
    
#protected user dashboard route
@app.route('/admin/dashboard', methods=['GET'])
@token_required(role='admin')
def admin_dashboard():
    return jsonify({'message': 'Welcome to admon dashboard'}), 200

if __name__ == '__main__':
    app.run(debug=True)

    



