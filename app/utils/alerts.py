import requests
from datetime import datetime, timedelta
from flask import current_app

def check_unusual_traffic(peer, current_stats):
    """Check if peer has unusual traffic patterns"""
    from app.models.bandwidth import BandwidthHistory
    from app.models.user import db
    
    # Get bandwidth history for the last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_history = BandwidthHistory.query.filter(
        BandwidthHistory.peer_id == peer.id,
        BandwidthHistory.timestamp >= one_hour_ago
    ).order_by(BandwidthHistory.timestamp.asc()).all()
    
    if not recent_history:
        return None
    
    # Calculate traffic in the last hour
    first_record = recent_history[0]
    current_rx = current_stats.get('rx_bytes', 0)
    current_tx = current_stats.get('tx_bytes', 0)
    
    # Calculate delta (bytes transferred in the last hour)
    rx_delta = max(0, current_rx - first_record.rx_bytes)
    tx_delta = max(0, current_tx - first_record.tx_bytes)
    
    # Convert to GB
    rx_gb = rx_delta / (1024 ** 3)
    tx_gb = tx_delta / (1024 ** 3)
    
    # Get thresholds from config
    download_threshold = current_app.config.get('TRAFFIC_ALERT_DOWNLOAD_GB', 10)
    upload_threshold = current_app.config.get('TRAFFIC_ALERT_UPLOAD_GB', 5)
    
    # Check if thresholds exceeded
    alert = None
    if rx_gb > download_threshold:
        alert = {
            'event': 'unusual_traffic',
            'peer_name': peer.name,
            'peer_ip': peer.ip_address,
            'details': f'Downloaded {rx_gb:.2f}GB in the last hour',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'severity': 'warning',
            'rx_bytes': int(rx_delta),
            'tx_bytes': int(tx_delta)
        }
    elif tx_gb > upload_threshold:
        alert = {
            'event': 'unusual_traffic',
            'peer_name': peer.name,
            'peer_ip': peer.ip_address,
            'details': f'Uploaded {tx_gb:.2f}GB in the last hour',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'severity': 'warning',
            'rx_bytes': int(rx_delta),
            'tx_bytes': int(tx_delta)
        }
    
    return alert

def send_webhook_alert(payload):
    """Send alert to configured webhook"""
    webhook_url = current_app.config.get('WEBHOOK_URL')
    if not webhook_url:
        return False
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print(f"Alert sent successfully: {payload['details']}")
            return True
        else:
            print(f"Failed to send alert: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to send webhook: {e}")
        return False
