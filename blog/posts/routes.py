from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, g
from flask_login import current_user, login_required
from blog import db
from blog.models import Post, User, Comment, Group, CommentShare, Tag, Category
from .forms import PostForm, CommentForm
from blog.main.forms import SearchForm
from blog.utils import save_image


posts = Blueprint('posts', __name__)


@posts.before_request
def before_request():
    if current_user.is_authenticated or current_user.is_anonymous:
        g.search_form = SearchForm()


@posts.route('/search')
#@login_required
def search():
    g.search_form = SearchForm()
    if not g.search_form.validate():
        return redirect(request.referrer)
        #return redirect(url_for('main.home'))
    posts, total = Post.search(g.search_form.q.data)
    return render_template('search.html', title='Search', posts=posts)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    groups = [(g.id, g.name) for g in current_user.groups.all()]
    form.group.choices = groups
    if form.validate_on_submit():

        if form.image.data and form.tags.data:
            post = Post(title=form.title.data, content=form.content.data,
                        image_file=save_image(form.image.data), author=current_user,
                        group=Group.query.get_or_404(form.group.data), tags=form.tags.data)
        elif form.tags.data:
            post = Post(title=form.title.data, content=form.content.data, author=current_user,
                        group=Group.query.get_or_404(form.group.data), tags=form.tags.data)
        elif form.image.data:
            post = Post(title=form.title.data, content=form.content.data,
                        image_file=save_image(form.image.data), author=current_user,
                        group=Group.query.get_or_404(form.group.data))
        else:
            post = Post(title=form.title.data, content=form.content.data,
                        group=Group.query.get_or_404(form.group.data), author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('post/create_post.html', title='New Post', form=form, legend='New Post')


@posts.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    comments = Comment.query.filter_by(post=post).order_by(Comment.date_posted.desc()).all()
    return render_template('post/post.html', title=post.title, post=post, comments=comments, form=form)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    groups = [(g.id, g.name) for g in current_user.groups.all()]
    form.group.choices = groups
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.group = Group.query.get_or_404(form.group.data)
        post.tags = form.tags.data
        #post.image_file = form.image.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('users.user_posts', username=post.author.username))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.group.data = post.group
        form.tags.data = post.tags
        #form.image.data = post.image_file
    return render_template('post/create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('users.user_posts', username=post.author.username))


'''@posts.route('/post/<string:username>/update', methods=['GET', 'POST'])
@login_required
def update_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
    if user != current_user:
        abort(403)
    return render_template('post/update_posts.html', title='Update Posts', posts=posts, user=user)'''


@posts.route('/comment/<int:comment_id>/share', methods=['GET', 'POST'])
@login_required
def share(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    Comment.shared(comment)
    form = CommentForm()
    if form.validate_on_submit():
        reply = Comment(content=form.content.data, author=current_user, post=comment.post, comment_id=comment.id)
        db.session.add(reply)
        db.session.commit()
        flash('You shared a reaction!', 'success')
        return redirect(url_for('posts.post', post_id=comment.post.id))
    return render_template('post/share.html', title='Share Comment', form=form, legend='Share', comment=comment)


@posts.route('/like/<int:post_id>/<action>')
@login_required
def post_like_action(post_id, action):  #post_like_action
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    elif action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)


@posts.route('/comment/like/<int:comment_id>/<action>')
@login_required
def comment_like_action(comment_id, action):  #comment_like_action
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if action == 'like':
        current_user.like_comment(comment)
        db.session.commit()
    elif action == 'unlike':
        current_user.unlike_comment(comment)
        db.session.commit()
    return redirect(request.referrer)


@posts.route('/save/<int:post_id>/<action>')
@login_required
def post_save_action(post_id, action):  #post_like_action
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'save':
        current_user.save_post(post)
        db.session.commit()
    elif action == 'unsave':
        current_user.unsave_post(post)
        db.session.commit()
    return redirect(request.referrer)


@posts.route('/comment/save/<int:comment_id>/<action>')
@login_required
def comment_save_action(comment_id, action):  #comment_like_action
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if action == 'save':
        current_user.save_comment(comment)
        db.session.commit()
    elif action == 'unsave':
        current_user.unsave_comment(comment)
        db.session.commit()
    return redirect(request.referrer)


@posts.route('/group/<string:name>')
def group(name):
    user_obj = User.query.all()
    cats = Category.query.all()
    group_name = Group.query.filter_by(name=name).first_or_404()
    gps = Group.query.all()
    posts = Post.query.filter_by(group=group_name).order_by(Post.date_posted.desc()).all()
    users = user_obj[:4]
    groups = gps[:4]
    topics = posts[:4]
    return render_template('post/group_posts.html', posts=posts, group_name=group_name,
                           topics=topics, users=users, groups=groups, cats=cats)


@posts.route('/category/<string:name>')
def category(name):
    cats = Category.query.all()
    cat_name = Category.query.filter_by(name=name).first_or_404()
    groups = Group.query.filter_by(category=cat_name)
    return render_template('post/cat_posts.html', groups=groups, cat_name=cat_name, cats=cats)


@posts.route('/tag/<string:name>')
def tag(name):
    user_obj = User.query.all()
    cats = Category.query.all()
    tag_name = Tag.query.filter_by(name=name).first_or_404()
    gps = Group.query.all()
    posts = tag_name.posts.order_by(Post.date_posted.desc()).all()
    users = user_obj[:4]
    groups = gps[:4]
    topics = posts[:4]
    return render_template('post/tag_posts.html', posts=posts, tag_name=tag_name,
                           topics=topics, users=users, groups=groups, cats=cats)



