import os
from flask import Flask
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['CKEDITOR_FILE_UPLOADER'] = "upload"
app.config['CKEDITOR_ENABLE_CSRF'] = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'blog',
    'host': 'mongodb+srv://yukiao_blog:yukiao_blog@cluster0.9arzc.mongodb.net/blog?retryWrites=true&w=majority',
    # 'port': 27017
}

csrf = CSRFProtect(app)
ckeditor = CKEditor(app)
db = MongoEngine(app)
bcrypt = Bcrypt(app)

from app import views, models
