import requests
import os
from datetime import datetime, timedelta

# Cache for public IP
_ip_cache = {
    'ip': None,
    'timestamp': None,
    'ttl': 3600  # Cache for 1 hour
}

def get_public_ip():
    """Fetch public IP from ipify API with caching and fallback"""
    global _ip_cache
    
    # Check cache first
    if _ip_cache['ip'] and _ip_cache['timestamp']:
        age = (datetime.now() - _ip_cache['timestamp']).total_seconds()
        if age < _ip_cache['ttl']:
            return _ip_cache['ip']
    
    # Try to fetch from API
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            # Update cache
            _ip_cache['ip'] = ip
            _ip_cache['timestamp'] = datetime.now()
            return ip
    except Exception as e:
        print(f"Failed to fetch public IP from API: {e}")
    
    # Fallback to cached IP if available
    if _ip_cache['ip']:
        print("Using cached IP (API unavailable)")
        return _ip_cache['ip']
    
    # Final fallback to environment variable or None
    return os.getenv('PUBLIC_IP', None)
