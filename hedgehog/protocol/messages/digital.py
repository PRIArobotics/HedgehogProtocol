from typing import Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import io_pb2
from hedgehog.utils import protobuf

# <GSL customizable: module-header>
from hedgehog.protocol.proto.subscription_pb2 import Subscription
# </GSL customizable: module-header>


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port',))
@dataclass(frozen=True)
class Request(Message):
    port: int

    def __init__(self, port: int) -> None:
        # <default GSL customizable: Request-init-validation />
        object.__setattr__(self, 'port', port)

    # <default GSL customizable: Request-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value',))
@dataclass(frozen=True)
class Reply(Message):
    port: int
    value: bool

    def __init__(self, port: int, value: bool) -> None:
        # <default GSL customizable: Reply-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'value', value)

    # <default GSL customizable: Reply-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'subscription',))
@dataclass(frozen=True)
class Subscribe(Message):
    port: int
    subscription: Subscription

    def __init__(self, port: int, subscription: Subscription) -> None:
        # <default GSL customizable: Subscribe-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'subscription', subscription)

    # <default GSL customizable: Subscribe-extra-members />

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value', 'subscription',))
@dataclass(frozen=True)
class Update(Message):
    is_async = True

    port: int
    value: bool
    subscription: Subscription

    def __init__(self, port: int, value: bool, subscription: Subscription) -> None:
        # <default GSL customizable: Update-init-validation />
        object.__setattr__(self, 'port', port)
        object.__setattr__(self, 'value', value)
        object.__setattr__(self, 'subscription', subscription)

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
