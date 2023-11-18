from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user


from application import app, db
from application.models import *
from application.forms import *
from application.utils import save_image
from werkzeug.security import generate_password_hash


from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()



from application.forms import SignUpForm, EditProfileForm, VerificationResetPasswordForm
from application.models import User

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditProfileForm()


    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.username = form.username.data
        user.fullname = form.fullname.data
        # user.bio = form.bio.data

        # if form.profile_pic.data:
        #     pass
        db.session.commit()
        flash('profile updated', 'succes')
        return redirect(url_for('profile', username=current_user.username))
    
    form.username.data = current_user.username
    form.fullname.data = current_user.fullname
    
    flash('Form validation failed.', 'error')
    return render_template('edit.html', title='Edit Profile', form=form)

@app.route('/profile')
@login_required
def profile():
    # Retrieve posts for the current user
    user_posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.post_date.desc()).all()

    # Debug: Print post information to the console
    for post in user_posts:
        print(f"Post ID: {post.id}, Author ID: {post.author_id}, Photo: {post.photo}")

    # Paginate all posts for display on the page
    page = request.args.get('page', 1, type=int)
    all_posts = Post.query.order_by(Post.post_date.desc()).paginate(page=page, per_page=3)

    return render_template('profile.html', title=f'{current_user.fullname} Profile', posts=user_posts, all_posts=all_posts)




@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.email = form.email.data
            user.password = form.new_password.data
            db.session.commit()
            flash('Password successfully updated', 'success')
            return redirect(url_for('login', username=user.username))
        else:
            flash('User not found in the database', 'error')

    return render_template('forgot_password.html', title='Forgot Password', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, fullname=form.fullname.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))
    
    flash('Form validation failed.', 'error')
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CreatePostForm()

    if form.validate_on_submit():
        post = Post(
            author_id=current_user.id,
            caption=form.caption.data
        )
        post.photo = save_image(form.post_pic.data)
        db.session.add(post)
        db.session.commit()
        flash('Your image has been posted 🩷!', 'success')
        
        form.caption.data = ''

        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.post_date.desc()) \
                    .paginate(page=page, per_page=3)

    return render_template('index.html', title='Home', form=form, posts=posts)





@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)
