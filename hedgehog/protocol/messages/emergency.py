from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import emergency_pb2
from hedgehog.utils import protobuf

__all__ = ['Action', 'Request', 'Reply', 'Subscribe', 'Update']

# <GSL customizable: module-header>
from hedgehog.protocol.proto.subscription_pb2 import Subscription
# </GSL customizable: module-header>


@RequestMsg.message(emergency_pb2.EmergencyAction, 'emergency_action', fields=('activate',))
@dataclass(frozen=True, repr=False)
class Action(SimpleMessage):
    activate: bool

    def __post_init__(self):
        # <default GSL customizable: Action-init-validation>
        pass
        # </GSL customizable: Action-init-validation>

    # <default GSL customizable: Action-extra-members />

    @classmethod
    def _parse(cls, msg: emergency_pb2.EmergencyAction) -> 'Action':
        activate = msg.activate
        return cls(activate)

    def _serialize(self, msg: emergency_pb2.EmergencyAction) -> None:
        msg.activate = self.activate


@protobuf.message(emergency_pb2.EmergencyMessage, 'emergency_message', fields=())
@dataclass(frozen=True, repr=False)
class Request(Message):

    def __post_init__(self):
        # <default GSL customizable: Request-init-validation>
        pass
        # </GSL customizable: Request-init-validation>

    # <default GSL customizable: Request-extra-members />

    def _serialize(self, msg: emergency_pb2.EmergencyMessage) -> None:
        msg.SetInParent()


@protobuf.message(emergency_pb2.EmergencyMessage, 'emergency_message', fields=('active',))
@dataclass(frozen=True, repr=False)
class Reply(Message):
    active: bool

    def __post_init__(self):
        # <default GSL customizable: Reply-init-validation>
        pass
        # </GSL customizable: Reply-init-validation>

    # <default GSL customizable: Reply-extra-members />

    def _serialize(self, msg: emergency_pb2.EmergencyMessage) -> None:
        msg.active = self.active


@protobuf.message(emergency_pb2.EmergencyMessage, 'emergency_message', fields=('subscription',))
@dataclass(frozen=True, repr=False)
class Subscribe(Message):
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: Subscribe-init-validation>
        pass
        # </GSL customizable: Subscribe-init-validation>

    # <default GSL customizable: Subscribe-extra-members />

    def _serialize(self, msg: emergency_pb2.EmergencyMessage) -> None:
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(emergency_pb2.EmergencyMessage, 'emergency_message', fields=('active', 'subscription',))
@dataclass(frozen=True, repr=False)
class Update(Message):
    is_async = True

    active: bool
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: Update-init-validation>
        pass
        # </GSL customizable: Update-init-validation>

    # <default GSL customizable: Update-extra-members />

    def _serialize(self, msg: emergency_pb2.EmergencyMessage) -> None:
        msg.active = self.active
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('emergency_message')
def _parse_emergency_message_request(msg: emergency_pb2.EmergencyMessage) -> Union[Request, Subscribe]:
    active = msg.active
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_emergency_message_request-return>
    if subscription is None:
        return Request()
    else:
        return Subscribe(subscription)
    # </GSL customizable: _parse_emergency_message_request-return>


@ReplyMsg.parser('emergency_message')
def _parse_emergency_message_reply(msg: emergency_pb2.EmergencyMessage) -> Union[Reply, Update]:
    active = msg.active
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_emergency_message_reply-return>
    if subscription is None:
        return Reply(active)
    else:
        return Update(active, subscription)
    # </GSL customizable: _parse_emergency_message_reply-return>
