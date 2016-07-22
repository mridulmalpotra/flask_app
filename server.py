"""
Sample program for Flask basics.
Check README.md for more info.
"""

from flask import Flask, render_template, request, redirect, session, flash
from flask_admin import Admin
from dataset import connect

DB_NAME = "contacts.db"
TABLE_NAME = "flask"
DEBUG_LEVEL = False

# Flask global variables
FLASK_APP = Flask(__name__)
FLASK_ADMIN = Admin(FLASK_APP, name='Admin panel')

FLASK_APP.config.update(dict(
    DEBUG=DEBUG_LEVEL,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='pass'
))


def get_user_data(name, primary_id=True, email=True, team=True, mobile=True):
    """
    Gets individual user data.
    """
    flask_db = connect("sqlite:///"+DB_NAME)
    table = flask_db[TABLE_NAME]
    data_list = {}
    for user in table:
        if user['name'] == name:
            # print user['name'], user['team'], user['email'], user['mobile'],
            if primary_id:
                data_list['id'] = user['id']
            if name:
                data_list['name'] = user['name']
            if email:
                data_list['email'] = user['email']
            if team:
                data_list['team'] = user['team']
            if mobile:
                data_list['mobile'] = user['mobile']
            break
    return data_list


def get_data(primary_id=True, name=False, email=False, team=False, mobile=False):
    """
    Gets all user data based on parameters given.
    """
    flask_db = connect("sqlite:///"+DB_NAME)
    table = flask_db[TABLE_NAME]
    data_list = []
    for user in table:
        # print user['name'], user['team'], user['email'], user['mobile'],
        temp_list = {}
        if primary_id:
            temp_list['id'] = user['id']
        if name:
            temp_list['name'] = user['name']
        if email:
            temp_list['email'] = user['email']
        if team:
            temp_list['team'] = user['team']
        if mobile:
            temp_list['mobile'] = user['mobile']
        data_list += [temp_list]
    return data_list


def add_user_entry(data):
    """
    Adds a new user to database.
    """
    print data
    if len(data['mobile']) != 10:
        return "Mobile number is not correct!"
    flask_db = connect("sqlite:///"+DB_NAME)
    table = flask_db[TABLE_NAME]
    for user in table:
        if data['name'] == user['name']:
            return "User name already exists!"
    primary_id = table.insert(dict(name=data['name'], team=data['team'], \
    mobile=data['mobile'], email=data['email']))
    print "\n\nPrimary key after insertion:", primary_id
    return None


def del_user_entries(names):
    """
    Deletes a user from table.
    """
    flask_db = connect("sqlite:///"+DB_NAME)
    table = flask_db[TABLE_NAME]
    deleted_flag = False
    for user in table:
        if user['name'] in names:
            deleted_flag = table.delete(name=user['name'])
    if not deleted_flag:
        return "Deletion not completely successful!"
    return None


# Routing Functions
@FLASK_APP.route('/')
def index():
    """
    Function to control home page.
    """
    if session:
        return redirect('/list')
    else:
        return redirect('/login')


LIST_ERROR = None
@FLASK_APP.route('/list', methods=['GET', 'POST'])
def list_all():
    """
    Function to control list page.
    """
    global LIST_ERROR
    if request.method == 'GET':
        user_list = get_data(name=True, mobile=True)
        print user_list
        error = LIST_ERROR
        LIST_ERROR = None
        return render_template('list.html', user_list=user_list, error=error)
    elif request.method == 'POST':
        LIST_ERROR = None
        names = []
        for value in request.form:
            if "check_User " in value:
                names += [value[6:]]
        if not names:
            LIST_ERROR = "No entry selected!"
            return redirect('/list')
        LIST_ERROR = del_user_entries(names)
        return redirect('/list')


@FLASK_APP.route('/user/<string:user_name>')
def list_user(user_name):
    """
    Function to control user page.
    """
    print "Fetching data for user", user_name
    user_data = get_user_data(name=user_name)
    print user_data
    return render_template('user.html', user_data=user_data)


REGISTER_ERROR = None
@FLASK_APP.route('/register', methods=['GET', 'POST'])
def register_user():
    """
    Function to control register page.
    """
    global REGISTER_ERROR
    if request.method == 'GET':
        error = REGISTER_ERROR
        REGISTER_ERROR = None
        return render_template('register.html', error=error)
    elif request.method == 'POST':
        REGISTER_ERROR = None
        received_data = {}
        received_data['name'] = request.form['name']
        received_data['email'] = request.form['email']
        received_data['mobile'] = request.form['mobile']
        received_data['team'] = request.form['team']

        print "\n\nReceived data:", received_data

        REGISTER_ERROR = add_user_entry(received_data)
        if not REGISTER_ERROR:
            return redirect('/list')
        else:
            return redirect('/register')


@FLASK_APP.route('/login', methods=['GET', 'POST'])
def login():
    """
    Function to control login page.
    """
    error = None
    if request.method == 'POST':
        if request.form['username'] != FLASK_APP.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != FLASK_APP.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect('/list')
    return render_template('login.html', error=error)


@FLASK_APP.route('/logout')
def logout():
    """
    Function to control logout page.
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('/login')


if __name__ == "__main__":
    FLASK_APP.run(host='127.0.0.1', port=5000, debug=DEBUG_LEVEL)
