from flask_socketio import SocketIO, emit
from flask import (
    request
)
from coolname import generate_slug
import json
import random
import string

from . import socketio
from .playerlist import PlayerList
from .player import Player
from .gamelist import GameList
from .game import Game
   
# List of online players
player_list = PlayerList()

# List of on-going games
game_list = GameList()

# List of pending challenges
challenges = {}

def generate_challenge_id() -> str:
    """Generate a random ID"""
    id_length = 8
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase) for _ in range(id_length))

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
    player: Player = player_list.remove_player_by_sid(request.sid)
    # Update everyone's player list
    socketio.emit('player_list', {
        'playerList': json.dumps(player_list.as_list())
    }, namespace="/")
    # Delete pending challenges
    for opponent, challenge_id in player.sent_challenges.items():
        challenges.pop(challenge_id, None)
        opponent = player_list.get_player_by_name(opponent)
        if opponent is not None:
            del opponent.received_challenges[player.get_username()]

    for challenger, challenge_id in player.received_challenges.items():
        challenges.pop(challenge_id, None)
        challenger = player_list.get_player_by_name(challenger)
        if challenger is not None:
            del challenger.sent_challenges[player.get_username()]
    # End the game the player is in
    game = game_list.get_game(player.get_game_id())
    if game is not None:
        if game.get_participant_slot(player.get_username()) == Game.SLOT_WHITE:
            result = "0-1"
        else:
            result = "1-0"
        game.end(result)
        
        game_list.remove_game(game.get_game_id(), cleanup=True)
    print(f'Client {str(player)}[{request.sid}] has disconnected!')

@socketio.on('challenge')
def on_challenge(data):
    player = player_list.get_player_by_sid(request.sid)
    if player is None:
        return
    elif player.get_game_id() is not Game.GAME_ID_EMPTY:
        player.emit("request_status", {
            "type": "error",
            "message": "You are already in a game!"
        })
        return
    opponent = data.get('opponent', None)
    if opponent is None: # Wrongly formatted payload
        player.emit("request_status", {
            "type": "error",
            "message": "Wrongly formatted payload."
        })
        return
    elif player.get_username() == opponent: # The opponent is the same as the challenger
        player.emit("request_status", {
            "type": "error",
            "message": "You can't challenge yourself!"
        })
        return
    elif player.sent_challenges.get(opponent, None) is not None:
        player.emit("request_status", {
            "type": "error",
            "message": "You've already challenged this player."
        })
        return
    opponent_object = player_list.get_player_by_name(opponent)
    if opponent_object is None: # Opponent doesn't exist!
        player.emit("request_status", {
            "type": "error",
            "message": "Your opponent isn't online anymore."
        })
        return
    elif opponent_object.get_game_id() is not Game.GAME_ID_EMPTY:
        player.emit("request_status", {
            "type": "error",
            "message": "Your opponent is in a game!"
        })
        return
    # Add challenge to the list of pending challenges
    challenge_id = generate_challenge_id()
    challenges[challenge_id] = {
        'challenger': player.get_username(),
        'opponent': opponent
    }
    player.sent_challenges[opponent] = challenge_id
    opponent_object.received_challenges[player.get_username()] = challenge_id

    # Send the challenge!
    opponent_object.emit('receive_challenge', {
        'challenge_id': challenge_id,
        'challenger': player.get_username()
    })
    player.emit("request_status", {
        "type": "success",
        "message": "Challenging " + opponent + "..."
    })

@socketio.on('accept_challenge')
def on_accept_challenge(data):
    player = player_list.get_player_by_sid(request.sid)
    if player is None:
        return
    challenge_id = data.get('challenge_id', None)
    if challenge_id is None: # Wrongly formatted payload
        player.emit("request_status", {
            "type": "error",
            "message": "Wrongly formatted payload."
        })
        return
    challenge = challenges.get(challenge_id, None)
    if challenge is None: # Invalid challenge id!
        player.emit("request_status", {
            "type": "error",
            "message": "Invalid challenge!"
        })
        return
    elif challenge.get('opponent', None) != player.get_username(): # The acceptor is not the challenged opponent!
        player.emit("request_status", {
            "type": "error",
            "message": "Invalid payload."
        })
        return
    challenger = challenge.get('challenger', None)
    challenger_object = player_list.get_player_by_name(challenger)
    if challenger_object is None: # Challenger doesn't exist!
        player.emit("request_status", {
            "type": "error",
            "message": "The challenger is no longer online."
        })
        return
    # Delete the challenge!
    del challenges[challenge_id]
    for opponent, challenge_id in player.sent_challenges.items():
        challenges.pop(challenge_id, None)
        opponent = player_list.get_player_by_name(opponent)
        if opponent is not None:
            del opponent.received_challenges[player.get_username()]

    for _challenger, challenge_id in player.received_challenges.items():
        challenges.pop(challenge_id, None)
        _challenger = player_list.get_player_by_name(_challenger)
        if _challenger is not None:
            del _challenger.sent_challenges[player.get_username()]
    # Create the game!
    game = Game()
    color = random.randint(Game.SLOT_WHITE, Game.SLOT_BLACK)
    game.set_participant(color, challenger_object)
    game.set_participant(1 - color, player)
    game.start()

    game_list.add_game(game)
    player.emit("request_status", {
        "type": "success",
        "message": "Accepted challenge from " + challenger + "!"
    })

@socketio.on('play_move')
def on_play_move(data):
    player = player_list.get_player_by_sid(request.sid)
    if player is None:
        return
    game_id = player.get_game_id()
    if game_id == Game.GAME_ID_EMPTY:
        return
    game = game_list.get_game(game_id)
    if game is None:
        return
    elif not game.is_playing:
        return
    game.play_move(player.get_username(), data)

    if not game.is_playing: # Game ended!
        game_list.remove_game(game.get_game_id(), cleanup=True)
        print("Game ended!")
