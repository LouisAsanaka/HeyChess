from . import socketio

class Player:
    
    def __init__(self, sid, username):
        self.sid = sid
        self.username = username

    def set_sid(self, sid):
        self.sid = sid

    def get_sid(self):
        return self.sid

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def emit(self, event, *args, **kwargs):
        socketio.emit(event, *args, room=self.sid, **kwargs)

    def __str__(self):
        return f"{self.username}[{self.sid}]"
