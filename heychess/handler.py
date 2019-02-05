from flask_socketio import SocketIO, emit
from flask import (
    request
)
from coolname import generate_slug
import json
from . import socketio
from .playerlist import PlayerList
from .player import Player
   
# List of online players
player_list = PlayerList()

@socketio.on('connect')
def on_connect():
    # Generate a random username
    username: str = generate_slug(2)
    # Create a Player object and add it to the list of players
    player: Player = player_list.add_player(Player(request.sid, username))
    # Send the randomly-generated username to the player
    player.emit('set_username', username)
    # Update everyone's player list
    socketio.emit('player_list', {
        'playerList': json.dumps(player_list.as_list())
    }, namespace="/")
    
    print(f'Client {username}[{request.sid}] has connected!')

@socketio.on('disconnect')
def on_disconnect():
    # Remove the player from the online players list
    player = player_list.get_player_by_sid(request.sid)
    player_list.remove_player_by_sid(request.sid)
    # Update everyone's player list
    socketio.emit('player_list', {
        'playerList': json.dumps(player_list.as_list())
    }, namespace="/")

    print(f'Client {str(player)}[{request.sid}] has disconnected!')

