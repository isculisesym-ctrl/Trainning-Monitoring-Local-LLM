#!/usr/bin/env python3
"""
Simple HTTP server for the training dashboard
Run this in a separate terminal: python serve_dashboard.py
Then open: http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
import socket
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def find_available_port(preferred_ports=[3000, 5000, 5001, 8001, 8002, 8003, 9000]):
    """Find an available port from preferred list"""
    for port in preferred_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                s.bind(('127.0.0.1', port))  # Also try localhost
                return port
        except OSError:
            pass

    # Fallback: try range starting from 9000
    for port in range(9000, 9100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            pass
    return None


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """Custom handler to serve dashboard and data files with CORS"""

    def do_GET(self):
        """Handle GET requests"""
        # Parse the path
        if self.path == '/' or self.path == '' or self.path == '/index.html':
            file_path = PROJECT_ROOT / "dashboard.html"
        elif self.path.startswith('/data/'):
            # Serve data files (like live_metrics.json)
            file_path = PROJECT_ROOT / self.path.lstrip('/')
        else:
            # Try to serve from PROJECT_ROOT
            file_path = PROJECT_ROOT / self.path.lstrip('/')

        # Security: prevent path traversal
        try:
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(PROJECT_ROOT.resolve())):
                self.send_error(403, "Access denied")
                return
        except:
            self.send_error(400, "Bad path")
            return

        # Check if file exists
        if not file_path.exists():
            self.send_error(404, "Not found: {}".format(self.path))
            return

        # Read file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            self.send_error(500, "Error reading file: {}".format(e))
            return

        # Determine content type
        if str(file_path).endswith('.html'):
            content_type = 'text/html'
        elif str(file_path).endswith('.json'):
            content_type = 'application/json'
        elif str(file_path).endswith('.js'):
            content_type = 'application/javascript'
        elif str(file_path).endswith('.css'):
            content_type = 'text/css'
        else:
            content_type = 'application/octet-stream'

        # Send response
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        """Minimal logging"""
        pass  # Suppress verbose logs


def main():
    """Start the dashboard server"""
    # Verify dashboard exists
    dashboard_file = PROJECT_ROOT / "dashboard.html"
    if not dashboard_file.exists():
        print("ERROR: dashboard.html not found at {}".format(dashboard_file))
        return

    # Find available port
    port = find_available_port()
    if port is None:
        print("ERROR: Could not find available port")
        return

    # Create server
    try:
        http.server.HTTPServer.allow_reuse_address = True
        httpd = http.server.HTTPServer(("", port), DashboardHandler)
    except OSError as e:
        print("ERROR: Could not start server on port {}".format(port))
        print("Details: {}".format(e))
        return

    url = "http://localhost:{}".format(port)
    metrics_file = PROJECT_ROOT / "data" / "training_logs" / "live_metrics.json"

    print("\n" + "="*70)
    print("Training Dashboard Server STARTED")
    print("="*70)
    print("URL: {}".format(url))
    print("Directory: {}".format(PROJECT_ROOT))
    print("Dashboard: {}".format(dashboard_file))
    print("Metrics: {}".format(metrics_file))
    print("\nWill auto-refresh every 2 seconds during training")
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")

    # Try to open browser
    try:
        webbrowser.open(url)
        print("Browser opening (if not, open manually: {})\n".format(url))
    except:
        print("Please open: {}\n".format(url))

    try:
        with httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print("Error: {}".format(e))


if __name__ == "__main__":
    main()
