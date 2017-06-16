from . import ReplyMsg, SimpleMessage
from hedgehog.protocol.proto import ack_pb2
from hedgehog.protocol.proto.ack_pb2 import OK, UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND


@ReplyMsg.message(ack_pb2.Acknowledgement, 'acknowledgement')
class Acknowledgement(SimpleMessage):
    def __init__(self, code: int=OK, message: str='') -> None:
        self.code = code
        self.message = message

    @classmethod
    def _parse(cls, msg: ack_pb2.Acknowledgement) -> 'Acknowledgement':
        code = msg.code
        message = msg.message
        return cls(code, message)

    def _serialize(self, msg: ack_pb2.Acknowledgement) -> None:
        msg.code = self.code
        msg.message = self.message
