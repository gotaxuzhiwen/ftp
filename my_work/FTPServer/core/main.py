import socketserver
from core.server import FTPServer

def main():
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 9999), FTPServer)
    server.serve_forever()