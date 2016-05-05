from . import Message, register
from hedgehog.protocol.proto.ack_pb2 import OK


@register
class Acknowledgement(Message):
    _command_oneof = 'acknowledgement'

    def __init__(self, code=OK, message=''):
        self.code = code
        self.message = message

    @classmethod
    def _parse(cls, msg):
        return cls(msg.code, msg.message)

    def _serialize(self, msg):
        msg.code = self.code
        msg.message = self.message
