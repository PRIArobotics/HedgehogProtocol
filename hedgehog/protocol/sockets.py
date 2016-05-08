from . import messages


def _rindex(mylist, elem):
    return len(mylist) - mylist[::-1].index(elem) - 1


class DealerRouterWrapper:
    """
    A wrapper for ZMQ dealer & router sockets used to send Hedgehog Protobuf messages.

    Each message consists of zero or more (opaque, binary) header frames, one (empty) delimiter frame,
    and one or more command frames (valid, Protobuf-encoded `HedgehogMessage`s).
    Serializing/parsing is handled by this class.

    Therefore, `send` and `recv` take/return the headers, and one `HedgehogMessage` object.
    The `_multipart` variants take/return the headers, and a list of `HedgehogMessage` objects.
    """
    def __init__(self, socket):
        self.socket = socket

    def send(self, header, msg):
        self.send_multipart(header, [msg])

    def recv(self):
        header, msgs = self.recv_multipart()
        assert len(msgs) == 1
        return header, msgs[0]

    def send_multipart(self, header, msgs):
        parts = header + [b''] + [msg.serialize() for msg in msgs]
        self.socket.send_multipart(parts)

    def recv_multipart(self):
        parts = self.socket.recv_multipart()
        delim = _rindex(parts, b'')
        header, msgs = parts[:delim], [messages.parse(msg) for msg in parts[delim + 1:]]
        return header, msgs

    def close(self):
        self.socket.close()


class ReqWrapper:
    """
    A wrapper for ZMQ req sockets used to send Hedgehog Protobuf messages.

    Each message consists of one (empty) delimiter frame,
    and one or more command frames (valid, Protobuf-encoded `HedgehogMessage`s).
    Serializing/parsing is handled by this class.

    Therefore, `send` and `recv` take/return one `HedgehogMessage` object.
    The `_multipart` variants take/return a list of `HedgehogMessage` objects.
    """

    def __init__(self, socket):
        self.socket = socket

    def send(self, msg):
        self.send_multipart([msg])

    def recv(self):
        msgs = self.recv_multipart()
        assert len(msgs) == 1
        return msgs[0]

    def send_multipart(self, msgs):
        parts = [msg.serialize() for msg in msgs]
        self.socket.send_multipart(parts)

    def recv_multipart(self):
        parts = self.socket.recv_multipart()
        msgs = [messages.parse(msg) for msg in parts]
        return msgs

    def close(self):
        self.socket.close()
