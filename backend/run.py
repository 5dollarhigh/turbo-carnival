#!/usr/bin/env python3
"""
Grocery Spend Tracker Backend Server

Run this script to start the Flask server on your PC.
Access from your phone by connecting to: http://<YOUR_PC_IP>:5000
"""

from app import create_app
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == '__main__':
    app = create_app()
    local_ip = get_local_ip()

    print("=" * 60)
    print("🛒 Grocery Spend Tracker Server")
    print("=" * 60)
    print(f"\nServer starting...")
    print(f"\nAccess from this PC:      http://localhost:5000")
    print(f"Access from your phone:   http://{local_ip}:5000")
    print(f"\nMake sure your phone and PC are on the same WiFi network!")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    print()

    # Run the Flask app
    # host='0.0.0.0' allows connections from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=True)
