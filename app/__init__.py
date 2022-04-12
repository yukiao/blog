import os
from dotenv import load_dotenv
from flask import Flask
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine

if os.environ.get('FLASK_ENV') == 'development':
    load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['CKEDITOR_FILE_UPLOADER'] = "upload"
app.config['CKEDITOR_ENABLE_CSRF'] = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'blog',
    'host': os.environ.get('MONGO_DB_URI'),
}

csrf = CSRFProtect(app)
ckeditor = CKEditor(app)
db = MongoEngine(app)
bcrypt = Bcrypt(app)

from app import views, models
