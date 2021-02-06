from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
#from flask_script import Manager
from flask_admin import Admin, AdminIndexView, expose
from blog.config import Config
from flask_admin.contrib.sqla import ModelView
#from flask_admin.actions import ActionsMixin
from flask_marshmallow import Marshmallow
from elasticsearch import Elasticsearch
from flask_bootstrap import Bootstrap


class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin()):
            return redirect(url_for('users.login', next=request.path))
        return self.render('admin/index.html')


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
moment = Moment()
mail = Mail()
migrate = Migrate(db)
#manager = Manager()
#manager.add_command('db', MigrateCommand)
admin = Admin(index_view=IndexView())
ma = Marshmallow()
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    migrate.init_app(app)
    #manager(app)
    admin.init_app(app)
    ma.init_app(app)
    bootstrap.init_app(app)

    from blog.users.routes import users
    from blog.posts.routes import posts
    from blog.main.routes import main
    #from blog.message.routes import msg
    from blog.groups.routes import groups
    from blog.admins.routes import admins
    from blog.errors.handlers import errors
    from blog.api.routes import api

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    #app.register_blueprint(msg)
    app.register_blueprint(groups)
    app.register_blueprint(admins)
    app.register_blueprint(errors)
    app.register_blueprint(api)

    return app


from . import models
from blog.admins import routes


admin.add_view(routes.UserModelView(models.User, db.session))
admin.add_view(ModelView(models.Category, db.session))
admin.add_view(routes.GroupModelView(models.Group, db.session))
admin.add_view(routes.PostModelView(models.Post, db.session))
admin.add_view(routes.CommentModelView(models.Comment, db.session))
admin.add_view(routes.TagModelView(models.Tag, db.session))










