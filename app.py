from app import create_app

app, socketio = create_app()

@app.shell_context_processor
def make_shell_context():
    from app.models.user import db
    from app.models.peer import Peer
    from app.models.user import User
    return {'db': db, 'Peer': Peer, 'User': User}

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

