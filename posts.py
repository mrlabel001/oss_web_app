#import needed dependancies
from flask import Flask
from models import db , Post, User
from flask_restful import reqparse, Resource, Api
from flask import Blueprint
from auth import auth_bp, jwt, admin_required
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, verify_jwt_in_request


posts_bp = Blueprint('posts', __name__)
api = Api(posts_bp)

#post arguments
post_args = reqparse.RequestParser()
post_args.add_argument('post_url')
post_args.add_argument('post_description')
post_args.add_argument('user_id', help='user_id is required')

#patch arguments
patch_args = reqparse.RequestParser()
patch_args.add_argument('post_url')
patch_args.add_argument('post_description')
patch_args.add_argument('user_id', help='user_id is required')

class Posts(Resource):

    #route to get all posts
    @jwt_required()
    def get(self):
        posts = Post.query.all()
        return [post.to_dict() for post in posts]

    #route to add new post which is admins only!
    @admin_required()
    def post(self):
        data = post_args.parse_args()
        post = Post(post_url = data.get('post_url'), post_description=data.get('post_description'), user_id = get_jwt_identity())
        db.session. add(post)
        db.session.commit()
        return post.to_dict()

class PostsById(Resource):

    #route to update post. Admin only!
    @admin_required()
    def patch(self, id):
        data = patch_args.parse_args()
        post = Post.query.get(id)
        if post:
            post.post_url = data.get('post_url')
            post.post_description = data.get('post_description')
            db.session.commit()
            return {"msg": "Post updated succesfully"}
        else:
            return {"msg": "Error updating post!"}
        

    #route to delete post. Admin only!
    @admin_required()
    def delete(self, id):
        post = Post.query.get(id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return {'message': 'Post has been deleted'}
        else:
            return {'message': 'Error deleting post'}


api.add_resource(Posts, '/posts')
api.add_resource(PostsById, '/posts/<int:id>')
