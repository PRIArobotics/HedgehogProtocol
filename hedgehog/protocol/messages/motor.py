from . import Msg, Message
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import motor_pb2
from hedgehog.protocol.proto.motor_pb2 import POWER, BRAKE, VELOCITY


@Msg.register(motor_pb2.MotorAction, 'motor_action')
class Action(Message):
    def __init__(self, port, state, amount=0, reached_state=POWER, relative=None, absolute=None):
        if relative is not None and absolute is not None:
            raise InvalidCommandError("relative and absolute are mutually exclusive")
        if relative is None and absolute is None:
            if reached_state != 0:
                raise InvalidCommandError(
                    "reached_state must be kept at its default value for non-positional motor commands")
        else:
            if state == BRAKE:
                raise InvalidCommandError("state can't be BRAKE for positional motor commands")
            if amount <= 0:
                raise InvalidCommandError("velocity/power must be positive for positional motor commands")
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


@Msg.register(motor_pb2.MotorRequest, 'motor_request')
class Request(Message):
    def __init__(self, port):
        self.port = port

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port)

    def _serialize(self, msg):
        msg.port = self.port


@Msg.register(motor_pb2.MotorUpdate, 'motor_update')
class Update(Message):
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


@Msg.register(motor_pb2.MotorStateUpdate, 'motor_state_update')
class StateUpdate(Message):
    async = True

    def __init__(self, port, state):
        self.port = port
        self.state = state

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.state)

    def _serialize(self, msg):
        msg.port = self.port
        msg.state = self.state


@Msg.register(motor_pb2.MotorSetPositionAction, 'motor_set_position_action')
class SetPositionAction(Message):
    def __init__(self, port, position):
        self.port = port
        self.position = position

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.position)

    def _serialize(self, msg):
        msg.port = self.port
        msg.position = self.position
