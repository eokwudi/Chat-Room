import os
import requests
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "aldsjflsdlsflkdsfa"
socketio = SocketIO(app)

# Going to be used to hold certain aspects of user information and
# chat rooms
rooms = []
users = {}
identity = []
direct = ""
name = " "

# Entering chat room with a name. For the sake of this project, registration
# was not necessary. Can test with any name
# Another important point is that if you want to use two people at once, then
# enter one room using one name and add a couple comments, then
# open a new tab, use a new username, and enter the chat room to see
# previous messages

@app.route("/", methods=['GET','POST'])
def index():
    if request.method == "POST":
        name = request.form['username']
        session['username'] = name
        identity.append(name)
        session.permanent = True
        return render_template("welcome.html", title=name)
    name = session.get('username')
    session.permanent = True
    return render_template("welcome.html", title=name)

# JavaScript looks to process pages in full whenever the route is called
# For this reason, pages with forms will automatically return errors
# because the form tried to process with no data, for this reason
# intermediates are used in conjunction with JavaScript clicks to load
# pages with forms
@app.route("/transfer")
def transfer():
    return render_template("fill.html")


@app.route("/proxy")
def proxy():
    return render_template("people.html")

# Creates room name , stores room name, and enters user into room
@app.route("/fill", methods=['GET','POST'])
def fill():
    name = ""
    value = ""
    if request.method == "POST":
        name = request.form['chat']
        session['room'] = name
        rooms.append(session.get('room'))
        value = session.get('room')
    return redirect(url_for('sess', space=value))

# Creates room for communication for just two people
@app.route("/people", methods=['GET', 'POST'])
def people():
    if request.method == "POST":
        id = request.form['person']
        if id in identity:
            return redirect(url_for('current', space=id))
    return render_template("people.html")

# Names of rooms
@app.route("/list")
def list():
    return render_template("list.html", rooms=rooms)

# Sending and receiving messages in chat room
@app.route("/session/<space>", methods=['GET', 'POST'])
def sess(space):
    return render_template("session.html", space=space)

@socketio.on("my event")
def handle_comm(comment, methods = ['GET', 'POST']):
    room = session.get('room')
    emit("my response", {'text': session.get('username') + ':' + comment['msg']}, room=room)

@socketio.on('entered')
def enter(data):
    room = session.get('room')
    join_room(room)
    emit('status', {'text': session.get('username') + ' has entered the room.'}, room=room)

@socketio.on('left')
def leave(data):
    room = session.get('room')
    leave_room(room)
    emit('status', {'text': session.get('username') + ' has left the room.'}, room=room)

# Sending and receiving messages in private chat room
@app.route("/private/<space>", methods=["GET", "POST"])
def current(space):
    return render_template("private.html", space = space)

@socketio.on('entered', namespace='/private')
def enter(data):
    users[direct] = request.sid
    room = users.get(direct)
    join_room(room)
    emit('status', {'text': session.get('username') + 'has entered the room.'}, room=room)

@socketio.on('my message', namespace='/private')
def comment(data, methods=['GET', 'POST']):
    #users[direct] = request.sid
    room = users.get(direct)
    emit("my response", {'text': session.get('username') + ':' + data['msg']}, room=room)

@socketio.on('left', namespace='/private')
def leave(data):
    #users[direct] = request.sid
    room = users.get(direct)
    leave_room(room)
    emeit('status', {'text': session.get('username') + 'has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug='True')
