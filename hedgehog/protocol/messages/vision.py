from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import vision_pb2
from hedgehog.utils import protobuf

__all__ = ['CameraAction', 'RetrieveFrameAction']

# <GSL customizable: module-header>
from typing import Tuple


@dataclass
class FacesChannel:
    @classmethod
    def _parse(cls, msg: vision_pb2.Channel) -> 'FacesChannel':
        return cls()

    def _serialize(self, msg: vision_pb2.Channel) -> None:
        msg.faces.SetInParent()


@dataclass
class ContoursChannel:
    hsv_min: Tuple[int, int, int]
    hsv_max: Tuple[int, int, int]

    @staticmethod
    def _pack(hsv: Tuple[int, int, int]) -> int:
        return int.from_bytes(hsv, 'big')

    @staticmethod
    def _unpack(hsv: int) -> Tuple[int, int, int]:
        return tuple(hsv.to_bytes(3, 'big'))

    @classmethod
    def _parse(cls, msg: vision_pb2.Channel) -> 'ContoursChannel':
        hsv_min = ContoursChannel._unpack(msg.contours.hsv_min)
        hsv_max = ContoursChannel._unpack(msg.contours.hsv_max)
        return cls(hsv_min, hsv_max)

    def _serialize(self, msg: vision_pb2.Channel) -> None:
        msg.contours.hsv_min = ContoursChannel._pack(self.hsv_min)
        msg.contours.hsv_max = ContoursChannel._pack(self.hsv_max)


Channel = Union[FacesChannel, ContoursChannel]


__all__ += ['FacesChannel', 'ContoursChannel', 'Channel']
# </GSL customizable: module-header>


@RequestMsg.message(vision_pb2.VisionCameraAction, 'vision_camera_action', fields=('open', 'channels',))
@dataclass(frozen=True, repr=False)
class CameraAction(SimpleMessage):
    open: bool
    channels: Sequence[Channel]

    def __init__(self, open: bool, *channels: Channel) -> None:
        object.__setattr__(self, 'open', open)
        object.__setattr__(self, 'channels', channels)
        self.__post_init__()

    def __post_init__(self):
        # <default GSL customizable: CameraAction-init-validation>
        pass
        # </GSL customizable: CameraAction-init-validation>

    # <GSL customizable: CameraAction-extra-members>
    @staticmethod
    def _parse_channel(msg: vision_pb2.Channel) -> Channel:
        if msg.HasField('faces'):
            return FacesChannel._parse(msg)
        elif msg.HasField('contours'):
            return ContoursChannel._parse(msg)
        else:  # pragma: nocover
            assert False
    # </GSL customizable: CameraAction-extra-members>

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionCameraAction) -> 'CameraAction':
        open = msg.open
        channels = (CameraAction._parse_channel(channel) for channel in msg.channels)
        return cls(open, *channels)

    def _serialize(self, msg: vision_pb2.VisionCameraAction) -> None:
        msg.open = self.open
        for channel in self.channels:
            channel._serialize(msg.channels.add())


@RequestMsg.message(vision_pb2.VisionRetrieveFrameAction, 'vision_retrieve_frame_action', fields=())
@dataclass(frozen=True, repr=False)
class RetrieveFrameAction(SimpleMessage):

    def __post_init__(self):
        # <default GSL customizable: RetrieveFrameAction-init-validation>
        pass
        # </GSL customizable: RetrieveFrameAction-init-validation>

    # <default GSL customizable: RetrieveFrameAction-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionRetrieveFrameAction) -> 'RetrieveFrameAction':
        return cls()

    def _serialize(self, msg: vision_pb2.VisionRetrieveFrameAction) -> None:
        msg.SetInParent()
