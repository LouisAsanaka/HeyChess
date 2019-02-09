from . import socketio
from .game import Game

class Player:
    
    def __init__(self, sid, username):
        self.sid = sid
        self.username = username
        self.game_id = Game.GAME_ID_EMPTY
        
        self.sent_challenges = {}
        self.received_challenges = {}

    def set_sid(self, sid):
        self.sid = sid

    def get_sid(self):
        return self.sid

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_game_id(self, game_id: str):
        self.game_id = game_id

    def get_game_id(self) -> str:
        return self.game_id

    def emit(self, event, *args, **kwargs):
        socketio.emit(event, *args, room=self.sid, **kwargs)

    def __str__(self):
        return f"{self.username}[{self.sid}]"
