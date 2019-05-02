import socketserver
from core.ftpserver import FTPServer

def main():
    addr = ('127.0.0.1', 9000)
    myserver = socketserver.ThreadingTCPServer(addr, FTPServer)
    myserver.serve_forever()