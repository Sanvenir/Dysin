# -*- coding:utf-8 -*-
"""TCP/UDP message server for receiving external text."""
import socket
from PySide6.QtCore import QThread, Signal


class MessageServer(QThread):
    """TCP/UDP message server."""
    messageReceived = Signal(str)

    def __init__(self, port=7654):
        super().__init__()
        self.port = port
        self.running = False
        self.tcp_socket = None
        self.udp_socket = None

    def run(self):
        self.running = True
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('127.0.0.1', self.port))
        self.tcp_socket.listen(5)
        self.tcp_socket.settimeout(1.0)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('127.0.0.1', self.port))
        self.udp_socket.settimeout(1.0)
        while self.running:
            try:
                client, addr = self.tcp_socket.accept()
                data = client.recv(4096).decode('utf-8', errors='ignore')
                client.close()
                if data and self.messageReceived:
                    self.messageReceived.emit(data.strip())
            except socket.timeout:
                pass
            except Exception:
                pass
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                message = data.decode('utf-8', errors='ignore').strip()
                if message and self.messageReceived:
                    self.messageReceived.emit(message)
            except socket.timeout:
                pass
            except Exception:
                pass

    def stop(self):
        self.running = False
        if self.tcp_socket:
            try: self.tcp_socket.close()
            except: pass
        if self.udp_socket:
            try: self.udp_socket.close()
            except: pass
