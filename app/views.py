from datetime import timedelta
import functools
from flask import session, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from app import app
from app import bcrypt, csrf
from app.models import User
from app.forms import LoginForm, PostForm
from flask_ckeditor import upload_success, upload_fail
import os

# Fungsi untuk mengautentikasi user
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "_id" not in session:
            return redirect(url_for("login", next_path=[request.full_path]))
        return func(*args, **kwargs)
    
    return secure_function

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route("/")
def index():
    user = None
    if '_id' in session:
        user = session.get('_id')
    return render_template("screens/index.html", user=user)

@app.route("/posts/<postId>")
def posts(postId):
    print(postId)
    return render_template("screens/post.html")

@app.route("/categories")
def categories():
    return render_template("screens/category.html")

@app.route("/tags")
def tags():
    return render_template("screens/tag.html")

@csrf.exempt
@app.route("/register", methods=["POST"])
def register():
    username = request.json['username']
    password = request.json['password']
    
    hashed_password = bcrypt.generate_password_hash(password, 10).decode('utf-8')

    user = User(username=username, password=hashed_password)
    res = user.save()
    return jsonify(res)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    next_path = request.args.get('next_path')
    
    if request.method == "POST":
        if form.validate_on_submit():
            
            username = form.username.data
            raw_pass = form.password.data.encode('utf8')
            
            user = User.objects(username=username).first()

            if not user:
                flash('Account not found')
                return redirect(url_for('login'))
            
            if bcrypt.check_password_hash(user.password, raw_pass):
                session['_id'] = str(user.id)
                return redirect(url_for('index')) if not next_path else redirect(next_path)
            else:
                flash('Account not found')
                return redirect(url_for('login'))
        return render_template("screens/login.html", form=form, next_path=next_path)
    else:
        print(next_path)
        return render_template("screens/login.html", form=form, next_path=next_path)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    form = PostForm()
    
    if request.method == 'POST':
        print(request.form)
        return render_template("screens/admin/dashboard.html", form=form)
    return render_template("screens/admin/dashboard.html", form=form)

@app.route("/input",methods=["GET", "POST"])
def input():
    if request.method == "POST":
        data = request.form.get('content')
        print(data)
    form = CreatePostForm()
    return render_template("input.html",form=form)

@app.route('/protected')
@login_required
def protected():
    return "Hello"

@app.route('/files/<filename>')
def uploaded_files(filename):
    path="static/images"
    return send_from_directory(directory=path, path=filename)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg','gif', 'png', 'jpeg']:
        return upload_fail(message="Image only!")
    
    f.save(os.path.join('static/images', f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url, f.filename)

@app.route('/logout', methods=['POST'])
def logout():
    if '_id' in session:
        session.pop('_id')
    return redirect(url_for('index'))