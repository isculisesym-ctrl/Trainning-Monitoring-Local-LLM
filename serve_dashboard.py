#!/usr/bin/env python3
"""
Simple HTTP server for the training dashboard
Run this in a separate terminal: python serve_dashboard.py
Then open: http://localhost:8000/dashboard.html
"""

import http.server
import socketserver
import webbrowser
import time
from pathlib import Path

PORT = 8000
DASHBOARD_PATH = Path(__file__).parent / "dashboard.html"


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from current directory and enable CORS"""

    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def main():
    os.chdir(Path(__file__).parent)

    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        url = f"http://localhost:{PORT}/dashboard.html"
        print(f"\n{'='*70}")
        print(f"Training Dashboard Server")
        print(f"{'='*70}")
        print(f"Server running at: {url}")
        print(f"\nMetrics file location: data/training_logs/live_metrics.json")
        print(f"Updates every 2 seconds while training is running")
        print(f"\nPress Ctrl+C to stop the server")
        print(f"{'='*70}\n")

        # Try to open browser
        try:
            webbrowser.open(url)
            print(f"Opening browser... (may take a few seconds)")
        except:
            print(f"Please open your browser manually: {url}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\nServer stopped.")


if __name__ == "__main__":
    import os
    main()
