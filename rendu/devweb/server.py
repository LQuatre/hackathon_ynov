import http.server
import socketserver
import http.client
import sys
import json

PORT = 5000
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
USE_SSL = False
AUTH_HEADER = ""

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

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
            # Inject authorization header for Cloudflare basic auth
            headers['Authorization'] = AUTH_HEADER
            
            # Connect to Ollama (HTTPS or HTTP)
            if USE_SSL:
                conn = http.client.HTTPSConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=30)
            else:
                conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=30)
                
            conn.request(method, self.path, body=data, headers=headers)
            response = conn.getresponse()
            
            # Send status code
            self.send_response(response.status)
            
            # Forward headers (excluding transport headers and standard defaults)
            for key, val in response.getheaders():
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection', 'date', 'server', 'content-type', 'cache-control']:
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
            sys.stderr.write(f"Proxy Connection Error: {str(e)}\n")
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
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    handler = ProxyHTTPRequestHandler
    
    with socketserver.ThreadingTCPServer(("", PORT), handler) as httpd:
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
