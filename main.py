from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import datetime
from flask import abort
from functools import wraps
from flask_gravatar import Gravatar
date = datetime.datetime.now()
day = date.strftime("%d/%m/%y")



## Delete this code:
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return LogIn.query.get(int(user_id))

class LogIn(UserMixin, db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(100))
    posts = relationship('BlogPost', back_populates='author')
    user_comment = relationship('Comment', back_populates='user')
##CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True,)
    author_id = db.Column(db.Integer, db.ForeignKey('login.id'))
    author = relationship('LogIn', back_populates='posts')
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    blog_comment = relationship('Comment', back_populates='post')

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('login.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('blogpost.id'))
    user = relationship('LogIn', back_populates='user_comment')
    post = relationship('BlogPost', back_populates='blog_comment')
    comment = db.Column(db.String(250), nullable=True)
db.create_all()

year = date.strftime("%y")



class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class Register(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Log(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Commenter(FlaskForm):
    comm = CKEditorField('Comments', validators=[DataRequired()])
    submit = SubmitField("Submit")
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def get_all_posts():
    aller = BlogPost.query.all()

    return render_template("index.html", all_posts=aller, current_user=current_user)
@app.route('/about-me')
def about():

    return render_template("about.html")

@app.route('/delete/<int:post_id>')
def delete_posts(post_id):
    if current_user.id == 1:
        forum = BlogPost.query.get(post_id)
        db.session.delete(forum)
        try:
            db.session.commit()
        except:
            pass
        return redirect(url_for('get_all_posts'))
    else:
        return redirect(url_for('get_all_posts'))

@app.route("/post/<int:index>", methods=['POST', 'GET'])
def show_post(index):
    gh = BlogPost.query.get(index)
    fast = Comment.query.filter_by(post_id=index).all()
    requested_post = gh
    print(gh.author.name)
    comment = Commenter()
    if comment.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        dh = comment.comm.data
        yu = gh
        er = current_user
        ty = Comment(comment=dh,user=er,post=yu)
        db.session.add(ty)
        try:
            db.session.commit()
        except:
            pass
        return redirect(url_for('show_post', index=index))
    return render_template("post.html", post=requested_post, vroom=fast, forms=comment, df=current_user)


@app.route("/edit/<int:post_id>", methods=['POST','GET'])
@admin_only
def edit_post(post_id):
    forum = BlogPost.query.get(post_id)

    requested_post = CreatePostForm(
        title=forum.title,
        subtitle=forum.subtitle,
        body=forum.body,
        author=forum.author,
        image_url=forum.img_url
    )
    if request.method == 'POST':
        forum.title = requested_post.title.data
        forum.subtitle = requested_post.subtitle.data
        forum.img_url = requested_post.img_url.data
        forum.body = requested_post.body.data
        try:
            db.session.commit()
        except:
            pass
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", forms=requested_post, is_edit=True, gh=current_user)

@app.route("/new", methods=['POST','GET'])
@admin_only
def new_post():
    fins = CreatePostForm()
    print(current_user)
    if fins.validate_on_submit():

        gen = fins.title.data
        gean = fins.subtitle.data
        fean = fins.author.data
        fen = fins.img_url.data
        po = fins.body.data
        new_table = BlogPost(title=gen, subtitle=gean, date=day, body=po, author=current_user, img_url=fen)
        db.session.add(new_table)
        try:
            db.session.commit()
        except:
            pass
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", forms=fins, current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=['POST','GET'])
def login():
    reg = Log()
    reg.validate_on_submit()
    if request.method == 'POST':
        eer = reg.email.data
        ett = reg.password.data
        user = LogIn.query.filter_by(email=eer).first()

        if not user:
            flash("Invalid Email")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, ett):
            flash("Invalid Password")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", forms=reg)

@app.route("/register", methods=['POST', 'GET'])
def register():
    reg = Register()
    fit = LogIn().query.all()
    op = []

    for lis in fit:
        op.append(lis.email)

    if request.method == 'POST':

        gh = reg.name.data
        lh = reg.email.data
        jh = reg.password.data
        fh = generate_password_hash(jh, salt_length=10)
        dh = LogIn(name=gh, email=lh, password=fh)
        if lh in op:
            flash("Email already Exsists")
            return redirect(url_for('login'))
        else:
            db.session.add(dh)
            try:
                db.session.commit()
                login_user(less)
            except:
                pass
            return redirect(url_for('get_all_posts'))
    return render_template("register.html", forms=reg)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug = True)