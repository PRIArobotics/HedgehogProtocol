from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import io_pb2
from hedgehog.utils import protobuf

__all__ = ['Request', 'Reply', 'Subscribe', 'Update']

# <GSL customizable: module-header>
from hedgehog.protocol.proto.subscription_pb2 import Subscription

__all__ += ['Subscription']
# </GSL customizable: module-header>


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port',))
@dataclass(frozen=True, repr=False)
class Request(Message):
    port: int

    def __post_init__(self):
        # <default GSL customizable: Request-init-validation>
        pass
        # </GSL customizable: Request-init-validation>

    # <default GSL customizable: Request-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value',))
@dataclass(frozen=True, repr=False)
class Reply(Message):
    port: int
    value: bool

    def __post_init__(self):
        # <default GSL customizable: Reply-init-validation>
        pass
        # </GSL customizable: Reply-init-validation>

    # <default GSL customizable: Reply-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'subscription',))
@dataclass(frozen=True, repr=False)
class Subscribe(Message):
    port: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: Subscribe-init-validation>
        pass
        # </GSL customizable: Subscribe-init-validation>

    # <default GSL customizable: Subscribe-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value', 'subscription',))
@dataclass(frozen=True, repr=False)
class Update(Message):
    is_async = True

    port: int
    value: bool
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: Update-init-validation>
        pass
        # </GSL customizable: Update-init-validation>

    # <default GSL customizable: Update-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('digital_message')
def _parse_digital_message_request(msg: io_pb2.DigitalMessage) -> Union[Request, Subscribe]:
    port = msg.port
    value = msg.value
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_digital_message_request-return>
    if subscription is None:
        return Request(port)
    else:
        return Subscribe(port, subscription)
    # </GSL customizable: _parse_digital_message_request-return>


@ReplyMsg.parser('digital_message')
def _parse_digital_message_reply(msg: io_pb2.DigitalMessage) -> Union[Reply, Update]:
    port = msg.port
    value = msg.value
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_digital_message_reply-return>
    if subscription is None:
        return Reply(port, value)
    else:
        return Update(port, value, subscription)
    # </GSL customizable: _parse_digital_message_reply-return>
