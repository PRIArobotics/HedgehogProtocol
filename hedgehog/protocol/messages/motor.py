from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import motor_pb2
from hedgehog.protocol.proto.motor_pb2 import POWER, BRAKE, VELOCITY


@RequestMsg.message(motor_pb2.MotorAction, 'motor_action')
class Action(SimpleMessage):
    def __init__(self, port: int, state: int, amount: int=0,
                 reached_state: int=POWER, relative: int=None, absolute: int=None) -> None:
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
    def _parse(cls, msg: motor_pb2.MotorAction) -> 'Action':
        port = msg.port
        state = msg.state
        amount = msg.amount
        reached_state = msg.reached_state
        relative = msg.relative if msg.HasField('relative') else None
        absolute = msg.absolute if msg.HasField('absolute') else None
        return cls(port, state, amount, reached_state, relative, absolute)

    def _serialize(self, msg: motor_pb2.MotorAction) -> None:
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount
        msg.reached_state = self.reached_state
        if self.relative is not None:
            msg.relative = self.relative
        if self.absolute is not None:
            msg.absolute = self.absolute


@RequestMsg.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port',))
class CommandRequest(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorCommandMessage) -> 'CommandRequest':
        port = msg.port
        return cls(port)

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port


@ReplyMsg.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'state', 'amount'))
class CommandReply(SimpleMessage):
    def __init__(self, port: int, state: int, amount: int) -> None:
        self.port = port
        self.state = state
        self.amount = amount

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorCommandMessage) -> 'CommandReply':
        port = msg.port
        state = msg.state
        amount = msg.amount
        return cls(port, state, amount)

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount


@RequestMsg.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port',))
class StateRequest(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorStateMessage) -> 'StateRequest':
        port = msg.port
        return cls(port)

    def _serialize(self, msg: motor_pb2.MotorStateMessage):
        msg.port = self.port


@ReplyMsg.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'velocity', 'position'))
class StateReply(SimpleMessage):
    def __init__(self, port: int, velocity: int, position: int) -> None:
        self.port = port
        self.velocity = velocity
        self.position = position

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorStateMessage) -> 'StateReply':
        port = msg.port
        velocity = msg.velocity
        position = msg.position
        return cls(port, velocity, position)

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position


@RequestMsg.message(motor_pb2.MotorSetPositionAction, 'motor_set_position_action')
class SetPositionAction(SimpleMessage):
    def __init__(self, port: int, position: int) -> None:
        self.port = port
        self.position = position

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorSetPositionAction) -> 'SetPositionAction':
        port = msg.port
        position = msg.position
        return cls(port, position)

    def _serialize(self, msg: motor_pb2.MotorSetPositionAction) -> None:
        msg.port = self.port
        msg.position = self.position
