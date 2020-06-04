from app import current_app

@current_app.route('/')
@current_app.route('/index')
def new():
    return "Hello, World!"