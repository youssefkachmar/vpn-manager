from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from app.models.peer import Peer
from app.models.user import User
from app.utils.wireguard import WireGuardManager
from app import db
from werkzeug.security import check_password_hash
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Redirect to dashboard or login"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@main.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    peers = Peer.query.order_by(Peer.created_at.desc()).all()

    # Get WireGuard stats
    wg_manager = WireGuardManager()
    stats = wg_manager.get_peer_stats()

    # Update peer stats in context
    for peer in peers:
        if peer.public_key in stats:
            peer.stats = stats[peer.public_key]
        else:
            peer.stats = {
                'online': False,
                'rx_bytes': 0,
                'tx_bytes': 0
            }

    return render_template('dashboard.html', peers=peers, username=session.get('username'))

@main.route('/peer/new', methods=['GET', 'POST'])
def new_peer():
    """Create new peer"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Peer name is required', 'danger')
            return redirect(url_for('main.new_peer'))

        # Initialize WireGuard manager
        wg_manager = WireGuardManager()

        # Generate keys
        keys = wg_manager.generate_keys()
        if not keys:
            flash('Failed to generate keys', 'danger')
            return redirect(url_for('main.new_peer'))

        # Get next available IP
        ip_address = wg_manager.get_next_ip()
        if not ip_address:
            flash('No available IP addresses', 'danger')
            return redirect(url_for('main.new_peer'))

        # Create peer in database
        peer = Peer(
            name=name,
            ip_address=ip_address,
            public_key=keys['public_key'],
            private_key=keys['private_key'],
            preshared_key=keys['preshared_key'],
            enabled=True
        )

        try:
            db.session.add(peer)
            db.session.commit()

            # Generate peer config
            config_content = wg_manager.generate_peer_config(peer)
            wg_manager.save_peer_config(peer, config_content)

            # Generate QR code
            wg_manager.generate_qrcode(config_content, peer.id)

            # Update server config
            wg_manager.save_server_config()
            wg_manager.reload_wireguard()

            flash(f'Peer "{name}" created successfully!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating peer: {str(e)}', 'danger')
            return redirect(url_for('main.new_peer'))

    return render_template('add_peer.html')

@main.route('/peer/<int:peer_id>/delete', methods=['POST'])
def delete_peer(peer_id):
    """Delete a peer"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    peer = Peer.query.get_or_404(peer_id)
    peer_name = peer.name

    try:
        # Delete from database
        db.session.delete(peer)
        db.session.commit()

        # Delete peer files
        wg_manager = WireGuardManager()
        wg_manager.delete_peer_files(peer_id)

        # Update server config
        wg_manager.save_server_config()
        wg_manager.reload_wireguard()

        flash(f'Peer "{peer_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting peer: {str(e)}', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route('/peer/<int:peer_id>/toggle', methods=['POST'])
def toggle_peer(peer_id):
    """Toggle peer enabled/disabled status"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    peer = Peer.query.get_or_404(peer_id)

    wg_manager = WireGuardManager()
    success = wg_manager.toggle_peer(peer_id, not peer.enabled)

    if success:
        status = "enabled" if peer.enabled else "disabled"
        flash(f'Peer "{peer.name}" has been {status}!', 'success')
    else:
        flash('Failed to toggle peer status.', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route('/peer/<int:peer_id>/qrcode')
def show_qrcode(peer_id):
    """Show QR code page for a peer"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    peer = Peer.query.get_or_404(peer_id)
    qr_filename = f'peer_{peer.id}.png'

    return render_template('qrcode.html', peer=peer, qr_filename=qr_filename)

@main.route('/peer/<int:peer_id>/download')
def download_config(peer_id):
    """Download peer configuration file"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    peer = Peer.query.get_or_404(peer_id)

    from flask import current_app
    config_dir = current_app.config.get('CONFIG_DIR')
    config_path = os.path.join(config_dir, f'peer_{peer.id}.conf')

    if not os.path.exists(config_path):
        flash('Configuration file not found', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(
        config_path,
        as_attachment=True,
        download_name=f'{peer.name}.conf',
        mimetype='text/plain'
    )

@main.route('/api/peer-stats')
def peer_stats():
    """API endpoint to get peer statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    wg_manager = WireGuardManager()
    stats = wg_manager.get_peer_stats()

    # Update last_seen and bandwidth for online peers
    peers = Peer.query.all()

    for peer in peers:
        if peer.public_key in stats:
            peer_stat = stats[peer.public_key]
            if peer_stat['online']:
                peer.last_seen = datetime.utcnow()
            peer.total_rx = peer_stat['rx_bytes']
            peer.total_tx = peer_stat['tx_bytes']

    db.session.commit()

    # Return stats mapped to peer IDs
    result = {}
    for peer in peers:
        if peer.public_key in stats:
            result[peer.id] = stats[peer.public_key]
        else:
            result[peer.id] = {
                'online': False,
                'rx_bytes': peer.total_rx,
                'tx_bytes': peer.total_tx,
                'endpoint': None,
                'latest_handshake': 0
            }

    return jsonify(result)

@main.route('/settings')
def settings():
    """Settings page"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    from flask import current_app
    wg_manager = WireGuardManager()

    settings_data = {
        'endpoint': current_app.config.get('WG_SERVER_ENDPOINT'),
        'server_public_key': wg_manager.get_server_public_key(),
        'interface': wg_manager.get_main_interface(),
        'total_peers': Peer.query.count(),
        'enabled_peers': Peer.query.filter_by(enabled=True).count(),
        'disabled_peers': Peer.query.filter_by(enabled=False).count()
    }

    return render_template('settings.html', settings=settings_data)
