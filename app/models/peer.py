from datetime import datetime
from app.models.user import db

class Peer(db.Model):
    __tablename__ = 'peers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    public_key = db.Column(db.String(200), nullable=False, unique=True)
    private_key = db.Column(db.String(200), nullable=False)
    preshared_key = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW FIELDS - Add these
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    total_rx = db.Column(db.BigInteger, default=0)  # Bytes received
    total_tx = db.Column(db.BigInteger, default=0)  # Bytes transmitted

    def __repr__(self):
        return f'<Peer {self.name} - {self.ip_address}>'
