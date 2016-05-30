from . import Msg, Message
from hedgehog.protocol.proto import ack_pb2
from hedgehog.protocol.proto.ack_pb2 import OK, UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND


@Msg.register(ack_pb2.Acknowledgement, 'acknowledgement')
class Acknowledgement(Message):
    def __init__(self, code=OK, message=''):
        self.code = code
        self.message = message

    @classmethod
    def _parse(cls, msg):
        return cls(msg.code, msg.message)

    def _serialize(self, msg):
        msg.code = self.code
        msg.message = self.message
