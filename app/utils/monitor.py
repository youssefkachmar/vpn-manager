from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit

# Global scheduler instance
scheduler = BackgroundScheduler()
scheduler_started = False

def collect_bandwidth_stats():
    """Collect and store bandwidth stats every 5 minutes"""
    from flask import current_app
    from app.models.bandwidth import BandwidthHistory
    from app.models.peer import Peer
    from app.models.user import db
    from app.utils.wireguard import WireGuardManager
    from app.utils.alerts import check_unusual_traffic, send_webhook_alert
    
    # Must run within app context
    with current_app.app_context():
        try:
            wg_manager = WireGuardManager()
            stats = wg_manager.get_peer_stats()
            
            # Get all peers
            peers = Peer.query.all()
            
            for peer in peers:
                if peer.public_key in stats:
                    peer_stats = stats[peer.public_key]
                    
                    # Store bandwidth history
                    history = BandwidthHistory(
                        peer_id=peer.id,
                        timestamp=datetime.utcnow(),
                        rx_bytes=peer_stats['rx_bytes'],
                        tx_bytes=peer_stats['tx_bytes']
                    )
                    db.session.add(history)
                    
                    # Check for unusual traffic
                    alert = check_unusual_traffic(peer, peer_stats)
                    if alert:
                        send_webhook_alert(alert)
            
            db.session.commit()
            print(f"Bandwidth stats collected at {datetime.utcnow()}")
        
        except Exception as e:
            print(f"Error collecting bandwidth stats: {e}")
            db.session.rollback()

def start_bandwidth_monitor(app):
    """Initialize and start the bandwidth monitoring scheduler"""
    global scheduler_started
    
    if scheduler_started:
        return
    
    # Add job to collect bandwidth stats every 5 minutes
    scheduler.add_job(
        func=lambda: collect_bandwidth_stats(),
        trigger='interval',
        minutes=5,
        id='bandwidth_collector',
        name='Collect bandwidth statistics',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    scheduler_started = True
    
    print("Bandwidth monitoring scheduler started (5-minute intervals)")
    
    # Shutdown the scheduler when the app exits
    atexit.register(lambda: scheduler.shutdown())

def format_bytes(bytes_value):
    """Format bytes as human-readable string"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    elif bytes_value < 1024 ** 4:
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_value / (1024 ** 4):.2f} TB"
