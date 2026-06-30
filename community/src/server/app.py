#!/usr/bin/env python3
"""Training Dashboard Server"""

import http.server
import json
import os
import socket
import webbrowser
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
METRICS_FILE = PROJECT_ROOT / "data" / "logs" / "metrics.json"
DASHBOARD_FILE = PROJECT_ROOT / "src" / "web" / "dashboard.html"

def find_available_port(preferred_ports=None):
    if preferred_ports is None:
        preferred_ports = [3000, 5000, 5001, 8001, 8002, 8003, 9000]
    
    for port in preferred_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            pass
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path in ['/', '', '/index.html']:
                self.serve_dashboard()
            elif self.path == '/data/metrics':
                self.serve_metrics()
            elif self.path == '/config/session':
                self.serve_config()
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_dashboard(self):
        if not DASHBOARD_FILE.exists():
            self.send_error(404)
            return
        
        with open(DASHBOARD_FILE, 'rb') as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)
    
    def serve_metrics(self):
        if not METRICS_FILE.exists():
            metrics = {"status": "no_data"}
        else:
            with open(METRICS_FILE) as f:
                metrics = json.load(f)
        
        content = json.dumps(metrics).encode()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)
    
    def serve_config(self):
        config_file = PROJECT_ROOT / "config" / "training_session.json"
        if not config_file.exists():
            config = {}
        else:
            with open(config_file) as f:
                config = json.load(f)
        
        content = json.dumps(config).encode()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)
    
    def log_message(self, *args):
        pass

def start_server(port=None):
    if port is None:
        port = find_available_port()
    
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if not DASHBOARD_FILE.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_FILE}")
        return
    
    try:
        http.server.HTTPServer.allow_reuse_address = True
        server = http.server.HTTPServer(("", port), Handler)
    except OSError as e:
        print(f"ERROR: Could not bind to port {port}: {e}")
        return
    
    url = f"http://localhost:{port}"
    
    print("\n" + "="*70)
    print("Training Dashboard Server STARTED")
    print("="*70)
    print(f"URL: {url}")
    print(f"Dashboard: {DASHBOARD_FILE}")
    print(f"Metrics: {METRICS_FILE}")
    print("\nMetrics auto-refresh every 2 seconds")
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        webbrowser.open(url)
    except:
        print(f"Open in browser: {url}\n")
    
    try:
        with server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == "__main__":
    start_server()
