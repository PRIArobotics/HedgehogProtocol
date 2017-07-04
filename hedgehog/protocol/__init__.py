from typing import Sequence, Tuple

from hedgehog.utils import protobuf

from .messages import ContainerMessage, Message, RequestMsg, ReplyMsg
from .errors import UnknownCommandError


# a single protobuf-encoded message
RawMessage = bytes
# a single decoded message
#Message
# a sequence of raw messages
RawPayload = Sequence[RawMessage]
# a sequence of decoded messages
Payload = Sequence[Message]

# sequence of zeromq header frames
Header = Sequence[bytes]
# a multipart ZeroMQ message with headers, delimiter and payload
DelimitedMsg = Sequence[bytes]
# a decoded message with headers and raw payload
RawMsgs = Tuple[Header, RawPayload]
# a decoded message with headers and payload
Msgs = Tuple[Header, Payload]
# a decoded message with headers and a single raw message
RawMsg = Tuple[Header, RawMessage]
# a decoded message with headers and a single message
Msg = Tuple[Header, Message]


class CommSide(object):
    def __init__(self, receiver: ContainerMessage, sender: protobuf.ContainerMessage) -> None:
        self.receiver = receiver
        self.sender = sender

    def parse(self, data: RawMessage) -> Message:
        """Parses a binary protobuf message into a Message object."""
        try:
            return self.receiver.parse(data)
        except KeyError as err:
            raise UnknownCommandError() from err

    def serialize(self, msg: Message) -> RawMessage:
        """Serializes a Message object into a binary protobuf message"""
        return self.sender.serialize(msg)


ServerSide = CommSide(RequestMsg, ReplyMsg)
ClientSide = CommSide(ReplyMsg, RequestMsg)
