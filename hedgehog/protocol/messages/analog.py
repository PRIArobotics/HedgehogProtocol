from . import Msg, Message
from hedgehog.protocol.proto import io_pb2


@Msg.register(io_pb2.AnalogRequest, 'analog_request')
class Request(Message):
    def __init__(self, port):
        self.port = port

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port)

    def _serialize(self, msg):
        msg.port = self.port


@Msg.register(io_pb2.AnalogUpdate, 'analog_update')
class Update(Message):
    def __init__(self, port, value):
        self.port = port
        self.value = value

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.value)

    def _serialize(self, msg):
        msg.port = self.port
        msg.value = self.value
