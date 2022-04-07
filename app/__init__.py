
from flask import Flask
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine

app = Flask(__name__, )

app.config['SECRET_KEY'] = "VERY SECRET"
app.config['CKEDITOR_FILE_UPLOADER'] = "upload"
app.config['CKEDITOR_ENABLE_CSRF'] = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'blog',
    'host': '127.0.0.1',
    'port': 27017
}

csrf = CSRFProtect(app)
ckeditor = CKEditor(app)
db = MongoEngine(app)
bcrypt = Bcrypt(app)

from app import views, models
