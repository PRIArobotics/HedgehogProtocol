from . import messages


class RouterWrapper:
    """
    A wrapper for ZMQ router sockets used to send Hedgehog Protobuf messages.

    At this time, it is assumed that each message consists of one (opaque, binary) header part, and one message part
    (a valid, Protobuf-encoded `HedgehogMessage`).
    Therefore, `send` and `recv` take/return two values, respectively: a binary header, and a `HedgehogMessage` object.
    The object is serialized/parsed before being sent to the underlying socket.
    """
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
    """
    A wrapper for ZMQ dealer sockets used to send Hedgehog Protobuf messages.

    At this time, it is assumed that each message consists of one message part (a valid, Protobuf-encoded
    `HedgehogMessage`).
    Therefore, `send` and `recv` take/return one value, respectively: a `HedgehogMessage` object.
    The object is serialized/parsed before being sent to the underlying socket.
    """

    def __init__(self, socket):
        self.socket = socket

    def send(self, message):
        self.socket.send(message.SerializeToString())

    def recv(self):
        return messages.parse(self.socket.recv())

    def close(self):
        self.socket.close()
