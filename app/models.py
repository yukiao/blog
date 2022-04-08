from datetime import datetime
from app import db
from datetime import date
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=5)
    
class Category(db.Document):
    name = db.StringField(required=True, unique=True, max_length=100)
class Posts(db.Document):
    author = db.ReferenceField(User)
    title = db.StringField(required=True)
    cover = db.StringField(required=True)
    slug = db.StringField(required=True, unique=True)
    category = db.ReferenceField(Category)
    content = db.StringField(required=True)
    view = db.IntField(default=0)
    posted_at = db.DateField(default=date.today())