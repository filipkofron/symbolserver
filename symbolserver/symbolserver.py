from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

USE_HTTPS = True

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        for item in self.headers.items():
            print("Header: " + str(item))
        print("Request: " + str(self.path))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello world\t' + threading.currentThread().getName().encode() + b'\t' + str(threading.active_count()).encode() + b'\n')


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    server = ThreadingSimpleServer(('0.0.0.0', 8000), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
