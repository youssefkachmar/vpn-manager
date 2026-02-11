import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'vpn_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # WireGuard settings - Endpoint set at runtime
    # Priority: 1) PUBLIC_IP environment variable, 2) Auto-detect via get_public_ip()
    WG_SERVER_ENDPOINT = None  # Will be set dynamically in app initialization
    WG_SERVER_PORT = 51820
    
    # Directories
    CONFIG_DIR = os.path.join(BASE_DIR, 'configs')
    QRCODE_DIR = os.path.join(BASE_DIR, 'qrcodes')  # Use local dir for easier access
    
    # HTTPS Settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Monitoring and Alerts
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    TRAFFIC_ALERT_DOWNLOAD_GB = int(os.getenv('TRAFFIC_ALERT_DOWNLOAD_GB', 10))
    TRAFFIC_ALERT_UPLOAD_GB = int(os.getenv('TRAFFIC_ALERT_UPLOAD_GB', 5))
