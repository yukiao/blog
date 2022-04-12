import functools
from flask import session, redirect, url_for, request

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "_id" not in session:
            return redirect(url_for("login", next_path=[request.full_path]))
        return func(*args, **kwargs)
    
    return secure_function