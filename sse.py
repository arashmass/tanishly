from flask import Flask, render_template, flash, request, url_for, redirect, session, abort
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_socketio import SocketIO, join_room, leave_room
from flask_sse import sse
import random


app = Flask(__name__)
app.config["REDIS_URL"] = 'redis://localhost:6379'
app.register_blueprint(sse, url_prefix='/stream')

socketio = SocketIO(app)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

class User(UserMixin):

    def __init__(self, id,name, password):
        self.id = id
        self.name = name
        self.password = password


user_names = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login' , methods = ['POST','GET'])
def login():
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        if name in user_names: # TODO: query in db
            if not password == password:
                flash("error", "password missmatch, 401")
                session['username'] = name
            else:
                return redirect(url_for('index'))
        else: 
            user_names.append(name)
            # login_user(user)
            flash("info", "user created")
    return render_template("login.html")


@app.route('/contact' , methods = ['POST'])
def contact():
    if not session['username']:
        abort(401)
    if request.method == "POST":
        name = request.form['username']
        if name in user_names:
            sse.publish({"message" : "{}".format(name)}, type='new_contact')
            # return "{} added to your contact.".format(name)
        else:
            sse.publish({"message" : "no such user singed! : {}".format(name)}, type='new_contact')
    return render_template("contact.html")

@app.route('/contact/approve/<username>')
def approve_contact(username):
    if not session['username']:
        abort(401)
    # TODO: add contact session[] to username
    pass

rooms = []

# Socket io Enabled
@app.route('/new_room/<name>')
def new_room(name):
    if not session['username']:
        abort(401)
    # if name is in sessions contacts
    # sse to name and retrive sdp
    sse.publish({"message": "new room created : {}".format(name), "user":session['username']}, type='new_room', channel=name)
    rooms.append(name)
    return "new room created : {}".format(name)

@app.route('/join_room/<party>', methods=['GET'])
def join_first(party):
    pass
@app.route('/join_room/<party>', methods=['POST'])
def join_second():
    if not session['username']:
        abort(401)
    pass

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

# @app.route('/add_to_room/<room>/<user>')
# def add_to_room(room, user):
#     if room in rooms:
#         sse.publish({"message": "new user {} added to room:{}".format(user, room)}, type='new_user')

#     return "user {} added to room : {}".format(user, room)

