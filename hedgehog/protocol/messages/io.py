from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import io_pb2
from hedgehog.protocol.proto.io_pb2 import INPUT_FLOATING, INPUT_PULLUP, INPUT_PULLDOWN
from hedgehog.protocol.proto.io_pb2 import OUTPUT_OFF, OUTPUT_ON

from hedgehog.protocol.proto.io_pb2 import OUTPUT, PULLUP, PULLDOWN, LEVEL


def _check_flags(flags: int) -> None:
    if flags & OUTPUT and flags & (PULLUP | PULLDOWN):
        raise InvalidCommandError("only input ports can be set to pullup or pulldown")
    if not flags & OUTPUT and flags & LEVEL:
        raise InvalidCommandError("only output ports can be set to on")
    if flags & PULLUP and flags & PULLDOWN:
        raise InvalidCommandError("pullup and pulldown are mutually exclusive")


@RequestMsg.message(io_pb2.IOStateAction, 'io_state_action')
class StateAction(SimpleMessage):
    def __init__(self, port: int, flags: int) -> None:
        _check_flags(flags)
        self.port = port
        self.flags = flags

    @property
    def output(self) -> bool:
        return (self.flags & OUTPUT) != 0

    @property
    def pullup(self) -> bool:
        return (self.flags & PULLUP) != 0

    @property
    def pulldown(self) -> bool:
        return (self.flags & PULLDOWN) != 0

    @property
    def level(self) -> bool:
        return (self.flags & LEVEL) != 0

    @classmethod
    def _parse(cls, msg: io_pb2.IOStateAction) -> 'StateAction':
        return cls(msg.port, msg.flags)

    def _serialize(self, msg: io_pb2.IOStateAction) -> None:
        msg.port = self.port
        msg.flags = self.flags


@RequestMsg.message(io_pb2.IOStateMessage, 'io_state_message', fields=('port',))
class StateRequest(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: io_pb2.IOStateAction) -> 'StateRequest':
        return cls(msg.port)

    def _serialize(self, msg: io_pb2.IOStateMessage) -> None:
        msg.port = self.port


@ReplyMsg.message(io_pb2.IOStateMessage, 'io_state_message')
class StateReply(SimpleMessage):
    def __init__(self, port: int, flags: int) -> None:
        _check_flags(flags)
        self.port = port
        self.flags = flags

    @property
    def output(self) -> bool:
        return (self.flags & OUTPUT) != 0

    @property
    def pullup(self) -> bool:
        return (self.flags & PULLUP) != 0

    @property
    def pulldown(self) -> bool:
        return (self.flags & PULLDOWN) != 0

    @property
    def level(self) -> bool:
        return (self.flags & LEVEL) != 0

    @classmethod
    def _parse(cls, msg: io_pb2.IOStateMessage) -> 'StateReply':
        return cls(msg.port, msg.flags)

    def _serialize(self, msg: io_pb2.IOStateMessage) -> None:
        msg.port = self.port
        msg.flags = self.flags
