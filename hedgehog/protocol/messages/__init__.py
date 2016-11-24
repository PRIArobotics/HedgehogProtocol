from hedgehog.utils import protobuf
from hedgehog.protocol.errors import UnknownCommandError
from ..proto import hedgehog_pb2


Msg = protobuf.MessageType(hedgehog_pb2.HedgehogMessage)


class Message(protobuf.Message):
    async = False


def parse(data):
    """Parses a binary protobuf message into a Message object."""
    try:
        return Msg.parse(data)
    except KeyError as err:
        raise UnknownCommandError


def serialize(msg):
    """Serializes a Message object into a binary protobuf message"""
    return Msg.serialize(msg)
