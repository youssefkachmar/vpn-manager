import os

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'vpn_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for sessions
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # WireGuard settings
    WG_SERVER_ENDPOINT = 'your-domain.com:51820'  # Or your public IP 
    SECRET_KEY = 'your-secret-key'
    
    # Directories
    CONFIG_DIR = os.path.join(BASE_DIR, 'configs')
    QRCODE_DIR = '/var/www/vpn-qrcodes'
    
    # HTTPS Settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
