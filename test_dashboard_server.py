#!/usr/bin/env python3
"""
Test script to verify dashboard server is working
Run this before starting the actual serve_dashboard.py
"""

import os
from pathlib import Path
import http.server
import socketserver
import threading
import time
import urllib.request
import json

PORT = 8000
PROJECT_ROOT = Path(__file__).parent

def test_server():
    """Test if the dashboard server can start and serve files"""

    print("="*70)
    print("Testing Dashboard Server Setup")
    print("="*70)

    # Test 1: Check if dashboard.html exists
    dashboard_file = PROJECT_ROOT / "dashboard.html"
    print("\n[TEST 1] Check dashboard.html exists")
    if dashboard_file.exists():
        size_kb = dashboard_file.stat().st_size / 1024
        print("OK: Found dashboard.html ({:.1f} KB)".format(size_kb))
    else:
        print("FAIL: NOT FOUND: {}".format(dashboard_file))
        return False

    # Test 2: Check if live_metrics path exists
    metrics_dir = PROJECT_ROOT / "data" / "training_logs"
    print("\n[TEST 2] Check metrics directory")
    if metrics_dir.exists():
        print("OK: Found directory: {}".format(metrics_dir))
    else:
        print("WARN: Directory missing (will be created during training): {}".format(metrics_dir))

    # Test 3: Try to start server on port 8000
    print("\n[TEST 3] Try to start server on port {}".format(PORT))

    class TestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logs

        def do_GET(self):
            if self.path == '/' or self.path == '':
                self.path = '/dashboard.html'
            return super().do_GET()

    try:
        os.chdir(PROJECT_ROOT)
        httpd = socketserver.TCPServer(("", PORT), TestHandler)
        print("OK: Server can bind to port {}".format(PORT))
    except OSError as e:
        print("FAIL: Cannot bind to port {}: {}".format(PORT, e))
        return False

    # Test 4: Serve in background and test fetch
    print("\n[TEST 4] Start server in background and test fetch")

    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)  # Give server time to start

    success = False
    try:
        # Try both URLs
        for url_path in ["http://127.0.0.1:{}/".format(PORT), "http://localhost:{}/".format(PORT)]:
            try:
                response = urllib.request.urlopen(url_path, timeout=3)
                content = response.read()
                if len(content) > 1000:
                    print("OK: Successfully fetched dashboard ({} bytes)".format(len(content)))
                    success = True
                    break
            except Exception as e:
                continue

        if not success:
            print("FAIL: Could not fetch dashboard")
            return False
    except Exception as e:
        print("FAIL: Error during fetch: {}".format(e))
        return False
    finally:
        httpd.server_close()

    # Test 5: Try to fetch live_metrics.json (should 404 before training)
    print("\n[TEST 5] Check live_metrics.json (will 404 before training starts)")
    metrics_file = PROJECT_ROOT / "data" / "training_logs" / "live_metrics.json"
    if metrics_file.exists():
        print("OK: Found: {}".format(metrics_file))
    else:
        print("INFO: Not yet created (will be created when training starts)")

    print("\n" + "="*70)
    print("ALL TESTS PASSED - Dashboard server is ready!")
    print("="*70)
    print("\nNext steps:")
    print("  1. python serve_dashboard.py")
    print("  2. Browser opens: http://localhost:8000/dashboard.html")
    print("  3. Start training: python training_12h.py")
    print("  4. Dashboard will update with live metrics")
    print()

    return True


if __name__ == "__main__":
    test_server()
