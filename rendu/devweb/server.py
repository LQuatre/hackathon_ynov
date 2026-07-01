import http.server
import socketserver
import http.client
import sys
import json

PORT = 5000
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default logs to keep terminal clean
        pass

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.handle_proxy("POST")
        else:
            self.send_error(404, "Not Found")

    def handle_proxy(self, method):
        # Read body if POST
        data = None
        headers = {}
        if method == "POST":
            content_length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(content_length)
            headers['Content-Type'] = self.headers.get('Content-Type', 'application/json')
        
        try:
            # Connect to Ollama
            conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=10)
            conn.request(method, self.path, body=data, headers=headers)
            response = conn.getresponse()
            
            # Send status code
            self.send_response(response.status)
            
            # Forward headers (excluding transport headers)
            for key, val in response.getheaders():
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    self.send_header(key, val)
            
            # Force chunked transfer encoding for browser streaming support
            self.send_header('Transfer-Encoding', 'chunked')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Stream response chunks to client
            while True:
                chunk = response.read(2048)
                if not chunk:
                    break
                # HTTP chunked transfer format: <hex_size>\r\n<data>\r\n
                size_line = f"{len(chunk):X}\r\n".encode('utf-8')
                self.wfile.write(size_line)
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
                
            # Closing chunk
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
            conn.close()
            
        except Exception as e:
            # Handle Ollama disconnection or errors gracefully
            try:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                err_msg = json.dumps({"error": f"Ollama is offline or unreachable: {str(e)}"}).encode('utf-8')
                self.wfile.write(err_msg)
            except Exception:
                pass

if __name__ == "__main__":
    # Enable port reuse to avoid 'Address already in use' errors
    socketserver.TCPServer.allow_reuse_address = True
    handler = ProxyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n=======================================================")
        print(f"🚀  Web interface running at: http://localhost:{PORT}")
        print(f"🔌  Proxying API calls to Ollama on {OLLAMA_HOST}:{OLLAMA_PORT}")
        print(f"Press Ctrl+C to stop the server.")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping web server. Goodbye!")
            sys.exit(0)
