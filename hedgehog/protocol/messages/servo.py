from typing import Union

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import servo_pb2
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.utils import protobuf


@RequestMsg.message(servo_pb2.ServoAction, 'servo_action')
class Action(SimpleMessage):
    def __init__(self, port: int, active: bool, position: int=None) -> None:
        if active and position is None:
            raise InvalidCommandError("position must be given when activating servo")
        self.port = port
        self.active = active
        self.position = position if active else None

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
class CommandRequest(Message):
    def __init__(self, port: int) -> None:
        self.port = port

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'subscription'))
class CommandSubscribe(Message):
    def __init__(self, port: int, subscription: Subscription) -> None:
        self.port = port
        self.subscription = subscription

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('servo_command_message')
def _parse_command_request(msg: servo_pb2.ServoCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port', 'active', 'position'))
class CommandReply(Message):
    def __init__(self, port: int, active: bool, position: int) -> None:
        self.port = port
        self.active = active
        self.position = position if active else None

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.active
        if self.position is not None:
            msg.position = self.position


@protobuf.message(servo_pb2.ServoCommandMessage, 'servo_command_message')
class CommandUpdate(Message):
    is_async = True

    def __init__(self, port: int, active: bool, position: int, subscription: Subscription) -> None:
        self.port = port
        self.active = active
        self.position = position if active else None
        self.subscription = subscription

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.active
        if self.position is not None:
            msg.position = self.position
        msg.subscription.CopyFrom(self.subscription)


@ReplyMsg.parser('servo_command_message')
def _parse_command_reply(msg: servo_pb2.ServoCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    active = msg.active
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return CommandReply(port, active, position)
    else:
        return CommandUpdate(port, active, position, subscription)
