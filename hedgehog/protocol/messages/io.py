from typing import Union

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import io_pb2
from hedgehog.protocol.proto.io_pb2 import INPUT_FLOATING, INPUT_PULLUP, INPUT_PULLDOWN
from hedgehog.protocol.proto.io_pb2 import OUTPUT_OFF, OUTPUT_ON
from hedgehog.protocol.proto.io_pb2 import OUTPUT, PULLUP, PULLDOWN, LEVEL
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.utils import protobuf


def _check_flags(flags: int) -> None:
    if flags & OUTPUT and flags & (PULLUP | PULLDOWN):
        raise InvalidCommandError("only input ports can be set to pullup or pulldown")
    if not flags & OUTPUT and flags & LEVEL:
        raise InvalidCommandError("only output ports can be set to on")
    if flags & PULLUP and flags & PULLDOWN:
        raise InvalidCommandError("pullup and pulldown are mutually exclusive")


@RequestMsg.message(io_pb2.IOAction, 'io_action')
class Action(SimpleMessage):
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
    def _parse(cls, msg: io_pb2.IOAction) -> 'Action':
        port = msg.port
        flags = msg.flags
        return cls(port, flags)

    def _serialize(self, msg: io_pb2.IOAction) -> None:
        msg.port = self.port
        msg.flags = self.flags


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port',))
class CommandRequest(Message):
    def __init__(self, port: int) -> None:
        self.port = port

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port', 'subscription'))
class CommandSubscribe(Message):
    def __init__(self, port: int, subscription: Subscription) -> None:
        self.port = port
        self.subscription = subscription

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('io_command_message')
def _parse_command_request(msg: io_pb2.IOCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message', fields=('port', 'flags'))
class CommandReply(Message):
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

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.flags = self.flags


@protobuf.message(io_pb2.IOCommandMessage, 'io_command_message')
class CommandUpdate(Message):
    is_async = True

    def __init__(self, port: int, flags: int, subscription: Subscription) -> None:
        _check_flags(flags)
        self.port = port
        self.flags = flags
        self.subscription = subscription

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

    def _serialize(self, msg: io_pb2.IOCommandMessage) -> None:
        msg.port = self.port
        msg.flags = self.flags
        msg.subscription.CopyFrom(self.subscription)


@ReplyMsg.parser('io_command_message')
def _parse_command_reply(msg: io_pb2.IOCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    flags = msg.flags
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandReply(port, flags)
    else:
        return CommandUpdate(port, flags, subscription)
