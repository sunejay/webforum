from flask import Blueprint
from flask_wtf.file import FileField, FileAllowed
from flask_admin.contrib.sqla import ModelView
from blog.models import Group, User, Post, Category, Tag

admins = Blueprint('admins', __name__)


class UserModelView(ModelView):
    column_filters = ['username', 'email', 'admin']
    column_list = ['username', 'email', 'admin', 'roles', 'date_joined']
    column_searchable_list = ['username', 'email']
    #column_sortable_list = ['username', 'admin']
    form_columns = ['username', 'email', 'image_file', 'password', 'admin']
    form_args = {
        'image_file': {'validators': [FileAllowed(['jpg', 'png', 'gif'])]},
    }
    form_overrides = {'image_file': FileField}
    '''form_extra_fields = {
        'password': PasswordField('New password'),
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password_hash = User.make_password(form.password.data)
        return super(UserModelView, self).on_model_change(form, model, is_created)'''


class GroupModelView(ModelView):
    column_filters = [Category.name]
    column_list = ['name', 'description', 'category']
    column_searchable_list = ['name', 'description']
    form_columns = ['name', 'icon', 'description', 'category']
    form_args = {
        'icon': {'validators': [FileAllowed(['gif'])]},
    }
    form_overrides = {'icon': FileField}


class PostModelView(ModelView):
    column_filters = [Group.name, User.username, User.email, Tag.name, 'date_posted']
    column_list = ['title', 'group', 'author', 'tease', 'tag_list', 'date_posted']
    column_searchable_list = ['title', 'content']
    column_select_related_list = ['author'] # Efficiently SELECT the author
    form_columns = ['title', 'content', 'image_file', 'group', 'author', 'tags']
    form_args = {
        'image_file': {'validators': [FileAllowed(['jpg', 'png', 'gif'])]},
    }
    form_overrides = {'image_file': FileField}
    form_ajax_refs = {
        'author': {
            'fields': (User.username, User.email),
        },
    }


class CommentModelView(ModelView):
    column_filters = [Post.title, User.username, User.email, 'date_posted']
    column_list = ['author', 'tease', 'date_posted']
    column_searchable_list = ['content']
    column_select_related_list = ['author'] # Efficiently SELECT the author
    form_columns = ['content', 'image_file', 'author']
    form_args = {
        'image_file': {'validators': [FileAllowed(['jpg', 'png', 'gif'])]},
    }
    form_overrides = {'image_file': FileField}
    form_ajax_refs = {
        'author': {
            'fields': (User.username, User.email),
        },
    }


class TagModelView(ModelView):
    column_filters = ['name']
    column_searchable_list = ['name']
    form_columns = ['name']



'''
class UserAdminView(ModelView):
    def create_model(self, form):
        if 'C' not in current_user.roles:
            flash('You are not allowed to create users.', 'warning')
            return
        model = self.model(
            form.username.data, form.password.data,
            form.admin.data,
            form.notes.data
        )
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    def update_model(self, form, model):
        if 'U' not in current_user.roles:
            flash('You are not allowed to edit users.', 'warning')
            return
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                flash('Passwords must match')
                return
            model.pwdhash = generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()

    def delete_model(self, model):
        if 'D' not in current_user.roles:
            flash('You are not allowed to delete users.', 'warning')
            return
        super(UserAdminView, self).delete_model(model)

    def is_action_allowed(self, name):
        if name == 'delete' and 'D' not in current_user.roles:
            flash('You are not allowed to delete users.', 'warning')
            return False
        return True
'''











































































