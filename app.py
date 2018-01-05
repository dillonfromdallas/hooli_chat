from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user,)

import forms
import Models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'jgvhbfrdjkhgjhbmnefrlvdfgcvjwmbnefrgvfbdhcjvdwbm'

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'


@loginManager.user_loader
def load_user(userid):
    try:
        return Models.User.get(Models.User.id == userid)
    except Models.DoesNotExist:
        return None


@app.before_request
def beforeRequest():
    '''Connect to the Database before each request.'''
    g.db = Models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def afterRequest(response):
    '''Close the database connection after each request.'''
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Awesome - welcome in!", "success")
        Models.User.createUser(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = Models.User.get(Models.User.email == form.email.data)
        except Models.DoesNotExist:
            flash("Your email or password does not match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Access Granted", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password does not match!", "error")
    return render_template('login.html', form=form)


@app.route('/new', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        Models.Post.create(user=g.user._get_current_object(),
                           content = form.content.data)


        flash("Message posted - thanks!")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("See ya later!", "success")
    return redirect(url_for('index'))

@app.route('/')
def index():
    stream=Models.Post.select().limit(99)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = Models.User.select().where(
                Models.User.username**username).get()
        except Models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(99)
    else:
        stream = current_user.get_stream().limit(99)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def viewPost(post_id):
    posts = Models.Post.select().where(Models.Post.id == post_id)
    if not posts.count():
        abort(404)
    return render_template('stream.html', stream=posts)



@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = Models.User.get(Models.User.username**username)
    except Models.DoesNotExist:
        abort(404)
    else:
        try:
            Models.Relationship.create(
                from_user = g.user._get_current_object(),
                to_user=to_user
            )
        except Models.IntegrityError:
            pass
        else:

            flash("You are now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = Models.User.get(Models.User.username**username)
    except Models.DoesNotExist:
        abort(404)
    else:
        try:
            Models.Relationship.get(
                from_user = g.user._get_current_object(),
                to_user = to_user
            ).delete_instance()
        except Models.IntegrityError:
            pass
        else:
            flash("You have unfollowed {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    Models.initialize()
    try:
        Models.User.createUser(
            username='dillonr',
            email='email@internet.com',
            password='password',
            admin=True
         )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)