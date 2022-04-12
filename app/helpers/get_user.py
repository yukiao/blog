from flask import session
def get_user():
    user = None
    if '_id' in session:
        user = session.get('_id')
    
    return user