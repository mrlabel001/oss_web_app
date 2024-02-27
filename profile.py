#import needed dependancies
from flask import Flask
from models import db , User
from flask_restful import reqparse, Resource, Api
from flask import Blueprint
from auth import auth_bp, jwt, admin_required
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, verify_jwt_in_request


profile_bp = Blueprint('profile', __name__)
api = Api(profile_bp)

#post arguments
post_args = reqparse.RequestParser()
post_args.add_argument('house')
post_args.add_argument('class_stream')
post_args.add_argument('school_club')
post_args.add_argument('proffession')
post_args.add_argument('football_team')
post_args.add_argument('about_you')

#patch arguments
patch_args = reqparse.RequestParser()
patch_args.add_argument('house')
patch_args.add_argument('class_stream')
patch_args.add_argument('school_club')
patch_args.add_argument('proffession')
patch_args.add_argument('football_team')
patch_args.add_argument('about_you')


class ProfileById(Resource):

    #route to create user's profile
    @jwt_required()
    def post(self):
        data = post_args.parse_args()
        profile = Profile(house = data.get("house"),
        class_stream=data.get('class_stream'),
        school_club=data.get('school_club'),
        proffession=data.get('proffession'),
        football_team=data.get('football_team'),
        about_you=data.get('about_you'),
        user_id = get_jwt_identity())
        db.session. add(post)
        db.session.commit()
        return profile.to_dict()


    #route to get user's profile
    @jwt_required()
    def get(self, id):
        profile = Profile.query.filter_by(id = user.id).first()
        return profile.to_dict()

    #route to update profile
    @jwt_required()
    def patch(self, id):
        data = patch_args.parse_args()
        profile = Profile.query.get(id = user.id)
        if profile:
            profile.house = data.get('house')
            profile.class_stream = data.get('class_stream')
            profile.school_club = data.get('school_club')
            profile.proffession = data.get('proffession')
            profile.football_team = data.get('football_team')
            profile.about_you = data.get('about_you')
            db.session.commit()
            return {"msg": "profile updated succesfully"}
        else:
            return {"msg": "Error updating profile!"}

    #route to delete post
    @jwt_required()
    def delete(self, id):
        profile = Profile.query.get(id = user.id)
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return {'message': 'Profile has been deleted'}
        else:
            return {'message': 'Error deleting profile'}


api.add_resource(ProfileById, '/profile')
        

