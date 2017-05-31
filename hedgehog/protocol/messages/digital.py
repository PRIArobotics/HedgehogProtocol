from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.proto import io_pb2


@RequestMsg.message(io_pb2.DigitalMessage, 'digital_message', fields=('port',))
class Request(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: io_pb2.DigitalMessage) -> 'Request':
        return cls(msg.port)

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port


@ReplyMsg.message(io_pb2.DigitalMessage, 'digital_message')
class Reply(SimpleMessage):
    def __init__(self, port: int, value: bool) -> None:
        self.port = port
        self.value = value

    @classmethod
    def _parse(cls, msg: io_pb2.DigitalMessage) -> 'Reply':
        return cls(msg.port, msg.value)

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value
