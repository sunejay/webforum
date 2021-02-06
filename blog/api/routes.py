from flask import Blueprint, jsonify
from blog.models import User, Post, users_schema


api = Blueprint('api', __name__)


@api.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify(result)