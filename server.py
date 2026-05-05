#!/usr/bin/env python3
"""
Servidor local para el Facturador RJCH.
Sirve index.html en http://localhost:8080
y hace proxy de las llamadas a la API de Anthropic (resuelve el error CORS).

Uso:
    python3 server.py
    python3 server.py 8080        # puerto personalizado
"""

import sys
import os
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

class Handler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silenciar logs de archivos estáticos, solo mostrar proxy
        if '/proxy/' in (args[0] if args else ''):
            super().log_message(format, *args)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/proxy/anthropic':
            self._proxy_anthropic()
        else:
            self.send_error(404)

    def _proxy_anthropic(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        api_key = self.headers.get('X-Api-Key', '')
        model_header = self.headers.get('X-Model', '')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._cors()
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Api-Key, X-Model')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(('localhost', PORT), Handler)
    print(f'\n  Facturador RJCH corriendo en:')
    print(f'  → http://localhost:{PORT}')
    print(f'\n  Ctrl+C para detener\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor detenido.')
