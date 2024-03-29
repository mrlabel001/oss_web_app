#import needed dependancies
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

#users model
class User(db.Model, SerializerMixin):
    serialize_only = ('id', 'first_name', 'last_name', 'email', 'file_no', 'year')
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    file_no = db.Column(db.Integer)
    year = db.Column(db.Integer)
    status = db.Column(db.Bool)
    admin = db.Column(db.String) #special string known to admins only
    password = db.Column(db.String)

    #relationships
    profile = db.relationship('Profile', backref='user', uselist=False)
    posts = db.relationship('Post', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

#profile model
class Profile(db.Model, SerializerMixin):
    serialize_only = ('house', 'class_stream', 'school_club', 'profession', 'football_team', 'about_you', 'user_id')
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    house = db.Column(db.String)
    class_stream = db.Column(db.String)
    school_club = db.Column(db.String)
    profession = db.Column(db.String)
    football_team = db.Column(db.String)
    about_you = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

#posts model
class Post(db.Model, SerializerMixin):
    serialize_only = ('post_url', 'user_id', 'post_description')
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    post_url = db.Column(db.String)
    post_description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

#reviews model
class Review(db.Model, SerializerMixin):
    serialize_only = ('text', 'user_id', 'post_id')
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
