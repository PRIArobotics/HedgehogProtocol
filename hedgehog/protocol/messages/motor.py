from . import Message, register
from hedgehog.protocol.proto.motor_pb2 import POWER, BRAKE, VELOCITY


@register
class Action(Message):
    _command_oneof = 'motor_action'

    def __init__(self, port, state, amount=0, reached_state=POWER, relative=None, absolute=None):
        assert relative is None or absolute is None, "only one of absolute and relative may be set"
        self.port = port
        self.state = state
        self.amount = amount
        self.reached_state = reached_state
        self.relative = relative
        self.absolute = absolute

    @classmethod
    def _parse(cls, msg):
        return cls(
            msg.port, msg.state,
            msg.amount,
            msg.reached_state,
            msg.relative if msg.HasField('relative') else None,
            msg.absolute if msg.HasField('absolute') else None)

    def _serialize(self, msg):
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount
        msg.reached_state = self.reached_state
        if self.relative is not None: msg.relative = self.relative
        if self.absolute is not None: msg.absolute = self.absolute


@register
class Request(Message):
    _command_oneof = 'motor_request'

    def __init__(self, port):
        self.port = port

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port)

    def _serialize(self, msg):
        msg.port = self.port


@register
class Update(Message):
    _command_oneof = 'motor_update'

    def __init__(self, port, velocity, position):
        self.port = port
        self.velocity = velocity
        self.position = position

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.velocity, msg.position)

    def _serialize(self, msg):
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position


@register
class StateUpdate(Message):
    _command_oneof = 'motor_state_update'

    def __init__(self, port, state):
        self.port = port
        self.state = state

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.state)

    def _serialize(self, msg):
        msg.port = self.port
        msg.state = self.state


@register
class SetPositionAction(Message):
    _command_oneof = 'motor_set_position_action'

    def __init__(self, port, position):
        self.port = port
        self.position = position

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.position)

    def _serialize(self, msg):
        msg.port = self.port
        msg.position = self.position
