from hedgehog.utils import protobuf

from .messages import Message, RequestMsg, ReplyMsg
from .errors import UnknownCommandError


class CommSide(object):
    def __init__(self, receiver: protobuf.ContainerMessage, sender: protobuf.ContainerMessage) -> None:
        self.receiver = receiver
        self.sender = sender

    def parse(self, data: bytes) -> Message:
        """Parses a binary protobuf message into a Message object."""
        try:
            return self.receiver.parse(data)
        except KeyError as err:
            raise UnknownCommandError

    def serialize(self, msg: Message) -> bytes:
        """Serializes a Message object into a binary protobuf message"""
        return self.sender.serialize(msg)


ServerSide = CommSide(RequestMsg, ReplyMsg)
ClientSide = CommSide(ReplyMsg, RequestMsg)
