#import needed dependancies
from flask import Flask
from datetime import datetime
from functools import wraps
from models import db , User, TokenBlocklist
from flask_restful import reqparse, Resource, Api
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash    #hash password
from flask_jwt_extended import create_access_token, verify_jwt_in_request, JWTManager, get_jwt, jwt_required #Authentication and route protection

jwt = JWTManager()

#function to differentiate admin user
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["admin"] == "14603":  #only admins have access
                return fn(*args, **kwargs)
            else:
                return {"msg": "admins only"}, 403
        return decorator
    return wrapper


#function to revoke token after log out
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

#function to identify current user
@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id = identity).first()

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

#User sign up arguments
register_args = reqparse.RequestParser()
register_args.add_argument('first_name', required=True, help='please enter first_name')
register_args.add_argument('last_name')
register_args.add_argument('email', required=True, help='email is required')
register_args.add_argument('file_no', required=True, help='please enter file_no')
register_args.add_argument('year', required=True, help='year is required')
register_args.add_argument('admin', help='enter admin password')
register_args.add_argument('password', required=True, help='password is required')

#User log in up arguments
login_args = reqparse.RequestParser()
login_args.add_argument('email', required=True, help='email is required')
login_args.add_argument('password', required=True, help='password is required')

#User sign up
class RegisterUser(Resource):
    def post(self):
        data = register_args.parse_args()
        password_hash = generate_password_hash(data.password)
        user = User(
            first_name = data.get('first_name', None),
            last_name = data.get('last_name', None),
            email = data.get('email', None),
            file_no = data.get('file_no', None),
            year = data.get('year', None),
            admin = data.get('admin', None),
            password = password_hash)
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

#User log in
class Login(Resource):
    def post(self):
        data = login_args.parse_args()
        user = User.query.filter_by(email = data.get('email')).first()
        if user:
            if check_password_hash(user.password, data.get('password')):
                additional_claims = {"admin": user.admin}
                token = create_access_token(identity=user.id, additional_claims = additional_claims)
                return token
            else:
                return {"msg": 'forgot password!'}
        else:
            return {"msg": 'Invalid credentials'}

#User log out
class Logout(Resource):
    @jwt_required()
    def get(self):
        jwt_data = get_jwt()
        blocked_token = TokenBlocklist(jti=jwt_data.get('jti'), created_at=datetime.utcnow())
        db.session.add(blocked_token)
        db.session.commit()
        return {"msg": 'User logged out!'}

api.add_resource(RegisterUser, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')