import http.server
import socketserver
import threading

class TestServer:
    def __init__(self, host_path: str):
        pass

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=host_path, **kwargs)
        self.handler = Handler        
        self.http = socketserver.TCPServer(("localhost", 0), self.handler)
        print(f'Serving at port {self.http.server_address[1]}')
        threading.Thread(target=self.http.serve_forever, daemon=True).start()


def start_server(host_path: str):
    server = TestServer(host_path)
    return f'{server.http.server_address[0]}:{server.http.server_address[1]}'
