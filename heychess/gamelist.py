from typing import Optional

from .game import Game

class GameList:

    def __init__(self):
        self._games = {}

    def add_game(self, game: Game):
        self._games[game.get_game_id()] = game

    def remove_game(self, game_id: str, cleanup=True):
        game = self._games.pop(game_id, None)
        if cleanup and game is not None:
            game.remove_participant_by_slot(Game.SLOT_WHITE)
            game.remove_participant_by_slot(Game.SLOT_BLACK)

    def get_game(self, game_id: str) -> Optional[Game]:
        return self._games.get(game_id, None)

    def get_game_count(self) -> int:
        return len(self._games)