from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.proto import io_pb2


@RequestMsg.message(io_pb2.DigitalMessage, 'digital_message', fields=('port',))
class Request(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: io_pb2.DigitalMessage) -> 'Request':
        port = msg.port
        return cls(port)

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port


@ReplyMsg.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value'))
class Reply(SimpleMessage):
    def __init__(self, port: int, value: bool) -> None:
        self.port = port
        self.value = value

    @classmethod
    def _parse(cls, msg: io_pb2.DigitalMessage) -> 'Reply':
        port = msg.port
        value = msg.value
        return cls(port, value)

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value
