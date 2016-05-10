from . import Message, register
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.io_pb2 import DIGITAL_FLOATING, DIGITAL_PULLUP, DIGITAL_PULLDOWN
from hedgehog.protocol.proto.io_pb2 import ANALOG_FLOATING, ANALOG_PULLUP, ANALOG_PULLDOWN
from hedgehog.protocol.proto.io_pb2 import OUTPUT_OFF, OUTPUT_ON

from hedgehog.protocol.proto.io_pb2 import OUTPUT, ANALOG, PULLUP, PULLDOWN, LEVEL


@register
class StateAction(Message):
    _command_oneof = 'io_state_action'

    def __init__(self, port, flags):
        if flags & OUTPUT and flags & ANALOG:
            raise InvalidCommandError("only input ports can be set to analog")
        if flags & OUTPUT and flags & (PULLUP | PULLDOWN):
            raise InvalidCommandError("only input ports can be set to pullup or pulldown")
        if not flags & OUTPUT and flags & LEVEL:
            raise InvalidCommandError("only output ports can be set to on")
        if flags & PULLUP and flags & PULLDOWN:
            raise InvalidCommandError("pullup and pulldown are mutually exclusive")
        self.port = port
        self.flags = flags

    @property
    def output(self):
        return (self.flags & OUTPUT) != 0

    @property
    def analog(self):
        return (self.flags & ANALOG) != 0

    @property
    def pullup(self):
        return (self.flags & PULLUP) != 0

    @property
    def pulldown(self):
        return (self.flags & PULLDOWN) != 0

    @property
    def level(self):
        return (self.flags & LEVEL) != 0

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.flags)

    def _serialize(self, msg):
        msg.port = self.port
        msg.flags = self.flags
