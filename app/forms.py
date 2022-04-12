import datetime
from tokenize import String
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, PasswordField, DateField
from wtforms.fields import SelectField
from datetime import datetime
from wtforms.validators import DataRequired, URL
from app.helpers.category import getCategoriesPair
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    cover = StringField("Cover Image", validators=[DataRequired(), URL(require_tld=False, message="Not a valid image")])
    category = SelectField('Category', choices=getCategoriesPair())
    content = CKEditorField('Content')
    postedAt = DateField('Posted At', default=datetime.utcnow )

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(0)])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    
class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(0)])