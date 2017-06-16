import eventlet
from flask import Flask
from flask_socketio import SocketIO

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

if __name__ == '__main__':
    socketio.run(app, debug=True)
