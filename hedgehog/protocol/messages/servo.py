from typing import Any, Optional, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import servo_pb2
from hedgehog.utils import protobuf

__all__ = ['Action', 'CommandRequest', 'CommandReply', 'CommandSubscribe', 'CommandUpdate']

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.subscription_pb2 import Subscription

__all__ += ['Subscription']
# </GSL customizable: module-header>


@RequestMsg.message(servo_pb2.ServoAction, 'servo_action', fields=('port', 'position',))
@dataclass(frozen=True, repr=False)
class Action(SimpleMessage):
    port: int
    position: Optional[int]

    def __post_init__(self):
        # <default GSL customizable: Action-init-validation>
        pass
        # </GSL customizable: Action-init-validation>

    # <default GSL customizable: Action-extra-members />

    @classmethod
    def _parse(cls, msg: servo_pb2.ServoAction) -> 'Action':
        port = msg.port
        active = msg.active
        position = msg.position
        return cls(port, position if active else None)

    def _serialize(self, msg: servo_pb2.ServoAction) -> None:
        msg.port = self.port
        msg.active = self.position is not None
        if self.position is not None:
            msg.position = self.position


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port',))
@dataclass(frozen=True, repr=False)
class CommandRequest(Message):
    port: int

    def __post_init__(self):
        # <default GSL customizable: CommandRequest-init-validation>
        pass
        # </GSL customizable: CommandRequest-init-validation>

    # <default GSL customizable: CommandRequest-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'position',))
@dataclass(frozen=True, repr=False)
class CommandReply(Message):
    port: int
    position: Optional[int]

    def __post_init__(self):
        # <default GSL customizable: CommandReply-init-validation>
        pass
        # </GSL customizable: CommandReply-init-validation>

    # <default GSL customizable: CommandReply-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.position is not None
        if self.position is not None:
            msg.position = self.position


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandSubscribe(Message):
    port: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: CommandSubscribe-init-validation>
        pass
        # </GSL customizable: CommandSubscribe-init-validation>

    # <default GSL customizable: CommandSubscribe-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'position', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandUpdate(Message):
    is_async = True

    port: int
    position: Optional[int]
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: CommandUpdate-init-validation>
        pass
        # </GSL customizable: CommandUpdate-init-validation>

    # <default GSL customizable: CommandUpdate-extra-members />

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.position is not None
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
        return CommandReply(port, position if active else None)
    else:
        return CommandUpdate(port, position if active else None, subscription)
    # </GSL customizable: _parse_servo_command_message_reply-return>
