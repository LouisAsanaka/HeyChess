from typing import Optional

from .player import Player

class PlayerList:

    def __init__(self):
        self._players = {}
        self._name_to_sid = {}

    """Add a Player to the PlayerList"""
    def add_player(self, player: Player) -> Player:
        sid = player.get_sid()
        self._players[sid] = player
        self._name_to_sid[player.get_username()] = sid
        return player

    """Remove a player from the PlayerList by their sid"""
    def remove_player_by_sid(self, sid: str) -> Optional[Player]:
        player: Player = self._players.pop(sid, None)
        if player is not None:
            self._name_to_sid.pop(player.get_username())
        return player   

    """Remove a player from the PlayerList by their username"""
    def remove_player_by_name(self, username: str) -> Optional[Player]:
        sid: str = self._name_to_sid.pop(username, None)
        if sid is not None:
            return self._players.pop(sid, None)
        return None

    """Retrieve a Player instance by sid"""
    def get_player_by_sid(self, sid: str) -> Optional[Player]:
        return self._players.get(sid, None)

    """Retrieve a Player instance by username"""
    def get_player_by_name(self, username: str) -> Optional[Player]:
        return self._players.get(self._name_to_sid.get(username, None), None)

    """Return a list of player names"""
    def as_list(self) -> list:
        return list(self._name_to_sid.keys())
    