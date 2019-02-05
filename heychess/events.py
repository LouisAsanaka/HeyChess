from flask_socketio import SocketIO, emit
from flask import (
    request
)
from . import socketio


@socketio.on('connect')
def on_connect():
    print(f'Client {request.sid} connected!')

@socketio.on('disconnect')
def on_disconnect():
    print(f'Client {request.sid} disconnected!')
