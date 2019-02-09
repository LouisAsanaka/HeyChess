import random
import string

from flask_socketio import join_room, leave_room
import chess

from . import socketio

class Game:

    GAME_ID_EMPTY = "NULL"

    SLOT_WHITE = 0
    SLOT_BLACK = 1

    def __init__(self):
        self.game_id: str = Game.generate_room_id()
        self.board = chess.Board()
        self.is_playing = False
        self.participants = [None, None] 
        self.name_to_slot = {}

    @classmethod
    def generate_room_id(cls) -> str:
        """Generate a random room ID"""
        id_length = 8
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase) for _ in range(id_length))

    def get_game_id(self) -> str:
        return self.game_id

    def set_participant(self, slot, player):
        self.participants[slot] = player
        self.name_to_slot[player.get_username()] = slot
        player.set_game_id(self.game_id)
        join_room(room=self.game_id, sid=player.get_sid())

    def remove_participant_by_slot(self, slot):
        player = self.participants[slot]
        self.participants[slot] = None
        self.name_to_slot.pop(player.get_username(), None)
        player.set_game_id(Game.GAME_ID_EMPTY)
        leave_room(room=self.game_id, sid=player.get_sid())

    def remove_participant_by_name(self, name):
        slot = self.name_to_slot.pop(name, None)
        if slot is not None:
            player = self.participants[slot]
            self.participants[slot] = None

            player.set_game_id(Game.GAME_ID_EMPTY)
            leave_room(room=self.game_id, sid=player.get_sid())

    def get_participant_by_slot(self, slot):
        return self.participants[slot]

    def get_participant_by_name(self, name):
        slot = self.name_to_slot.get(name, None)
        if slot is not None:
            return self.participants[slot]
        return None

    def get_participant_slot(self, name):
        return self.name_to_slot.get(name, None)

    def get_slot_turn(self):
        return Game.SLOT_WHITE if self.board.turn is chess.WHITE else Game.SLOT_BLACK
    
    def get_participants(self):
        return self.participants

    def emit(self, event, *args, **kwargs):
        socketio.emit(event, *args, room=self.game_id, **kwargs)

    def play_move(self, name, move_cfg, check_game_end=True):
        if not self.is_playing:
            raise RuntimeWarning("Game is not in progress!")
        _from = move_cfg.get("from", None)
        to = move_cfg.get("to", None)
        if _from is None or to is None:
            return
        promotion = move_cfg.get("promotion", "")
        if not promotion and promotion not in "nbrq":
            return
        slot = self.get_participant_slot(name)
        if slot is None:
            return
        elif slot is not self.get_slot_turn():
            print("Cheater!")
            return
        move = chess.Move.from_uci(_from + to + promotion)
        if move not in self.board.legal_moves:
            return
        self.board.push(move)

        opponent = self.get_participant_by_slot(self.get_slot_turn())
        opponent.emit("move_played", move_cfg)

        if check_game_end and self.board.is_game_over(claim_draw=False):
            result = self.board.result(claim_draw=False)
            self.end(result)

    def start(self):
        self.emit("game_start", self.name_to_slot)
        self.is_playing = True

    def end(self, result):
        self.emit("game_end", result)
        self.is_playing = False
