from datetime import datetime
from email.policy import default
from app import db
from datetime import date
class Users(db.Document):
    username = db.StringField(required=True, unique=True)
    name = db.StringField(required=True, max_length=30)
    password = db.StringField(required=True, min_length=5)
    role = db.StringField(default="author")
class Categories(db.Document):
    name = db.StringField(required=True, unique=True, max_length=100)
    slug = db.StringField(required=True, unique=True, max_length=100)
    
class Tags(db.Document):
    name = db.StringField(required=True, unique=True, max_length=50)
class Posts(db.Document):
    author = db.ReferenceField(Users)
    title = db.StringField(required=True)
    cover = db.StringField(required=True)
    slug = db.StringField(required=True, unique=True)
    category = db.ReferenceField(Categories)
    content = db.StringField(required=True)
    description = db.StringField(required=True)
    view = db.IntField(default=0)
    tags = db.ListField(db.ReferenceField(Tags))
    posted_at = db.DateField(default=date.today())