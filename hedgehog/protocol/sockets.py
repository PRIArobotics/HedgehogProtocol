from hedgehog.utils.zmq.socket import Socket
from .messages import parse, serialize


def _rindex(mylist, x):
    """Index of the last occurrence of x in the sequence."""
    return len(mylist) - mylist[::-1].index(x) - 1


def to_delimited(header, payload, raw=True):
    """
    Returns a message consisting of header frames, delimiter frame, and payload frames.
    The payload frames may be given as sequences of bytes (raw) or as `Message`s.
    """
    msgs_raw = tuple(payload) if raw else tuple(serialize(msg) for msg in payload)
    return tuple(header) + (b'',) + msgs_raw


def from_delimited(msgs, raw=True):
    """
    From a message consisting of header frames, delimiter frame, and payload frames, return a tuple `(header, payload)`.
    The payload frames may be returned as sequences of bytes (raw) or as `Message`s.
    """
    delim = _rindex(msgs, b'')
    header, payload = tuple(msgs[:delim]), msgs[delim + 1:]
    return header, tuple(payload) if raw else tuple(parse(msg_raw) for msg_raw in payload)


class DealerRouterMixin(object):
    """
    A mixin for ZMQ dealer & router sockets used to send delimited & Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on dealer & router sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a header (one or more binary frames) followed by a delimiter (one empty frame). `send` methods
    accept a header parameter before the payload, `recv` methods return the header and payload as a tuple.
    """
    def send_msg(self, header, msg):
        self.send_msgs(header, [msg])

    def recv_msg(self):
        header, [msg] = self.recv_msgs()
        return header, msg

    def send_msgs(self, header, msgs):
        self.send_msgs_raw(header, (serialize(msg) for msg in msgs))

    def recv_msgs(self):
        header, msgs_raw = self.recv_msgs_raw()
        return header, tuple(parse(msg_raw) for msg_raw in msgs_raw)

    def send_msg_raw(self, header, msg_raw):
        self.send_msgs_raw(header, [msg_raw])

    def recv_msg_raw(self):
        header, [msg_raw] = self.recv_msgs_raw()
        return header, msg_raw

    def send_msgs_raw(self, header, msgs_raw):
        self.send_multipart(to_delimited(header, msgs_raw))

    def recv_msgs_raw(self):
        return from_delimited(self.recv_multipart())


class DealerRouterSocket(DealerRouterMixin, Socket):
    pass


class ReqMixin(object):
    """
    A mixin for ZMQ req sockets used to send Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on req sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a delimiter (one empty frame), implicitly added by the req socket.
    """

    def send_msg(self, msg):
        self.send_msgs([msg])

    def recv_msg(self):
        [msg] = self.recv_msgs()
        return msg

    def send_msgs(self, msgs):
        self.send_msgs_raw([serialize(msg) for msg in msgs])

    def recv_msgs(self):
        return tuple(parse(msg_raw) for msg_raw in self.recv_msgs_raw())

    def send_msg_raw(self, msg_raw):
        self.send_msgs_raw([msg_raw])

    def recv_msg_raw(self):
        [msg_raw] = self.recv_msgs_raw()
        return msg_raw

    def send_msgs_raw(self, msgs_raw):
        self.send_multipart(msgs_raw)

    def recv_msgs_raw(self):
        return self.recv_multipart()


class ReqSocket(ReqMixin, Socket):
    pass
