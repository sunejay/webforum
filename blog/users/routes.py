from flask import render_template, url_for, flash, redirect, request, Blueprint,g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from blog import db
from blog.models import User, Post
from blog.main.forms import SearchForm
from .forms import  RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, ChangePasswordForm
from blog.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.before_request
def before_request():
    if current_user.is_authenticated or current_user.is_anonymous:
        g.search_form = SearchForm()


@users.route('/search')
#@login_required
def search():
    g.search_form = SearchForm()
    if not g.search_form.validate():
        return redirect(request.referrer)
        #return redirect(url_for('main.home'))
    posts, total = Post.search(g.search_form.q.data)
    return render_template('search.html', title='Search', posts=posts)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Your account is created successfully', 'success')
        return redirect(url_for('main.home'))
    return render_template('user/register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('main.home'))
        else:
            flash(f'Login Unsuccessful. please use a valid email and password!', 'danger')
    return render_template('user/login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Account updated successfully', 'success')
        redirect(url_for('.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_img/' + current_user.image_file)
    return render_template('user/account.html', title='Account', img_file=img_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
    return render_template('user/user_posts.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('.login'))
    return render_template('user/reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('.login'))
    return render_template('user/reset_token.html', title='Reset Password', form=form)


@users.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            hashed_pw = generate_password_hash(form.new_password.data)
            current_user.password = hashed_pw
            db.session.commit()
            flash(f'Your password is successfully updated', 'success')
            return redirect(url_for('.account'))
        else:
            flash(f'Enter valid old password', 'danger')
    return render_template('user/change_password.html', form=form,)



@users.route('/follow/<string:username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash(f'You are already following this user.', 'info')
        return redirect(url_for('.user_posts', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}', 'success')
    return redirect(request.referrer)


@users.route('/unfollow/<string:username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are no longer following {username}', 'info')
    return redirect(request.referrer)


@users.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followed_by = user.followers.all()
    return render_template('user/followers.html', user=user, title=f"Followers of {username}", followed_by=followed_by)


@users.route('/following/<username>')
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    follows = user.followed.all()
    return render_template('user/following.html', user=user, title=f"Followed by {username}", follows=follows)






















