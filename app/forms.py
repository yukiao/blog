import datetime
from email.policy import default
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, DateTimeField, PasswordField
from wtforms.fields import SelectField
from datetime import datetime
from wtforms.validators import DataRequired

choiches = [('health', 'Health'), ('social', 'Social'), ('tech', 'Tech')]

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    category = SelectField('Category', choices=choiches)
    content = CKEditorField('Content')
    postedAt = DateTimeField('Posted At', default=datetime.utcnow, format="%d-%m-%Y %H:%M:%S" )

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])