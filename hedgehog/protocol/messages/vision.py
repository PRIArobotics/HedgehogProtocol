from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import vision_pb2
from hedgehog.utils import protobuf

__all__ = ['CameraAction', 'ReadFrameAction']

# <default GSL customizable: module-header />


@RequestMsg.message(vision_pb2.CameraAction, 'camera_action', fields=('open',))
@dataclass(frozen=True, repr=False)
class CameraAction(SimpleMessage):
    open: bool

    def __post_init__(self):
        # <default GSL customizable: CameraAction-init-validation>
        pass
        # </GSL customizable: CameraAction-init-validation>

    # <default GSL customizable: CameraAction-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.CameraAction) -> 'CameraAction':
        open = msg.open
        return cls(open)

    def _serialize(self, msg: vision_pb2.CameraAction) -> None:
        msg.open = self.open


@RequestMsg.message(vision_pb2.ReadFrameAction, 'read_frame_action', fields=())
@dataclass(frozen=True, repr=False)
class ReadFrameAction(SimpleMessage):

    def __post_init__(self):
        # <default GSL customizable: ReadFrameAction-init-validation>
        pass
        # </GSL customizable: ReadFrameAction-init-validation>

    # <default GSL customizable: ReadFrameAction-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.ReadFrameAction) -> 'ReadFrameAction':
        return cls()

    def _serialize(self, msg: vision_pb2.ReadFrameAction) -> None:
        msg.SetInParent()
