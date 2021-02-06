from time import time
from datetime import datetime
from flask import current_app, json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, login_manager, ma
from flask_login import UserMixin
from .search import add_to_index, remove_from_index, query_index


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SearchMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchMixin.after_commit)


joins = db.Table('join',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('group_id', db.Integer, db.ForeignKey('group.id')))
                #db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))
                    #db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


post_tags = db.Table('post_tags',
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')))


post_save = db.Table('post_save',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')))


comment_save = db.Table('comment_save',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')))


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))


'''class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    image_file = db.Column(db.String(20))
    date_sent = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f"Message('{self.content}', '{self.date_sent}')" #'<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))'''


class User(db.Model, UserMixin, SearchMixin):
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    roles = db.Column(db.String(4), default='R')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    liked_posts = db.relationship('PostLike',
                                  foreign_keys='PostLike.user_id',
                                  backref='user', lazy='dynamic')
    liked_comments = db.relationship('CommentLike',
                                     foreign_keys='CommentLike.user_id',
                                     backref='user', lazy='dynamic')
    groups = db.relationship('Group', secondary=joins,
                             backref=db.backref('users', lazy='dynamic'),
                             lazy='dynamic')
    saved_posts = db.relationship('Post', secondary=post_save,
                             backref=db.backref('users', lazy='dynamic'),
                             lazy='dynamic')
    saved_comments = db.relationship('Comment', secondary=comment_save,
                                 backref=db.backref('users', lazy='dynamic'),
                                 lazy='dynamic')
    '''sent_messages = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    received_messages = db.relationship('Message',
                                        foreign_keys='Message.receiver_id',
                                        backref='receiver', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')'''

    def is_admin(self):
        return self.admin

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def join(self, group):
        if not self.has_joined(group):
            self.groups.append(group)

    def leave(self, group):
        if self.has_joined(group):
            self.groups.remove(group)

    def has_joined(self, group):
        return self.groups.filter(joins.c.group_id == group.id).count() > 0

    def like_post(self, post):
        if not self.has_liked_post(post):
            pl = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(pl)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id,
                                     PostLike.post_id == post.id).count() > 0

    def like_comment(self, comment):
        if not self.has_liked_comment(comment):
            cl = CommentLike(user_id=self.id, comment_id=comment.id)
            db.session.add(cl)

    def unlike_comment(self, comment):
        if self.has_liked_comment(comment):
            CommentLike.query.filter_by(user_id=self.id, comment_id=comment.id).delete()

    def has_liked_comment(self, comment):
        return CommentLike.query.filter(CommentLike.user_id == self.id,
                                        CommentLike.comment_id == comment.id).count() > 0

    def save_post(self, post):
        if not self.has_joined(post):
            self.saved_posts.append(post)

    def unsave_post(self, post):
        if self.has_joined(post):
            self.saved_posts.remove(post)

    def has_saved_post(self, post):
        return self.saved_posts.filter(post_save.c.post_id == post.id).count() > 0

    def save_comment(self, comment):
        if not self.has_joined(comment):
            self.saved_comments.append(comment)

    def unsave_comment(self, comment):
        if self.has_joined(comment):
            self.saved_comments.remove(comment)

    def has_saved_comment(self, comment):
        return self.saved_comments.filter(comment_save.c.comment_id == comment.id).count() > 0

    '''def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(receiver=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n'''

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @property
    def followed_posts(self):
        return Post.query.join(followers,(followers.c.followed_id == Post.user_id)).\
            filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model, SearchMixin):   #, SearchableMixin
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    #post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    group = db.relationship('Group', backref=db.backref('posts', lazy='dynamic'), lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    @property
    def tag_list(self):
        return ', '.join(tag.name for tag in self.tags)

    @property
    def tease(self):
        return self.body[:100]

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class CommentShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')
    shares = db.relationship('CommentShare', backref='comment', lazy='dynamic')

    @property
    def share(self):
        return Comment.query.get(self.comment_id)

    def shared(self):
        s = CommentShare(comment_id=self.id)
        db.session.add(s)

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"


class Group(db.Model, SearchMixin):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    icon = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    #tags = db.relationship('Tag', backref='group', lazy='dynamic')

    def __repr__(self):
        return f"Group('{self.name}')"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    groups = db.relationship('Group', backref='category', lazy='dynamic')

    def __repr__(self):
        return f"Category('{self.name}')"


class Tag(db.Model, SearchMixin):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)         #, nullable=False

    def __repr__(self):
        return f"Tag('{self.name}')"


class ReportPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ReportComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)











class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
    user = ma.HyperlinkRelated("get_users")

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post

post_schema = PostSchema()
posts_schema = PostSchema(many=True)





















































































