import os
import re
import json
from bs4 import BeautifulSoup
from datetime import timedelta
from flask import session, flash, redirect, render_template, request, send_from_directory, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_ckeditor import upload_success, upload_fail
from app import app
from app import bcrypt
from app.helpers.category import getCategoriesPair
from app.models import Posts, Tags, Users, Categories
from app.forms import CategoryForm, LoginForm, PostForm, RegisterForm
from mongoengine.queryset.visitor import Q
from app.helpers.get_formated_date import get_formatted_date
from app.helpers.get_user import get_user
from app.helpers.login_required import login_required

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route("/")
def index():
    user = get_user()

    articles = Posts.objects()
    most_viewed = Posts.objects().order_by('-view').limit(5)
    category = Categories.objects()
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=5
    
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)
        
    print(paginated_articles[1].posted_at)

    all_tags = Tags.objects()

    top_tags = Posts.objects().aggregate([
        {
            "$unwind": "$tags"
        },
        {
            "$lookup": {
                "from": "tags",
                "localField": "tags",
                "foreignField": "_id",
                "as": "tags"
            }
        },
        {
            "$group":{
                "_id": "$tags.name",
                "total": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "total": -1
            }
        },
        {
            "$limit": 10
        },
        {
            "$project": {
                "name": "$_id",
            }
        }
    ])
    
    all_tags = []
    
    for tag in top_tags:
        all_tags.append({
            "name": tag['name'][0]
        })

    pagination = Pagination(page=page, total=len(articles), per_page=5)
    return render_template("screens/index.html", user=user, articles=paginated_articles, most_viewed=most_viewed, category=category, pagination=pagination, top_tags=all_tags)


# Post Route
@app.route("/posts/<post_slug>")
def posts(post_slug):
    user = get_user()
    
    article = Posts.objects(slug=post_slug).first()
    
    if not article:
        return redirect('/error')
    
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
    
    categories = Categories.objects()
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)
        
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/category.html", articles=paginated_articles, pagination=pagination, categories=categories, active='all', user=user)

@app.route("/categories/<category_slug>")
def categories_detail(category_slug):
    user = get_user()
    
    category = Categories.objects(slug=category_slug).first()
    
    if not category:
        return redirect('/error')
    
    articles = Posts.objects(category=category)
    
    categories = Categories.objects()
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)
        
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/category.html", articles=paginated_articles, pagination=pagination, categories=categories, active=category.name, user=user)

@app.route("/tags")
def tags():
    user = get_user()
    articles = Posts.objects()
    top_tags = Posts.objects().aggregate([
        {
            "$unwind": "$tags"
        },
        {
            "$lookup": {
                "from": "tags",
                "localField": "tags",
                "foreignField": "_id",
                "as": "tags"
            }
        },
        {
            "$group":{
                "_id": "$tags.name",
                "total": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "total": -1
            }
        },
        {
            "$limit": 10
        },
        {
            "$project": {
                "name": "$_id",
            }
        }
    ])
    
    all_tags = []
    
    for tag in top_tags:
        all_tags.append({
            "name": tag['name'][0]
        })
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)
    
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/tag.html", user=user, articles=paginated_articles, tags=all_tags, pagination = pagination, )

@app.route("/tags/<tag>")
def tags_detail(tag):
    user = get_user()
    lookup_tag = Tags.objects(name=tag).first()

    if not lookup_tag:
        return redirect('/error')
    
    articles = Posts.objects(tags=lookup_tag)
    
    top_tags = Posts.objects().aggregate([
        {
            "$unwind": "$tags"
        },
        {
            "$lookup": {
                "from": "tags",
                "localField": "tags",
                "foreignField": "_id",
                "as": "tags"
            }
        },
        {
            "$group":{
                "_id": "$tags.name",
                "total": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "total": -1
            }
        },
        {
            "$limit": 10
        },
        {
            "$project": {
                "name": "$_id",
            }
        }
    ])
    
    all_tags = []
    
    for tag in top_tags:
        all_tags.append({
            "name": tag['name'][0]
        })
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    
    for article in paginated_articles:
        article.posted_at = get_formatted_date(article.posted_at)
    
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/tag.html", user=user, articles=paginated_articles,  pagination=pagination, tags=all_tags)

@app.route("/archives/<int:year>/<int:month>")
def archive(year, month):
    user = get_user()
    
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "author",
                "foreignField": "_id",
                "as": "author"
            }
        },
        {
            "$project": {
                "author": "$author.name",
                "title": "$title",
                "slug": "$slug",
                "cover": "$cover",
                "category": "$category",
                "content": "$content",
                "view": "$view",
                "posted_at": "$posted_at",
                "description": "$description",
                "year": {
                    "$year": "$posted_at"
                },
                "month": {
                    "$month": "$posted_at"
                }
            },
        },
        {
            "$match": {
                "$and": [
                {"year": year},
                {"month": month}
                ]
            }
        },
    ]
    
    articles = []
    
    year = Posts.objects().aggregate(pipeline)
    for y in year:
        articles.append(y)
        
    print(articles)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page=6
    
    offset = (page-1) * per_page
    
    if len(articles) < offset:
        return redirect("/error")
    
    paginated_articles = articles[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(articles), per_page=per_page)
    
    return render_template("screens/archive.html", user=user, articles=paginated_articles,  pagination=pagination)

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

#     user = Users(username=username, password=hashed_password)
#     res = user.save()
#     return jsonify(res)

# @csrf.exempt
# @app.route("/new_category", methods=["POST"])
# def new_category_add():
#     name = request.json['name']
#     slug = request.json['slug']
    
#     new_category = Categories(name=name, slug=slug)
#     new_category.save()
    
#     return jsonify(new_category)


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
            
            user = Users.objects(username=username).first()

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

@app.route("/search")
def search():
    keyword = request.args.get("keyword", default="")
    
    regex = re.compile(f'.*{keyword}.*', flags=re.IGNORECASE)
    
    articles = Posts.objects(title=regex)
    
    return render_template('screens/search.html', articles=articles)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    user_id = session.get('_id')
    total_posts = len(Posts.objects(author=user_id))
    
    author = Users.objects(id = user_id).first()
    
    total_views = Posts.objects(author = user_id).sum("view")
    
    return render_template('screens/admin/dashboard.html', total_posts=total_posts, total_views=total_views, author=author)

@app.route('/admin/posts')
@login_required
def admin_post():
    user_id = session.get('_id')
    posts = Posts.objects(author=user_id)
    author = Users.objects(id = user_id).first()
    
    return render_template('screens/admin/post.html', posts=posts, author=author)

@app.route("/admin/posts/new", methods=['GET', 'POST'])
@login_required
def new_article():
    
    form = PostForm()
    form.category.choices = getCategoriesPair()
    
    user_id = session.get('_id')
    author = Users.objects(id = user_id).first()

    if request.method == 'POST':
        if form.validate_on_submit():
            word_array = form.title.data.strip().lower().split(" ")
            slug = "-".join(word_array)
            category = Categories.objects(id=request.form['category']).first()
            
            soup = BeautifulSoup(form.content.data)
            description = soup.get_text().replace(u'\xa0', u' ')            
            description = " ".join(description.split(" ")[:20])
            
            tags = request.form.getlist('tags[]')
            
            tag_list = []
            
            for tag in tags:
                tag_exist = Tags.objects(name=tag).first()
                if not tag_exist:
                    new_tag = Tags(name=tag)
                    new_tag.save()
                    tag_list.append(new_tag)
                else:
                    tag_list.append(tag_exist)
                    
            new_post = Posts(
                author=author,
                title=request.form['title'],
                slug=slug,
                tags=tag_list,
                description = description,
                cover=request.form['cover'],
                category=category,
                content=request.form['content'],
            )
            new_post.save()
            
            return redirect('/admin/posts')
        
    return render_template("screens/admin/add_article.html", form=form, author=author)

@app.route("/admin/posts/edit/<article_id>", methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    form = PostForm()
    form.category.choices = getCategoriesPair()
    
    user_id = session.get('_id')
    author = Users.objects(id = user_id).first()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            
            article = Posts.objects(id = article_id).first()

            word_array = form.title.data.strip().lower().split(" ")
            slug = "-".join(word_array)
            category = Categories.objects(id=form.category.data).first()
            
            soup = BeautifulSoup(form.content.data)
            description = soup.get_text().replace(u'\xa0', u' ')
            description = " ".join(description.split(" ")[:20])
            
            tags = request.form.getlist('tags[]')
            
            tag_list = []
            
            for tag in tags:
                tag_exist = Tags.objects(name=tag).first()
                if not tag_exist:
                    new_tag = Tags(name=tag)
                    new_tag.save()
                    tag_list.append(new_tag)
                else:
                    tag_list.append(tag_exist)

            field_data = {
                "title": form.title.data,
                "slug": slug,
                "cover": form.cover.data,
                "category": category,
                "description": description,
                "tags": tag_list,
                "content": form.content.data,
                "posted_at": form.postedAt.data
            }
            
            article.update(**field_data)
            article.reload()
            
            print(article.category)
            return redirect('/admin/posts')
    
    article = Posts.objects(id = article_id).first()
    
    tags = []
    
    if article.tags:
        for tag in article.tags:
            tags.append(json.loads(tag.to_json()))
    
    form.title.default = article.title
    form.cover.default = article.cover
    form.content.default = article.content
    form.category.default = article.category.id
    form.postedAt.default = article.posted_at
    
    form.process()
    
    return render_template("screens/admin/edit_article.html", form=form, article_id=article.id, tags= json.dumps(tags), author=author)

@app.route('/admin/posts/delete/<article_id>', methods=['POST'])
@login_required
def delete_post(article_id):
    user_id = session.get('_id')
    
    Posts.objects(id=article_id).first().delete()
    
    return redirect('/admin/posts')

@app.route('/admin/authors')
@login_required
def manage_user():
    user_id = session.get('_id')
    author = Users.objects(id=user_id).first()
    
    users = Users.objects()
    
    return render_template('screens/admin/manage_user.html', author=author, users=users)

@app.route('/admin/authors/new', methods=["GET", "POST"])
@login_required
def new_author():
    user_id = session.get('_id')
    author = Users.objects(id=user_id).first()
    users = Users.objects()
    
    form = RegisterForm()
    
    if request.method == 'POST':
        username = form.username.data
        
        user_exist = Users.objects(username=username).first()
        if(user_exist):
            return render_template('screens/admin/add_author.html', error="Account already exists", author=author, users=users, form=form)
        
        name = form.name.data
        password = form.password.data
    
        hashed_password = bcrypt.generate_password_hash(password, 10).decode('utf-8')
        user = Users(username=username, name=name, password=hashed_password)
        user.save()
        
        return redirect("/admin/authors")
    
    return render_template('screens/admin/add_author.html', author=author, users=users, form=form)

@app.route('/admin/categories')
@login_required
def manage_category():
    user_id = session.get('_id')
    author = Users.objects(id=user_id).first()
    
    categories = Categories.objects()
    
    return render_template('screens/admin/manage_category.html', author=author, categories=categories)

@app.route('/admin/categories/new', methods=["GET", "POST"])
@login_required
def new_category():
    user_id = session.get('_id')
    author = Users.objects(id=user_id).first()
    
    form = CategoryForm()
    
    if request.method == 'POST':
        name = form.name.data
        slug = "-".join(name.lower().split(" "))
        
        category_exist = Categories.objects(slug=slug).first()
        if(category_exist):
            return render_template('screens/admin/add_category.html', error="Category already exists", author=author, form=form)
        
        category = Categories(name=name, slug=slug)
        category.save()
        
        return redirect("/admin/categories")
    
    return render_template('screens/admin/add_category.html', author=author, form=form)

# @csrf.exempt
# @app.route('/category', methods=['GET', 'POST'])
# def admin_category():
#     if request.method == 'POST':
#         category_name = request.json['category']
#         category_name.lower()
#         try:
#             new_category = Categories(name=category_name)
#             new_category = new_category.save()
#             return jsonify({
#                 "status": "success",
#                 "message": "category created",
#                 "data" : new_category
#             })
#         except:
#             return {
#                 "status" : "failed",
#                 "message": "something went wrong"
#             }
            
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

@app.route('/error')
def error():
    return render_template("screens/error.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("screens/error.html")
