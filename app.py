#!/usr/bin/env python3
"""
Simple runner for the Trade Calculator bundle.
Run this file with: python app.py
It starts a static HTTP server serving the folder (index.html) and opens your browser.
If port 8080 is taken it will try 8000.
"""
import argparse
import http.server
import socketserver
import os
import webbrowser
import sys
import socket

PORTS_TO_TRY = [8080, 8000]
HERE = os.path.dirname(os.path.abspath(__file__))

os.chdir(HERE)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # minimize console spam
        sys.stdout.write("[http] %s - %s\n" % (self.client_address[0], format % args))
        sys.stdout.flush()


# Use a server class that allows quick restarts and uses daemon threads so
# KeyboardInterrupt shuts things down cleanly.
class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def find_free_port(ports):
    for p in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", p))
                return p
            except OSError:
                continue
    return None


def run():
    parser = argparse.ArgumentParser(description="Serve the trade_calculator_bundle folder and open a browser")
    parser.add_argument('--port', '-p', type=int, help='Port to use (overrides automatic selection)')
    parser.add_argument('--no-browser', action='store_true', help="Don't open the web browser automatically")
    args = parser.parse_args()

    if args.port:
        port = args.port
        # If a specific port was requested, check it's available quickly.
        if find_free_port([port]) is None:
            # Port unavailable — exit silently
            sys.exit(1)
    else:
        port = find_free_port(PORTS_TO_TRY)
        if port is None:
            # No free ports found — exit silently
            sys.exit(1)

    handler = QuietHandler
    try:
        with ReusableThreadingTCPServer(("", port), handler) as httpd:
            url = f"http://localhost:{port}/"
            if not args.no_browser:
                try:
                    webbrowser.open(url, new=2)
                except Exception:
                    # Ignore browser open failures (silent)
                    pass
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                # Server stopped by user
                pass
    except Exception as e:
        # Failed to start server — exit silently
        sys.exit(1)

if __name__ == '__main__':
    run()
