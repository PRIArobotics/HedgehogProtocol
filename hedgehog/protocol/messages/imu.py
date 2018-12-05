from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import imu_pb2
from hedgehog.utils import protobuf

__all__ = ['RateRequest', 'RateReply', 'RateSubscribe', 'RateUpdate', 'AccelerationRequest', 'AccelerationReply', 'AccelerationSubscribe', 'AccelerationUpdate', 'PoseRequest', 'PoseReply', 'PoseSubscribe', 'PoseUpdate']

# <GSL customizable: module-header>
from hedgehog.protocol.proto.imu_pb2 import RATE, ACCELERATION, POSE
from hedgehog.protocol.proto.subscription_pb2 import Subscription

__all__ += [
    'RATE', 'ACCELERATION', 'POSE',
    'Subscription',
]
# </GSL customizable: module-header>


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=())
@dataclass(frozen=True, repr=False)
class RateRequest(Message):

    def __post_init__(self):
        # <default GSL customizable: RateRequest-init-validation>
        pass
        # </GSL customizable: RateRequest-init-validation>

    # <default GSL customizable: RateRequest-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = RATE


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z',))
@dataclass(frozen=True, repr=False)
class RateReply(Message):
    x: int
    y: int
    z: int

    def __post_init__(self):
        # <default GSL customizable: RateReply-init-validation>
        pass
        # </GSL customizable: RateReply-init-validation>

    # <default GSL customizable: RateReply-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = RATE
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('subscription',))
@dataclass(frozen=True, repr=False)
class RateSubscribe(Message):
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: RateSubscribe-init-validation>
        pass
        # </GSL customizable: RateSubscribe-init-validation>

    # <default GSL customizable: RateSubscribe-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = RATE
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z', 'subscription',))
@dataclass(frozen=True, repr=False)
class RateUpdate(Message):
    is_async = True

    x: int
    y: int
    z: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: RateUpdate-init-validation>
        pass
        # </GSL customizable: RateUpdate-init-validation>

    # <default GSL customizable: RateUpdate-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = RATE
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=())
@dataclass(frozen=True, repr=False)
class AccelerationRequest(Message):

    def __post_init__(self):
        # <default GSL customizable: AccelerationRequest-init-validation>
        pass
        # </GSL customizable: AccelerationRequest-init-validation>

    # <default GSL customizable: AccelerationRequest-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = ACCELERATION


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z',))
@dataclass(frozen=True, repr=False)
class AccelerationReply(Message):
    x: int
    y: int
    z: int

    def __post_init__(self):
        # <default GSL customizable: AccelerationReply-init-validation>
        pass
        # </GSL customizable: AccelerationReply-init-validation>

    # <default GSL customizable: AccelerationReply-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = ACCELERATION
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('subscription',))
@dataclass(frozen=True, repr=False)
class AccelerationSubscribe(Message):
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: AccelerationSubscribe-init-validation>
        pass
        # </GSL customizable: AccelerationSubscribe-init-validation>

    # <default GSL customizable: AccelerationSubscribe-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = ACCELERATION
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z', 'subscription',))
@dataclass(frozen=True, repr=False)
class AccelerationUpdate(Message):
    is_async = True

    x: int
    y: int
    z: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: AccelerationUpdate-init-validation>
        pass
        # </GSL customizable: AccelerationUpdate-init-validation>

    # <default GSL customizable: AccelerationUpdate-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = ACCELERATION
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=())
@dataclass(frozen=True, repr=False)
class PoseRequest(Message):

    def __post_init__(self):
        # <default GSL customizable: PoseRequest-init-validation>
        pass
        # </GSL customizable: PoseRequest-init-validation>

    # <default GSL customizable: PoseRequest-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = POSE


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z',))
@dataclass(frozen=True, repr=False)
class PoseReply(Message):
    x: int
    y: int
    z: int

    def __post_init__(self):
        # <default GSL customizable: PoseReply-init-validation>
        pass
        # </GSL customizable: PoseReply-init-validation>

    # <default GSL customizable: PoseReply-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = POSE
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('subscription',))
@dataclass(frozen=True, repr=False)
class PoseSubscribe(Message):
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: PoseSubscribe-init-validation>
        pass
        # </GSL customizable: PoseSubscribe-init-validation>

    # <default GSL customizable: PoseSubscribe-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = POSE
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(imu_pb2.ImuMessage, 'imu_message', fields=('x', 'y', 'z', 'subscription',))
@dataclass(frozen=True, repr=False)
class PoseUpdate(Message):
    is_async = True

    x: int
    y: int
    z: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: PoseUpdate-init-validation>
        pass
        # </GSL customizable: PoseUpdate-init-validation>

    # <default GSL customizable: PoseUpdate-extra-members />

    def _serialize(self, msg: imu_pb2.ImuMessage) -> None:
        msg.kind = POSE
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.parser('imu_message')
def _parse_imu_message_request(msg: imu_pb2.ImuMessage) -> Union[RateRequest, RateSubscribe, AccelerationRequest, AccelerationSubscribe, PoseRequest, PoseSubscribe]:
    kind = msg.kind
    x = msg.x
    y = msg.y
    z = msg.z
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_imu_message_request-return>
    if not subscription:
        class_ = {
            RATE: RateRequest,
            ACCELERATION: AccelerationRequest,
            POSE: PoseRequest,
        }[kind]
        return class_()
    else:
        class_ = {
            RATE: RateSubscribe,
            ACCELERATION: AccelerationSubscribe,
            POSE: PoseSubscribe,
        }[kind]
        return class_(subscription)
    # </GSL customizable: _parse_imu_message_request-return>


@ReplyMsg.parser('imu_message')
def _parse_imu_message_reply(msg: imu_pb2.ImuMessage) -> Union[RateReply, RateUpdate, AccelerationReply, AccelerationUpdate, PoseReply, PoseUpdate]:
    kind = msg.kind
    x = msg.x
    y = msg.y
    z = msg.z
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_imu_message_reply-return>
    if not subscription:
        class_ = {
            RATE: RateReply,
            ACCELERATION: AccelerationReply,
            POSE: PoseReply,
        }[kind]
        return class_(x, y, z)
    else:
        class_ = {
            RATE: RateUpdate,
            ACCELERATION: AccelerationUpdate,
            POSE: PoseUpdate,
        }[kind]
        return class_(x, y, z, subscription)
    # </GSL customizable: _parse_imu_message_reply-return>
