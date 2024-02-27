#import needed dependancies
from datetime import timedelta
from flask import Flask
from flask_migrate import Migrate
from models import db
from posts import posts_bp
from profile import profile_bp
from auth import auth_bp, jwt, admin_required
from flask_jwt_extended import jwt_required
from flask import Blueprint

#configure my app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours = 2)
app.register_blueprint(posts_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
db.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

@app.route('/home')
@admin_required()
def home():
    return 'home'

if __name__ == '__main__':
    app.run(debug=True)