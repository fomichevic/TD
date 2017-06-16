from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

room = {}
coroutine= {}
clients = defaultdict(list)
wait_room = None


@app.route('/')
def chat():
    return render_template('chat.html', async_mode=socketio.async_mode)

def stop(room_id):
    print('killlllllllllllllllll')
    eventlet.kill(coroutine[room_id])

def serve(room_id):
    while True:
        socketio.emit('message', {'data':'123'}, room=room_id)
        eventlet.sleep(3)
        if 3<4: #term when game ends
            stop(room_id)
            break
        
@socketio.on('message')
def message(msg):
    uid = request.sid;
    print('client {} send the message "{}"'.format(uid, msg['data']))
    emit('message', {'data': msg['data']}, room = room[uid])

@socketio.on('connect')
def enter():
    global wait_room

    if not wait_room:
        room_id = uuid().hex
        wait_room = room_id
    else:
        room_id = wait_room
        wait_room = None
        emit('message', {'data': 'urra'}, room=room_id)

    uid = request.sid;
    join_room(room_id)
    room[uid] = room_id
    clients[room_id].append(uid)
    
    if wait_room:
        eid = eventlet.spawn(serve, room_id)
        coroutine[room_id] = eid
    print('client {} connected'.format(uid))

@socketio.on('disconnect')
def leave():
    global wait_room

    uid = request.sid
    room_id = room[uid]

    leave_room(room_id)
    clients[room_id].remove(uid)
    del room[uid]

    if not wait_room:
        wait_room = room_id
        return

    if wait_room != room_id:
        other = clients[room_id][0]
        join_room(wait_room, other)
        del clients[room_id]

    close_room(room_id)
    wait_room = None
    print('client {} disconnected'.format(uid))
 

if __name__ == '__main__':
    socketio.run(app, debug=True)
