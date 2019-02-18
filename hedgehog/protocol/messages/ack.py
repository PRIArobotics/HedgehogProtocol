from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import ack_pb2
from hedgehog.utils import protobuf

__all__ = ['Acknowledgement']

# <GSL customizable: module-header>
from hedgehog.protocol.proto.ack_pb2 import OK, UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND

__all__ += ['OK', 'UNKNOWN_COMMAND', 'INVALID_COMMAND', 'UNSUPPORTED_COMMAND', 'FAILED_COMMAND']
# </GSL customizable: module-header>


@ReplyMsg.message(ack_pb2.Acknowledgement, 'acknowledgement', fields=('code', 'message',))
@dataclass(frozen=True, repr=False)
class Acknowledgement(SimpleMessage):
    code: int = OK
    message: str = ''

    def __post_init__(self):
        # <default GSL customizable: Acknowledgement-init-validation>
        pass
        # </GSL customizable: Acknowledgement-init-validation>

    # <default GSL customizable: Acknowledgement-extra-members />

    @classmethod
    def _parse(cls, msg: ack_pb2.Acknowledgement) -> 'Acknowledgement':
        code = msg.code
        message = msg.message
        return cls(code, message=message)

    def _serialize(self, msg: ack_pb2.Acknowledgement) -> None:
        msg.code = self.code
        msg.message = self.message
