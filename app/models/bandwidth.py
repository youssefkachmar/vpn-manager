from datetime import datetime
from app.models.user import db

class BandwidthHistory(db.Model):
    __tablename__ = 'bandwidth_history'
    
    id = db.Column(db.Integer, primary_key=True)
    peer_id = db.Column(db.Integer, db.ForeignKey('peers.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    rx_bytes = db.Column(db.BigInteger, default=0)
    tx_bytes = db.Column(db.BigInteger, default=0)
    
    # Relationship to peer
    peer = db.relationship('Peer', backref=db.backref('bandwidth_history', lazy='dynamic'))
    
    def __repr__(self):
        return f'<BandwidthHistory peer_id={self.peer_id} timestamp={self.timestamp}>'
