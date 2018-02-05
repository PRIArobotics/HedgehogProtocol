from typing import Union

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import motor_pb2
from hedgehog.protocol.proto.motor_pb2 import POWER, BRAKE, VELOCITY
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.utils import protobuf


@RequestMsg.message(motor_pb2.MotorAction, 'motor_action')
class Action(SimpleMessage):
    def __init__(self, port: int, state: int, amount: int=0, reached_state: int=POWER, relative: int=None, absolute: int=None) -> None:
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


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port',))
class CommandRequest(Message):
    def __init__(self, port: int) -> None:
        self.port = port

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'subscription'))
class CommandSubscribe(Message):
    def __init__(self, port: int, subscription: Subscription) -> None:
        self.port = port
        self.subscription = subscription

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('motor_command_message')
def _parse_command_request(msg: motor_pb2.MotorCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'state', 'amount'))
class CommandReply(Message):
    def __init__(self, port: int, state: int, amount: int) -> None:
        self.port = port
        self.state = state
        self.amount = amount

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message')
class CommandUpdate(Message):
    is_async = True

    def __init__(self, port: int, state: int, amount: int, subscription: Subscription) -> None:
        self.port = port
        self.state = state
        self.amount = amount
        self.subscription = subscription

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount
        msg.subscription.CopyFrom(self.subscription)


@ReplyMsg.parser('motor_command_message')
def _parse_command_reply(msg: motor_pb2.MotorCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    state = msg.state
    amount = msg.amount
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandReply(port, state, amount)
    else:
        return CommandUpdate(port, state, amount, subscription)


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port',))
class StateRequest(Message):
    def __init__(self, port: int) -> None:
        self.port = port

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'subscription'))
class StateSubscribe(Message):
    def __init__(self, port: int, subscription: Subscription) -> None:
        self.port = port
        self.subscription = subscription

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('motor_state_message')
def _parse_state_request(msg: motor_pb2.MotorStateMessage) -> Union[StateRequest, StateSubscribe]:
    port = msg.port
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return StateRequest(port)
    else:
        return StateSubscribe(port, subscription)


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'velocity', 'position'))
class StateReply(Message):
    def __init__(self, port: int, velocity: int, position: int) -> None:
        self.port = port
        self.velocity = velocity
        self.position = position

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message')
class StateUpdate(Message):
    is_async = True

    def __init__(self, port: int, velocity: int, position: int, subscription: Subscription) -> None:
        self.port = port
        self.velocity = velocity
        self.position = position
        self.subscription = subscription

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position
        msg.subscription.CopyFrom(self.subscription)


@ReplyMsg.parser('motor_state_message')
def _parse_state_reply(msg: motor_pb2.MotorStateMessage) -> Union[StateReply, StateUpdate]:
    port = msg.port
    velocity = msg.velocity
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return StateReply(port, velocity, position)
    else:
        return StateUpdate(port, velocity, position, subscription)
