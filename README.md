# WireGuard VPN Manager 🔐

A web-based management interface for WireGuard VPN server with QR code provisioning.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![WireGuard](https://img.shields.io/badge/WireGuard-enabled-green.svg)

## Features

- 🌐 Web-based GUI for VPN management
- 📱 QR code generation for easy mobile setup
- 👥 Multi-peer support
- 📊 Real-time peer statistics (online/offline, bandwidth)
- 🔄 Enable/disable peers without deletion
- 🔒 Secure configuration management
- 🚀 Easy deployment with systemd

## Tech Stack

- **Backend**: Flask (Python)
- **Web Server**: Nginx + Gunicorn
- **VPN**: WireGuard
- **Database**: SQLite (via SQLAlchemy)
- **QR Generation**: python-qrcode

## Prerequisites

- Ubuntu 20.04+ or Debian-based Linux
- Python 3.10+
- Root/sudo access
- Public IP or port forwarding (UDP 51820)
- Domain name (optional, recommended)

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

# Configure and start (see INSTALL.md for full instructions)
