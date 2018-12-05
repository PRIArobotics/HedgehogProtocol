from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import io_pb2
from hedgehog.utils import protobuf

__all__ = ['Action', 'CommandRequest', 'CommandReply', 'CommandSubscribe', 'CommandUpdate']

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.io_pb2 import INPUT_FLOATING, INPUT_PULLUP, INPUT_PULLDOWN
from hedgehog.protocol.proto.io_pb2 import OUTPUT_OFF, OUTPUT_ON
from hedgehog.protocol.proto.io_pb2 import OUTPUT, PULLUP, PULLDOWN, LEVEL
from hedgehog.protocol.proto.subscription_pb2 import Subscription

__all__ += [
    'INPUT_FLOATING', 'INPUT_PULLUP', 'INPUT_PULLDOWN',
    'OUTPUT_OFF', 'OUTPUT_ON',
    'OUTPUT', 'PULLUP', 'PULLDOWN', 'LEVEL',
    'Subscription',
]


def _check_flags(flags: int) -> None:
    if flags & OUTPUT and flags & (PULLUP | PULLDOWN):
        raise InvalidCommandError("only input ports can be set to pullup or pulldown")
    if not flags & OUTPUT and flags & LEVEL:
        raise InvalidCommandError("only output ports can be set to on")
    if flags & PULLUP and flags & PULLDOWN:
        raise InvalidCommandError("pullup and pulldown are mutually exclusive")
# </GSL customizable: module-header>


@RequestMsg.message(io_pb2.IOAction, 'io_action', fields=('port', 'flags',))
@dataclass(frozen=True, repr=False)
class Action(SimpleMessage):
    port: int
    flags: int

    def __post_init__(self):
        # <GSL customizable: Action-init-validation>
        _check_flags(self.flags)
        # </GSL customizable: Action-init-validation>

    # <GSL customizable: Action-extra-members>
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
    # </GSL customizable: Action-extra-members>

    @classmethod
    def _parse(cls, msg: io_pb2.IOAction) -> 'Action':
        port = msg.port
        flags = msg.flags
        return cls(port, flags)

    def _serialize(self, msg: io_pb2.IOAction) -> None:
        msg.port = self.port
        msg.flags = self.flags


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port',))
@dataclass(frozen=True, repr=False)
class CommandRequest(Message):
    port: int

    def __post_init__(self):
        # <default GSL customizable: CommandRequest-init-validation>
        pass
        # </GSL customizable: CommandRequest-init-validation>

    # <default GSL customizable: CommandRequest-extra-members />

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port', 'flags',))
@dataclass(frozen=True, repr=False)
class CommandReply(Message):
    port: int
    flags: int

    def __post_init__(self):
        # <GSL customizable: CommandReply-init-validation>
        _check_flags(self.flags)
        # </GSL customizable: CommandReply-init-validation>

    # <GSL customizable: CommandReply-extra-members>
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
    # </GSL customizable: CommandReply-extra-members>

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.flags = self.flags


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandSubscribe(Message):
    port: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: CommandSubscribe-init-validation>
        pass
        # </GSL customizable: CommandSubscribe-init-validation>

    # <default GSL customizable: CommandSubscribe-extra-members />

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port', 'flags', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandUpdate(Message):
    is_async = True

    port: int
    flags: int
    subscription: Subscription

    def __post_init__(self):
        # <GSL customizable: CommandUpdate-init-validation>
        _check_flags(self.flags)
        # </GSL customizable: CommandUpdate-init-validation>

    # <GSL customizable: CommandUpdate-extra-members>
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
    # </GSL customizable: CommandUpdate-extra-members>

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.flags = self.flags
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('io_command_message')
def _parse_io_command_message_request(msg: io_pb2.IOCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    flags = msg.flags
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_io_command_message_request-return>
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)
    # </GSL customizable: _parse_io_command_message_request-return>


@ReplyMsg.parser('io_command_message')
def _parse_io_command_message_reply(msg: io_pb2.IOCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    flags = msg.flags
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_io_command_message_reply-return>
    if subscription is None:
        return CommandReply(port, flags)
    else:
        return CommandUpdate(port, flags, subscription)
    # </GSL customizable: _parse_io_command_message_reply-return>
