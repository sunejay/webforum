from flask import g
from flask import render_template, request, Blueprint
from blog.models import Post, User, Group, Category
from flask_login import current_user
from .forms import SearchForm


main = Blueprint('main', __name__)


@main.before_request
def before_request():
    if current_user.is_authenticated or current_user.is_anonymous:
        g.search_form = SearchForm()


@main.route('/search')
#@login_required
def search():
    g.search_form = SearchForm()
    if not g.search_form.validate():
        return redirect(request.referrer)
        #return redirect(url_for('main.home'))
    posts, total = Post.search(g.search_form.q.data)
    return render_template('search.html', title='Search', posts=posts)


@main.route('/')
@main.route('/home')
def home():
    user_obj = User.query.all()
    cats = Category.query.all()
    gps = Group.query.all()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    #groups = [g[:4] for g in Group.query.all()]
    users = user_obj[:4]
    groups = gps[:4]
    topics = posts[:4]
    return render_template('home.html', posts=posts, topics=topics,
                           users=users, groups=groups, cats=cats)


@main.route('/about')
def about():
    return render_template('mgt/about.html')