from crypt import methods
import os
from flask import Flask, render_template, request, send_from_directory, url_for
from flask_ckeditor import CKEditor, upload_success, upload_fail
from flask_wtf.csrf import CSRFProtect
from Forms import CreatePostForm, LoginForm

app = Flask(__name__, )

ckeditor = CKEditor(app)

app.config['SECRET_KEY'] = "VERY SECRET"
app.config['CKEDITOR_FILE_UPLOADER'] = "upload"
app.config['CKEDITOR_ENABLE_CSRF'] = True

csrf = CSRFProtect(app)

@app.route("/")
def index():
    return render_template("screens/index.html")

@app.route("/posts/<postId>")
def posts(postId):
    print(postId)
    return render_template("screens/post.html")

@app.route("/categories")
def categories():
    return render_template("screens/category.html")

@app.route("/tags")
def tags():
    return render_template("screens/tag.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    else:
        form = LoginForm()
        return render_template("screens/login.html", form=form)

@app.route("/input",methods=["GET", "POST"])
def input():
    if request.method == "POST":
        data = request.form.get('content')
        print(data)
    form = CreatePostForm()
    return render_template("input.html",form=form)

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

if __name__ == "__main__":
    app.run(debug=True)