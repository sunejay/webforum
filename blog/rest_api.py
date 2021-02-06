#from flask import Blueprint
from blog import api_manager
from blog.models import User, Post, Group

#rest_api = Blueprint('rest_api', __name__)


class Api:
    user_api = api_manager.create_api(User, methods=['GET', 'POST'])
    post_api = api_manager.create_api(Post, methods=['GET', 'POST'])
    #api.create_api(Comment, methods=['GET', 'POST'])

    api_manager.create_api(Group, methods=['GET', 'POST'])
























