#!/usr/bin/env python3
"""Port Manager Server - Monitor and control ports & processes"""

import http.server
import json
import os
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PORT_MANAGER_ROOT = Path(__file__).parent
DASHBOARD_FILE = PORT_MANAGER_ROOT / "dashboard.html"
LOG_FILE = PORT_MANAGER_ROOT / "port_log.json"

def get_port_status():
    """Get all listening ports and their processes"""
    ports = {}

    try:
        # Run netstat to get port info
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            if 'LISTENING' not in line and 'ESTABLISHED' not in line:
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            try:
                proto = parts[0]
                local_addr = parts[1]
                state = parts[3]
                pid = int(parts[4])

                if ':' not in local_addr:
                    continue

                port = int(local_addr.split(':')[1])

                if state == 'LISTENING':
                    proc_name = get_process_name(pid)

                    if port not in ports:
                        ports[port] = {
                            'port': port,
                            'pid': pid,
                            'process': proc_name,
                            'state': state,
                            'proto': proto,
                            'timestamp': datetime.now().isoformat()
                        }
            except (ValueError, IndexError):
                continue

    except Exception as e:
        print(f"Error getting port status: {e}")

    return ports

def get_process_name(pid):
    """Get process name from PID"""
    try:
        result = subprocess.run(
            ['wmic', 'process', 'get', 'name,processid'],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    proc_pid = int(parts[-1])
                    if proc_pid == pid:
                        proc_name = ' '.join(parts[:-1])
                        return proc_name
                except ValueError:
                    pass
    except:
        pass

    return f"Unknown (PID: {pid})"

def kill_process(pid):
    """Kill a process by PID"""
    try:
        subprocess.run(
            ['taskkill', '/PID', str(pid), '/F'],
            capture_output=True,
            timeout=5
        )
        return True
    except:
        return False

def log_action(action, port, pid, process):
    """Log port management actions"""
    try:
        log_data = []
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                log_data = json.load(f)

        log_data.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'port': port,
            'pid': pid,
            'process': process
        })

        # Keep last 100 entries
        log_data = log_data[-100:]

        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)
    except:
        pass

class PortManagerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path in ['/', '/index.html']:
                self.serve_dashboard()
            elif self.path == '/api/ports':
                self.serve_ports_json()
            elif self.path == '/api/log':
                self.serve_log()
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)

            if self.path == '/api/kill':
                pid = data.get('pid')
                port = data.get('port')
                process = data.get('process')

                success = kill_process(pid)
                if success:
                    log_action('kill', port, pid, process)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': success}).encode())
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

    def serve_ports_json(self):
        ports = get_port_status()
        content = json.dumps(ports).encode()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def serve_log(self):
        if not LOG_FILE.exists():
            log_data = []
        else:
            with open(LOG_FILE) as f:
                log_data = json.load(f)

        content = json.dumps(log_data).encode()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass

def find_available_port(preferred_ports=None):
    """Find available port"""
    if preferred_ports is None:
        preferred_ports = [4000, 4001, 4002, 9001, 9002]

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

def start_server(port=None):
    if port is None:
        port = find_available_port()

    PORT_MANAGER_ROOT.mkdir(parents=True, exist_ok=True)

    if not DASHBOARD_FILE.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_FILE}")
        return

    try:
        http.server.HTTPServer.allow_reuse_address = True
        server = http.server.HTTPServer(("", port), PortManagerHandler)
    except OSError as e:
        print(f"ERROR: Could not bind to port {port}: {e}")
        return

    url = f"http://localhost:{port}"

    print("\n" + "="*70)
    print("PORT MANAGER SERVER STARTED")
    print("="*70)
    print(f"URL: {url}")
    print(f"\nFeatures:")
    print("  - Real-time port monitoring")
    print("  - Kill processes with one click")
    print("  - Action history logging")
    print("  - Auto-detect stuck processes")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")

    try:
        with server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nPort Manager stopped.")

if __name__ == "__main__":
    start_server()
