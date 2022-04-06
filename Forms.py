from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, MonthField, PasswordField
from wtforms.validators import DataRequired

class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField('Content',)
    month = MonthField("Month")
    
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])