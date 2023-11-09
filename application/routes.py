from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user


from application import app, db
from application.models import *
from application.forms import *
from application.utils import save_image


from application.forms import SignUpForm, EditProfileForm
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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title=f'{current_user.fullname} Profile')

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






@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)
