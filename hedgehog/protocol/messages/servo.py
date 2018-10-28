from typing import Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import servo_pb2
from hedgehog.utils import protobuf

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.subscription_pb2 import Subscription
# </GSL customizable: module-header>


@RequestMsg.message(servo_pb2.ServoAction, 'servo_action', fields=('port', 'active', 'position',))
@dataclass(frozen=True)
class Action(SimpleMessage):
    port: int
    active: bool
    position: int = None

    def __init__(self, port: int, active: bool, position: int=None) -> None:
        # <GSL customizable: Action-init-validation>
        if active and position is None:
            raise InvalidCommandError("position must be given when activating servo")
        # </GSL customizable: Action-init-validation>
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'active', active)
        object.__setattr__(self, 'position', position if active else None)

    # <default GSL customizable: Action-extra-members />

    @classmethod
    def _parse(cls, msg: servo_pb2.ServoAction) -> 'Action':
        port = msg.port
        active = msg.active
        position = msg.position
        return cls(port, active, position)

    def _serialize(self, msg: servo_pb2.ServoAction) -> None:
        msg.port = self.port
        msg.active = self.active
        if self.position is not None:
            msg.position = self.position


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port',))
@dataclass(frozen=True)
class CommandRequest(Message):
    port: int

    def __init__(self, port: int) -> None:
        # <default GSL customizable: CommandRequest-init-validation />
        object.__setattr__(self, 'port', port)

    # <default GSL customizable: CommandRequest-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'active', 'position',))
@dataclass(frozen=True)
class CommandReply(Message):
    port: int
    active: bool
    position: int

    def __init__(self, port: int, active: bool, position: int) -> None:
        # <default GSL customizable: CommandReply-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'active', active)
        object.__setattr__(self, 'position', position if active else None)

    # <default GSL customizable: CommandReply-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.active
        if self.position is not None:
            msg.position = self.position


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'subscription',))
@dataclass(frozen=True)
class CommandSubscribe(Message):
    port: int
    subscription: Subscription

    def __init__(self, port: int, subscription: Subscription) -> None:
        # <default GSL customizable: CommandSubscribe-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'subscription', subscription)

    # <default GSL customizable: CommandSubscribe-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'active', 'position', 'subscription',))
@dataclass(frozen=True)
class CommandUpdate(Message):
    is_async = True

    port: int
    active: bool
    position: int
    subscription: Subscription

    def __init__(self, port: int, active: bool, position: int, subscription: Subscription) -> None:
        # <default GSL customizable: CommandUpdate-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'active', active)
        object.__setattr__(self, 'position', position if active else None)
        object.__setattr__(self, 'subscription', subscription)

    # <default GSL customizable: CommandUpdate-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.active
        if self.position is not None:
            msg.position = self.position
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('servo_command_message')
def _parse_servo_command_message_request(msg: servo_pb2.ServoCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    active = msg.active
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_servo_command_message_request-return>
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)
    # </GSL customizable: _parse_servo_command_message_request-return>


@ReplyMsg.parser('servo_command_message')
def _parse_servo_command_message_reply(msg: servo_pb2.ServoCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    active = msg.active
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_servo_command_message_reply-return>
    if subscription is None:
        return CommandReply(port, active, position)
    else:
        return CommandUpdate(port, active, position, subscription)
    # </GSL customizable: _parse_servo_command_message_reply-return>
