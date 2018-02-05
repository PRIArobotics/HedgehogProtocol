from hedgehog.protocol import CommSide
from hedgehog.utils.zmq.async_socket import Socket
from . import RawMessage, Message, RawPayload, Payload, \
    Header, RawMsgs, Msgs, RawMsg, Msg

from .sockets import raw_to_delimited, to_delimited, raw_from_delimited, from_delimited


class DealerRouterMixin(object):
    """
    A mixin for async ZMQ dealer & router sockets used to send delimited & Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on dealer & router sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a header (one or more binary frames) followed by a delimiter (one empty frame). `send` methods
    accept a header parameter before the payload, `recv` methods return the header and payload as a tuple.
    """
    async def send_msg(self, header: Header, msg: Message):
        await self.send_msgs(header, [msg])

    async def recv_msg(self) -> Msg:
        header, [msg] = await self.recv_msgs()
        return header, msg

    async def send_msgs(self, header: Header, msgs: Payload):
        await self.send_msgs_raw(header, [self.side.serialize(msg) for msg in msgs])

    async def recv_msgs(self) -> Msgs:
        header, msgs_raw = await self.recv_msgs_raw()
        return header, tuple(self.side.parse(msg_raw) for msg_raw in msgs_raw)

    async def send_msg_raw(self, header: Header, msg_raw: RawMessage):
        await self.send_msgs_raw(header, [msg_raw])

    async def recv_msg_raw(self) -> RawMsg:
        header, [msg_raw] = await self.recv_msgs_raw()
        return header, msg_raw

    async def send_msgs_raw(self, header: Header, msgs_raw: RawPayload):
        await self.send_multipart(raw_to_delimited(header, msgs_raw))

    async def recv_msgs_raw(self) -> RawMsgs:
        return raw_from_delimited(await self.recv_multipart())


class DealerRouterSocket(DealerRouterMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(DealerRouterSocket, self).__init__(*args, **kwargs)
        self.side = side


class ReqMixin(object):
    """
    A mixin for async ZMQ req sockets used to send Hedgehog-encoded messages.

    This mixin defines methods to send/receive single/multipart binary/hedgehog messages on req sockets.
    For example, `send_msg` send a single hedgehog message, while `recv_msgs_raw` receives a multipart binary message.
    All these methods use a delimiter (one empty frame), implicitly added by the req socket.
    """

    async def send_msg(self, msg: Message):
        await self.send_msgs([msg])

    async def recv_msg(self) -> Message:
        [msg] = await self.recv_msgs()
        return msg

    async def send_msgs(self, msgs: Payload):
        await self.send_msgs_raw([self.side.serialize(msg) for msg in msgs])

    async def recv_msgs(self) -> Payload:
        return tuple(self.side.parse(msg_raw) for msg_raw in await self.recv_msgs_raw())

    async def send_msg_raw(self, msg_raw: RawMessage):
        await self.send_msgs_raw([msg_raw])

    async def recv_msg_raw(self) -> RawMessage:
        [msg_raw] = await self.recv_msgs_raw()
        return msg_raw

    async def send_msgs_raw(self, msgs_raw: RawPayload):
        await self.send_multipart(msgs_raw)

    async def recv_msgs_raw(self) -> RawPayload:
        return await self.recv_multipart()


class ReqSocket(ReqMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(ReqSocket, self).__init__(*args, **kwargs)
        self.side = side
