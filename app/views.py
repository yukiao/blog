from crypt import methods
import json
import os
import functools
from datetime import datetime, timedelta
from unicodedata import category
from flask import session, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_ckeditor import upload_success, upload_fail
from app import app
from app import bcrypt, csrf
from app.models import Posts, Tag, User, Category
from app.forms import LoginForm, PostForm
from mongoengine.queryset.visitor import Q

# Fungsi untuk mengautentikasi user
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "_id" not in session:
            return redirect(url_for("login", next_path=[request.full_path]))
        return func(*args, **kwargs)
    
    return secure_function

def get_user():
    user = None
    if '_id' in session:
        user = session.get('_id')
    
    return user

def get_formatted_date(date):
    month_dict = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }
    
    day = date.day
    month = month_dict[date.month]
    year = date.year
    
    return f'{day} {month} {year}'

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route("/")
def index():
    user = get_user()

    articles = Posts.objects()
    most_viewed = Posts.objects().order_by('-view').limit(5)
    category = Category.objects()
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=5
    
    offset = (page-1) * per_page
    
    paginated_articles = articles[offset:offset + per_page]
    
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)

    all_tags = Tag.objects()

    pagination = Pagination(page=page, total=len(articles), per_page=5)
    return render_template("screens/index.html", user=user, articles=paginated_articles, most_viewed=most_viewed, category=category, pagination=pagination, all_tags=all_tags)

# Post Route
@app.route("/posts/<post_slug>")
def posts(post_slug):
    user = get_user()
    
    article = Posts.objects(slug=post_slug).first()
    Posts.objects(slug=post_slug).update_one(inc__view=1)
    
    article.reload()
    
    article.posted_at = get_formatted_date(article.posted_at)
    
    author_articles = Posts.objects(Q(author = article.author) & Q(slug__ne=post_slug)).limit(5)
    
    return render_template("screens/post.html", article=article, author_articles=author_articles, user=user)

#Category
@app.route("/categories")
def categories():
    user = get_user()
    
    articles = Posts.objects()
    
    categories = Category.objects()
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    offset = (page-1) * per_page
    paginated_articles = articles[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/category.html", articles=paginated_articles, pagination=pagination, categories=categories, active='all', user=user)

@app.route("/categories/<category_slug>")
def categories_detail(category_slug):
    user = get_user()
    
    category = Category.objects(slug=category_slug).first()
    articles = Posts.objects(category=category)
    
    categories = Category.objects()
    print(categories)
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    
    offset = (page-1) * per_page
    paginated_articles = articles[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/category.html", articles=paginated_articles, pagination=pagination, categories=categories, active=category.name, user=user)

@app.route("/tags")
def tags():
    user = get_user()
    articles = Posts.objects()
    
    return render_template("screens/tag.html", user=user, articles=articles)

@app.route("/about")
def about():
    user = get_user()
    return render_template("screens/about.html", user=user)

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
        return render_template("screens/login.html", form=form, next_path=next_path)


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    user_id = session.get('_id')
    total_posts = len(Posts.objects(author=user_id))
    
    author = User.objects(id = user_id).first()
    
    pipeline = [
        {
            "$match": {"author": author.id}
        },
        {
            "$group": {
                "_id": 1,
                "total_views" : {
                    "$sum": "$view"
                }
            }
        }
    ]
    
    total_views = Posts.objects(author = user_id).sum("view")
    
    return render_template('screens/admin/dashboard.html', total_posts=total_posts, total_views=total_views)

@app.route('/admin/posts')
@login_required
def admin_post():
    user_id = session.get('_id')
    posts = Posts.objects(author=user_id)
    
    return render_template('screens/admin/post.html', posts=posts)

@app.route("/admin/posts/new", methods=['GET', 'POST'])
@login_required
def new_article():
    form = PostForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            user_id = session.get('_id')
            author = User.objects(id = user_id).first()
            
            word_array = form.title.data.strip().lower().split(" ")
            slug = "-".join(word_array)
            category = Category.objects(id=request.form['category']).first()
            
            tags = request.form.getlist('tags[]')
            
            tag_list = []
            
            for tag in tags:
                tag_exist = Tag.objects(name=tag).first()
                if not tag_exist:
                    new_tag = Tag(name=tag)
                    new_tag.save()
                    tag_list.append(new_tag)
                else:
                    tag_list.append(tag_exist)
                    
            new_post = Posts(
                author=author,
                title=request.form['title'],
                slug=slug,
                tags=tag_list,
                cover=request.form['cover'],
                category=category,
                content=request.form['content'],
            )
            new_post.save()
            
            return redirect('/admin/posts')
        
    return render_template("screens/admin/add_article.html", form=form)

@app.route("/admin/posts/edit/<article_id>", methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    form = PostForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            
            article = Posts.objects(id = article_id).first()

            word_array = form.title.data.strip().lower().split(" ")
            slug = "-".join(word_array)
            category = Category.objects(id=form.category.data).first()
            
            print(form.category.data)

            field_data = {
                "title": form.title.data,
                "slug": slug,
                "cover": form.cover.data,
                "category": category,
                "content": form.content.data,
                "posted_at": form.postedAt.data
            }
            
            article.update(**field_data)
            article.reload()
            
            print(article.category)
            return redirect('/admin/posts')
    
    article = Posts.objects(id = article_id).first()
    
    form.title.default = article.title
    form.cover.default = article.cover
    form.content.default = article.content
    form.category.default = article.category.id
    form.postedAt.default = article.posted_at
    
    form.process()
    
    return render_template("screens/admin/edit_article.html", form=form, article_id=article.id)

@app.route('/admin/posts/delete/<article_id>', methods=['POST'])
@login_required
def delete_post(article_id):
    user_id = session.get('_id')
    
    Posts.objects(id=article_id).first().delete()
    
    posts = Posts.objects(author=user_id)
    
    return render_template('screens/admin/post.html', posts=posts)

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