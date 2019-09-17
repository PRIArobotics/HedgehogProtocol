from typing import Any, Optional, Sequence, Tuple, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import vision_pb2
from hedgehog.utils import protobuf

__all__ = ['OpenCameraAction', 'CloseCameraAction', 'CaptureFrameAction', 'FrameRequest', 'FrameReply']

# <GSL customizable: module-header>
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


def _parse_channel(msg: vision_pb2.Channel) -> Channel:
    if msg.HasField('faces'):
        return FacesChannel._parse(msg)
    elif msg.HasField('contours'):
        return ContoursChannel._parse(msg)
    else:  # pragma: nocover
        assert False


__all__ += ['FacesChannel', 'ContoursChannel', 'Channel']
# </GSL customizable: module-header>


@protobuf.message(vision_pb2.VisionCameraAction, 'vision_camera_action', fields=('channels',))
@dataclass(frozen=True, repr=False)
class OpenCameraAction(Message):
    channels: Sequence[Channel]

    def __init__(self, *channels: Channel) -> None:
        object.__setattr__(self, 'channels', channels)
        self.__post_init__()

    def __post_init__(self):
        # <default GSL customizable: OpenCameraAction-init-validation>
        pass
        # </GSL customizable: OpenCameraAction-init-validation>

    # <default GSL customizable: OpenCameraAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionCameraAction) -> None:
        msg.open = True
        for channel in self.channels:
            channel._serialize(msg.channels.add())


@protobuf.message(vision_pb2.VisionCameraAction, 'vision_camera_action', fields=())
@dataclass(frozen=True, repr=False)
class CloseCameraAction(Message):

    def __post_init__(self):
        # <default GSL customizable: CloseCameraAction-init-validation>
        pass
        # </GSL customizable: CloseCameraAction-init-validation>

    # <default GSL customizable: CloseCameraAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionCameraAction) -> None:
        msg.open = False


@RequestMsg.message(vision_pb2.VisionCaptureFrameAction, 'vision_capture_frame_action', fields=())
@dataclass(frozen=True, repr=False)
class CaptureFrameAction(SimpleMessage):

    def __post_init__(self):
        # <default GSL customizable: CaptureFrameAction-init-validation>
        pass
        # </GSL customizable: CaptureFrameAction-init-validation>

    # <default GSL customizable: CaptureFrameAction-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionCaptureFrameAction) -> 'CaptureFrameAction':
        return cls()

    def _serialize(self, msg: vision_pb2.VisionCaptureFrameAction) -> None:
        msg.SetInParent()


@RequestMsg.message(vision_pb2.VisionFrameMessage, 'vision_frame_message', fields=('highlight',))
@dataclass(frozen=True, repr=False)
class FrameRequest(SimpleMessage):
    highlight: Optional[int]

    def __post_init__(self):
        # <default GSL customizable: FrameRequest-init-validation>
        pass
        # </GSL customizable: FrameRequest-init-validation>

    # <default GSL customizable: FrameRequest-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionFrameMessage) -> 'FrameRequest':
        highlight = msg.highlight
        return cls(highlight if highlight != -1 else None)

    def _serialize(self, msg: vision_pb2.VisionFrameMessage) -> None:
        msg.highlight = self.highlight if self.highlight is not None else -1


@ReplyMsg.message(vision_pb2.VisionFrameMessage, 'vision_frame_message', fields=('highlight', 'frame',))
@dataclass(frozen=True, repr=False)
class FrameReply(SimpleMessage):
    highlight: Optional[int]
    frame: bytes

    def __post_init__(self):
        # <default GSL customizable: FrameReply-init-validation>
        pass
        # </GSL customizable: FrameReply-init-validation>

    # <default GSL customizable: FrameReply-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionFrameMessage) -> 'FrameReply':
        highlight = msg.highlight
        frame = msg.frame
        return cls(highlight if highlight != -1 else None, frame)

    def _serialize(self, msg: vision_pb2.VisionFrameMessage) -> None:
        msg.highlight = self.highlight if self.highlight is not None else -1
        msg.frame = self.frame


@RequestMsg.parser('vision_camera_action')
def _parse_vision_camera_action_request(msg: vision_pb2.VisionCameraAction) -> Union[OpenCameraAction, CloseCameraAction]:
    open = msg.open
    channels = msg.channels
    # <GSL customizable: _parse_vision_camera_action_request-return>
    if open:
        channels = (_parse_channel(channel) for channel in channels)
        return OpenCameraAction(*channels)
    else:
        return CloseCameraAction()
    # </GSL customizable: _parse_vision_camera_action_request-return>
