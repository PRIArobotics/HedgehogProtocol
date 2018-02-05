from typing import Union

from . import RequestMsg, ReplyMsg, Message
from hedgehog.protocol.proto import io_pb2
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.utils import protobuf


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port',))
class Request(Message):
    def __init__(self, port: int) -> None:
        self.port = port

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'subscription'))
class Subscribe(Message):
    def __init__(self, port: int, subscription: Subscription) -> None:
        self.port = port
        self.subscription = subscription

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('digital_message')
def _parse_request(msg: io_pb2.DigitalMessage) -> Union[Request, Subscribe]:
    port = msg.port
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return Request(port)
    else:
        return Subscribe(port, subscription)


@protobuf.message(io_pb2.DigitalMessage, 'digital_message', fields=('port', 'value'))
class Reply(Message):
    def __init__(self, port: int, value: bool) -> None:
        self.port = port
        self.value = value

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value


@protobuf.message(io_pb2.DigitalMessage, 'digital_message')
class Update(Message):
    is_async = True

    def __init__(self, port: int, value: bool, subscription: Subscription) -> None:
        self.port = port
        self.value = value
        self.subscription = subscription

    def _serialize(self, msg: io_pb2.DigitalMessage) -> None:
        msg.port = self.port
        msg.value = self.value
        msg.subscription.CopyFrom(self.subscription)


@ReplyMsg.parser('digital_message')
def _parse_reply(msg: io_pb2.DigitalMessage) -> Union[Reply, Update]:
    port = msg.port
    value = msg.value
    subscription = msg.subscription if msg.HasField('subscription') else None
    if subscription is None:
        return Reply(port, value)
    else:
        return Update(port, value, subscription)
