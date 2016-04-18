from . import messages


class RouterWrapper:
    def __init__(self, socket):
        self.socket = socket

    def send(self, header, message):
        parts = [header, message.SerializeToString()]
        self.socket.send_multipart(parts)

    def recv(self):
        header, payload = self.socket.recv_multipart()
        return header, messages.parse(payload)

    def close(self):
        self.socket.close()


class DealerWrapper:
    def __init__(self, socket):
        self.socket = socket

    def send(self, message):
        self.socket.send(message.SerializeToString())

    def recv(self):
        return messages.parse(self.socket.recv())

    def close(self):
        self.socket.close()
