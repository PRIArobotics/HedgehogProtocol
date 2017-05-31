from typing import Sequence, TypeVar

from hedgehog.protocol import CommSide
from hedgehog.utils.zmq.socket import Socket
from . import RawMessage, Message, RawPayload, Payload, \
    Header, DelimitedMsg, RawMsgs, Msgs, RawMsg, Msg


T = TypeVar('T')


def _rindex(mylist: Sequence[T], x: T) -> int:
    """Index of the last occurrence of x in the sequence."""
    return len(mylist) - mylist[::-1].index(x) - 1


def raw_to_delimited(header: Header, raw_payload: RawPayload) -> DelimitedMsg:
    """
    Returns a message consisting of header frames, delimiter frame, and payload frames.
    The payload frames may be given as sequences of bytes (raw) or as `Message`s.
    """
    return tuple(header) + (b'',) + tuple(raw_payload)


def to_delimited(header: Header, payload: Payload, side: CommSide) -> DelimitedMsg:
    """
    Returns a message consisting of header frames, delimiter frame, and payload frames.
    The payload frames may be given as sequences of bytes (raw) or as `Message`s.
    """
    return raw_to_delimited(header, [side.serialize(msg) for msg in payload])


def raw_from_delimited(msgs: DelimitedMsg) -> RawMsgs:
    """
    From a message consisting of header frames, delimiter frame, and payload frames, return a tuple `(header, payload)`.
    The payload frames may be returned as sequences of bytes (raw) or as `Message`s.
    """
    delim = _rindex(msgs, b'')
    return tuple(msgs[:delim]), tuple(msgs[delim + 1:])


def from_delimited(msgs: DelimitedMsg, side: CommSide) -> Msgs:
    """
    From a message consisting of header frames, delimiter frame, and payload frames, return a tuple `(header, payload)`.
    The payload frames may be returned as sequences of bytes (raw) or as `Message`s.
    """
    header, raw_payload = raw_from_delimited(msgs)
    return header, tuple(side.parse(msg_raw) for msg_raw in raw_payload)


class DealerRouterMixin(object):
    """
    A mixin for ZMQ dealer & router sockets used to send delimited & Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on dealer & router sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a header (one or more binary frames) followed by a delimiter (one empty frame). `send` methods
    accept a header parameter before the payload, `recv` methods return the header and payload as a tuple.
    """
    def send_msg(self, header: Header, msg: Message):
        self.send_msgs(header, [msg])

    def recv_msg(self) -> Msg:
        header, [msg] = self.recv_msgs()
        return header, msg

    def send_msgs(self, header: Header, msgs: Payload):
        self.send_msgs_raw(header, [self.side.serialize(msg) for msg in msgs])

    def recv_msgs(self) -> Msgs:
        header, msgs_raw = self.recv_msgs_raw()
        return header, tuple(self.side.parse(msg_raw) for msg_raw in msgs_raw)

    def send_msg_raw(self, header: Header, msg_raw: RawMessage):
        self.send_msgs_raw(header, [msg_raw])

    def recv_msg_raw(self) -> RawMsg:
        header, [msg_raw] = self.recv_msgs_raw()
        return header, msg_raw

    def send_msgs_raw(self, header: Header, msgs_raw: RawPayload):
        self.send_multipart(raw_to_delimited(header, msgs_raw))

    def recv_msgs_raw(self) -> RawMsgs:
        return raw_from_delimited(self.recv_multipart())


class DealerRouterSocket(DealerRouterMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(DealerRouterSocket, self).__init__(*args, **kwargs)
        self.side = side


class ReqMixin(object):
    """
    A mixin for ZMQ req sockets used to send Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on req sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a delimiter (one empty frame), implicitly added by the req socket.
    """

    def send_msg(self, msg: Message):
        self.send_msgs([msg])

    def recv_msg(self) -> Message:
        [msg] = self.recv_msgs()
        return msg

    def send_msgs(self, msgs: Payload):
        self.send_msgs_raw([self.side.serialize(msg) for msg in msgs])

    def recv_msgs(self) -> Payload:
        return tuple(self.side.parse(msg_raw) for msg_raw in self.recv_msgs_raw())

    def send_msg_raw(self, msg_raw: RawMessage):
        self.send_msgs_raw([msg_raw])

    def recv_msg_raw(self) -> RawMessage:
        [msg_raw] = self.recv_msgs_raw()
        return msg_raw

    def send_msgs_raw(self, msgs_raw: RawPayload):
        self.send_multipart(msgs_raw)

    def recv_msgs_raw(self) -> RawPayload:
        return self.recv_multipart()


class ReqSocket(ReqMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(ReqSocket, self).__init__(*args, **kwargs)
        self.side = side
