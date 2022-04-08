import json
import os
import functools
from datetime import timedelta
from flask import session, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from app import app
from app import bcrypt, csrf
from app.models import Posts, User, Category
from app.forms import LoginForm, PostForm
from flask_ckeditor import upload_success, upload_fail

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
        
    articles = Posts.objects()
    return render_template("screens/index.html", user=user, articles=articles)

@app.route("/posts/<post_slug>")
def posts(post_slug):
    article = Posts.objects(slug=post_slug).first()
    return render_template("screens/post.html", article=article)

@app.route("/categories")
def categories():
    return render_template("screens/category.html")

@app.route("/tags")
def tags():
    return render_template("screens/tag.html")

@app.route("/about")
def about():
    return render_template("screens/about.html")

# @csrf.exempt
# @app.route("/register", methods=["POST"])
# def register():
#     username = request.json['username']
#     password = request.json['password']
    
#     hashed_password = bcrypt.generate_password_hash(password, 10).decode('utf-8')

#     user = User(username=username, password=hashed_password)
#     res = user.save()
#     return jsonify(res)

@app.route("/login", methods=["GET", "POST"])
def login():
    
    if "_id" in session:
        return redirect(url_for("index"))
    
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
        if form.validate_on_submit():
            user_id = session.get('_id')
            author = User.objects(id = user_id).first()
            
            word_array = request.form['title'].lower().split(" ")
            slug = "-".join(word_array)
            category = Category.objects(id=request.form['category']).first()
            print(request.form)
            new_post = Posts(
                author=author,
                title=request.form['title'],
                slug=slug,
                cover=request.form['cover'],
                category=category,
                content=request.form['content'],
            )
            new_post.save()
            return render_template("screens/admin/dashboard.html", form=form)
    return render_template("screens/admin/dashboard.html", form=form)

@app.route('/posted')
def posted():
    posts = Posts.objects().first()
    print(posts.category['name'])
    return jsonify(posts)

@csrf.exempt
@app.route('/category', methods=['GET', 'POST'])
def admin_category():
    if request.method == 'POST':
        category_name = request.json['category']
        category_name.lower()
        try:
            new_category = Category(name=category_name)
            new_category = new_category.save()
            return jsonify({
                "status": "success",
                "message": "category created",
                "data" : new_category
            })
        except:
            return {
                "status" : "failed",
                "message": "something went wrong"
            }
            
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