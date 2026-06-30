#!/usr/bin/env python3
"""Serve training dashboard on port 9000"""
import http.server
import socketserver
from pathlib import Path

PORT = 5000  # Dashboard exclusive port
PROJECT_ROOT = Path(__file__).parent.resolve()

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Determine file path
        if self.path == '/' or self.path == '':
            file_path = PROJECT_ROOT / 'dashboard.html'
        else:
            # Remove query string
            path = self.path.split('?')[0]
            file_path = PROJECT_ROOT / path.lstrip('/')

        # Security: prevent path traversal
        try:
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(PROJECT_ROOT)):
                self.send_error(403, "Access denied")
                return
        except:
            self.send_error(400, "Bad path")
            return

        # Check if file exists
        if not file_path.exists():
            self.send_error(404, f"Not found: {self.path}")
            return

        # Read file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")
            return

        # Determine content type
        if str(file_path).endswith('.html'):
            content_type = 'text/html; charset=utf-8'
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
        """Suppress logging"""
        pass

# Start server
if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"\n{'='*70}")
        print(f"Training Dashboard RUNNING")
        print(f"URL: http://localhost:{PORT}/")
        print(f"Metrics: http://localhost:{PORT}/data/training_logs/live_metrics.json")
        print(f"{'='*70}\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
