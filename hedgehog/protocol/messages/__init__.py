from hedgehog.utils import protobuf
from hedgehog.protocol.errors import UnknownCommandError
from ..proto import hedgehog_pb2


Msg = protobuf.MessageType(hedgehog_pb2.HedgehogMessage)


class Message(protobuf.Message):
    async = False


def parse(data):
    try:
        return Msg.parse(data)
    except KeyError as err:
        raise UnknownCommandError


def serialize(msg):
    return Msg.serialize(msg)
