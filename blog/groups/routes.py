from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, g
from flask_login import current_user, login_required
from blog import db
from blog.models import Category, Group
from blog.main.forms import SearchForm
from .forms import GroupForm, CategoryForm
from blog.utils import save_icon


groups = Blueprint('groups', __name__)


@groups.before_request
def before_request():
    if current_user.is_authenticated or current_user.is_anonymous:
        g.search_form = SearchForm()


@groups.route('/search')
#@login_required
def search():
    g.search_form = SearchForm()
    if not g.search_form.validate():
        return redirect(request.referrer)
        #return redirect(url_for('main.home'))
    posts, total = Post.search(g.search_form.q.data)
    return render_template('search.html', title='Search', posts=posts)



@groups.route('/join/<int:group_id>/<action>')
@login_required
def join_action(group_id, action):
    group = Group.query.filter_by(id=group_id).first_or_404()
    if action == 'join':
        current_user.join(group)
        db.session.commit()
    elif action == 'leave':
        current_user.leave(group)
        db.session.commit()
    return redirect(request.referrer)


@groups.route('/group/new', methods=['GET', 'POST'])
@login_required
def new_group():
    form = GroupForm()
    categories = [(c.id, c.name) for c in Category.query.all()]
    form.category.choices = categories
    if form.validate_on_submit():
        group = Group(name=form.name.data, icon=save_icon(form.icon.data),
                      description=form.description.data,
                      category=Category.query.get_or_404(form.category.data))
        db.session.add(group)
        db.session.commit()
        flash('A new Group has been created!', 'success')
        return redirect(request.referrer)
    return render_template('group/create_group.html', title='New Group', form=form, legend='New Group')











































