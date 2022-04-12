from datetime import datetime
from app import db
from datetime import date
class Users(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=5)
    
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
    view = db.IntField(default=0)
    tags = db.ListField(db.ReferenceField(Tags))
    posted_at = db.DateField(default=date.today())