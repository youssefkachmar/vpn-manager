from app import create_app, db
from app.models.peer import Peer
from app.models.user import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Peer': Peer, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)
