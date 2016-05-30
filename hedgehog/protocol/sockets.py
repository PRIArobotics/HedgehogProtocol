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
    The `_raw` variants work on binary messages instead of `HedgehogMessage` objects.
    """
    def __init__(self, socket):
        self.socket = socket

    def send(self, header, msg):
        self.send_multipart(header, [msg])

    def recv(self):
        header, [msg] = self.recv_multipart()
        return header, msg

    def send_raw(self, header, msg_raw):
        self.send_multipart_raw(header, [msg_raw])

    def recv_raw(self):
        header, [msg_raw] = self.recv_multipart_raw()
        return header, msg_raw

    def send_multipart(self, header, msgs):
        msgs_raw = [msg.serialize() for msg in msgs]
        self.send_multipart_raw(header, msgs_raw)

    def recv_multipart(self):
        header, msgs_raw = self.recv_multipart_raw()
        return header, [messages.parse(msg) for msg in msgs_raw]

    def send_multipart_raw(self, header, msgs_raw):
        parts = header + [b''] + msgs_raw
        self.socket.send_multipart(parts)

    def recv_multipart_raw(self):
        parts = self.socket.recv_multipart()
        delim = _rindex(parts, b'')
        header, msgs_raw = parts[:delim], parts[delim + 1:]
        return header, msgs_raw

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
    The `_raw` variants work on binary messages instead of `HedgehogMessage` objects.
    """

    def __init__(self, socket):
        self.socket = socket

    def send(self, msg):
        self.send_multipart([msg])

    def recv(self):
        [msg] = self.recv_multipart()
        return msg

    def send_raw(self, msg_raw):
        self.send_multipart_raw([msg_raw])

    def recv_raw(self):
        [msg_raw] = self.recv_multipart_raw()
        return msg_raw

    def send_multipart(self, msgs):
        parts = [msg.serialize() for msg in msgs]
        self.send_multipart_raw(parts)

    def recv_multipart(self):
        parts = self.recv_multipart_raw()
        msgs = [messages.parse(msg) for msg in parts]
        return msgs

    def send_multipart_raw(self, msgs_raw):
        self.socket.send_multipart(msgs_raw)

    def recv_multipart_raw(self):
        msgs_raw = self.socket.recv_multipart()
        return msgs_raw

    def close(self):
        self.socket.close()
