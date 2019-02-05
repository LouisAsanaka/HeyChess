from heychess import create_app, socketio

app = create_app(test_config=None)

if __name__ == '__main__':
    socketio.run(app)