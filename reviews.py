#import needed dependancies
from flask import Flask
from models import db , Post, User, Review
from flask_restful import reqparse, Resource, Api
from flask import Blueprint
from auth import auth_bp, jwt, admin_required
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, verify_jwt_in_request


reviews_bp = Blueprint('reviews', __name__)
api = Api(reviews_bp)

#post arguments
post_args = reqparse.RequestParser()
post_args.add_argument('text')
post_args.add_argument('user_id')
post_args.add_argument('post_id')

#patch arguments
patch_args = reqparse.RequestParser()
patch_args.add_argument('text')
patch_args.add_argument('user_id')
patch_args.add_argument('post_id')

class ReviewById(Resource):

    #route to get all reviews for a single  post
    @jwt_required()
    def get(self, post_id):
        reviews = Review.query.filter_by(post_id=post_id).all()
        if reviews:
            return [review.to_dict() for review in reviews]
        else:
            return {'message': 'No reviews found for the specified post'}, 404
            
    #post a new review
    @jwt_required()
    def post(self, post_id):
        data = post_args.parse_args()
        current_user_id = get_jwt_identity()
        post = Post.query.get(post_id)

        # check if user exists and is authenticated
        if current_user_id:
            review_text = data.get('text')
            review = Review(text=review_text, user_id=current_user_id, post_id=post_id)
            db.session.add(review)
            db.session.commit()
            return {'message': 'Review added successfully'}, 201
        else:
            return {'message': 'User not authenticated'}, 401

class ReviewDelete(Resource):

    #delete a review
    @admin_required()
    def delete(self, id):
        review = Review.query.filter_by(id = id).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            return {'message': 'Review has been deleted'}
        else:
            return {'message': 'Error deleting review'}

api.add_resource(ReviewById, '/reviews/<int:post_id>')
api.add_resource(ReviewDelete, '/reviewdelete/<int:id>')

    
