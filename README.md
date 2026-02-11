# WireGuard VPN Manager 🔐

A web-based management interface for a WireGuard VPN server with QR code provisioning for easy mobile setup.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![WireGuard](https://img.shields.io/badge/WireGuard-enabled-green.svg)

## Features

- 🌐 Web-based GUI for VPN management
- 📱 QR code generation for one-tap mobile configuration
- 👥 Multi-peer support with automatic IP allocation
- 🔄 Enable/disable peers without deleting
- 📊 Peer status and last handshake
- 🔒 Safe config handling and key management
- 🚀 Systemd service + Nginx reverse proxy (optional)

## Tech Stack

- Backend: Flask (Python)
- Web Server: Nginx + Gunicorn (optional)
- VPN: WireGuard
- DB: SQLite (via SQLAlchemy)
- QR: `qrcode` / `qrencode`

## Prerequisites

- Ubuntu 20.04+ or Debian-based Linux
- Python 3.10+
- Sudo/root access
- Public IP or router port forwarding (UDP 51820)
- Optional domain (DuckDNS/Cloudflare)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/youssefkachmar/vpn-manager.git
cd vpn-manager

# Install dependencies
sudo apt update
sudo apt install -y wireguard wireguard-tools python3 python3-pip python3-venv nginx git qrencode

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

See [INSTALL.md](INSTALL.md) for the full installation and deployment guide.

## Configuration

Edit `config.py`:

```python
WG_SERVER_ENDPOINT = 'your-domain.com:51820'  # Or your public IP:51820
SECRET_KEY = 'your-random-secret-key'
```

## Usage

### Add a Peer

1. Open the web interface (e.g., `http://your-server-ip`)
2. Click “Add Peer”
3. Enter a name (e.g., “MyPhone”)
4. Scan the generated QR code with the WireGuard app

### Connect from Mobile

1. Install the [WireGuard app](https://www.wireguard.com/install/)
2. Scan the QR code
3. Enable the tunnel

### Manage Peers

- Toggle enable/disable without deleting
- Delete peers
- View last handshake and status

## Troubleshooting

### VPN connects but no internet

```bash
# IP forwarding must be enabled (should return 1)
sysctl net.ipv4.ip_forward

# Restart WireGuard
sudo systemctl restart wg-quick@wg0
```

### Port forwarding

Forward UDP 51820 on your router to your server’s local IP.

## Project Structure

```
vpn-manager/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── peer.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── auth.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── wireguard.py
│   ├── static/
│   │   ├── css/
│   │   └── qrcodes/
│   └── templates/
├── configs/            # Peer .conf files (gitignored)
├── config.py           # App configuration
├── run.py              # Entry point
├── requirements.txt    # Python deps
├── INSTALL.md          # Full installation guide
└── README.md           # This file
```

## Security Notes

- Server private key and `wg0.conf` should have `600` permissions
- Peer private keys stay on the server; QR shows public info needed to connect
- Consider preshared keys for additional security
- Do not commit secrets or keys to Git

## License

MIT License

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

## Acknowledgments

- [WireGuard](https://www.wireguard.com/)
- [Flask](https://flask.palletsprojects.com/)
- [DuckDNS](https://www.duckdns.org/)
- [Cloudflare](https://www.cloudflare.com/)

## Support

Open issues at: https://github.com/youssefkachmar/vpn-manager/issues

---

Made with ❤️ for secure and private internet access.
