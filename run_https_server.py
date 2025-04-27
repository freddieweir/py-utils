#!/usr/bin/env python3
"""
run_https_server.py

A simple HTTPS server using automatically generated self-signed certificates.
"""
import sys

from module_venv import AutoVirtualEnvironment
from ssl_setup import SSLManager
from http.server import HTTPServer, SimpleHTTPRequestHandler


def main():
    # Ensure virtual environment and install cryptography
    env = AutoVirtualEnvironment(auto_packages=['cryptography'])
    env.auto_switch()

    # Initialize SSL manager and get SSL context
    manager = SSLManager(common_name='localhost')
    context = manager.get_ssl_context()

    # Configure and start HTTPS server
    server_address = ('localhost', 4443)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"🚀 Serving on https://{server_address[0]}:{server_address[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Shutting down server...")
        httpd.server_close()


if __name__ == '__main__':
    main() 