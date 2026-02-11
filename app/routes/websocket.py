from flask import Blueprint
from flask_socketio import SocketIO, emit
from flask_login import current_user
from app.utils.wireguard import WireGuardManager
from app.models.peer import Peer
from app.utils.monitor import format_bytes

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if not current_user.is_authenticated:
        return False
    print(f'Client connected: {current_user.username}')
    emit('connected', {'message': 'Connected to VPN Manager'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        print(f'Client disconnected: {current_user.username}')

@socketio.on('request_stats')
def handle_stats_request():
    """Handle real-time stats request"""
    if not current_user.is_authenticated:
        return False
    
    try:
        wg_manager = WireGuardManager()
        stats = wg_manager.get_peer_stats()
        
        # Get all peers
        peers = Peer.query.all()
        
        # Build response with peer stats
        peer_stats = {}
        for peer in peers:
            if peer.public_key in stats:
                peer_stat = stats[peer.public_key]
                peer_stats[peer.id] = {
                    'id': peer.id,
                    'name': peer.name,
                    'ip_address': peer.ip_address,
                    'online': peer_stat['online'],
                    'rx_bytes': peer_stat['rx_bytes'],
                    'tx_bytes': peer_stat['tx_bytes'],
                    'rx_formatted': format_bytes(peer_stat['rx_bytes']),
                    'tx_formatted': format_bytes(peer_stat['tx_bytes']),
                    'endpoint': peer_stat['endpoint'],
                    'latest_handshake': peer_stat['latest_handshake']
                }
            else:
                peer_stats[peer.id] = {
                    'id': peer.id,
                    'name': peer.name,
                    'ip_address': peer.ip_address,
                    'online': False,
                    'rx_bytes': 0,
                    'tx_bytes': 0,
                    'rx_formatted': '0 B',
                    'tx_formatted': '0 B',
                    'endpoint': None,
                    'latest_handshake': 0
                }
        
        emit('peer_stats', peer_stats)
    
    except Exception as e:
        print(f"Error getting peer stats: {e}")
        emit('error', {'message': 'Failed to get peer stats'})
