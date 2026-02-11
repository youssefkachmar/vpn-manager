from flask import Flask
from flask_login import LoginManager
from config import Config

# Import db from models.user (single source of truth)
from app.models.user import db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set WireGuard endpoint dynamically using public IP detection
    from app.utils.network import get_public_ip
    import os
    
    # Try to get from env first, then auto-detect
    public_ip = os.getenv('PUBLIC_IP') or get_public_ip()
    if public_ip:
        app.config['WG_SERVER_ENDPOINT'] = f"{public_ip}:{app.config['WG_SERVER_PORT']}"
        print(f"WireGuard endpoint set to: {app.config['WG_SERVER_ENDPOINT']}")
    else:
        app.config['WG_SERVER_ENDPOINT'] = f"your-server-ip:{app.config['WG_SERVER_PORT']}"
        print("Warning: Could not detect public IP, using placeholder")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize SocketIO
    from app.routes.websocket import socketio
    socketio.init_app(app, async_mode='threading')
    
    # Import models AFTER db is initialized
    from app.models.user import User
    from app.models.peer import Peer
    from app.models.bandwidth import BandwidthHistory
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        try:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@vpnmanager.local',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created (username: admin, password: admin123)")
            else:
                print(f"Admin user already exists: {admin.username}")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()
        
        # Start bandwidth monitoring scheduler
        from app.utils.monitor import start_bandwidth_monitor
        start_bandwidth_monitor(app)
    
    return app, socketio
