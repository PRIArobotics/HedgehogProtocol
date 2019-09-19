from typing import Any, Dict, Optional, Set, Tuple, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import vision_pb2
from hedgehog.utils import protobuf

__all__ = ['OpenCameraAction', 'CloseCameraAction', 'CreateChannelAction', 'UpdateChannelAction', 'DeleteChannelAction', 'ChannelRequest', 'ChannelReply', 'CaptureFrameAction', 'FrameRequest', 'FrameReply']

# <GSL customizable: module-header>
from hedgehog.protocol.proto.vision_pb2 import ChannelOperation
from hedgehog.protocol.proto.vision_pb2 import CREATE, READ, UPDATE, DELETE


@dataclass
class FacesChannel:
    @classmethod
    def _parse(cls, msg: vision_pb2.Channel) -> Tuple[str, 'FacesChannel']:
        return msg.key, cls()

    def _serialize(self, msg: vision_pb2.Channel, key: str) -> None:
        msg.key = key
        msg.faces.SetInParent()


@dataclass
class BlobsChannel:
    hsv_min: Tuple[int, int, int]
    hsv_max: Tuple[int, int, int]

    @staticmethod
    def _pack(hsv: Tuple[int, int, int]) -> int:
        return int.from_bytes(hsv, 'big')

    @staticmethod
    def _unpack(hsv: int) -> Tuple[int, int, int]:
        return tuple(hsv.to_bytes(3, 'big'))

    @classmethod
    def _parse(cls, msg: vision_pb2.Channel) -> Tuple[str, 'BlobsChannel']:
        hsv_min = BlobsChannel._unpack(msg.blobs.hsv_min)
        hsv_max = BlobsChannel._unpack(msg.blobs.hsv_max)
        return msg.key, cls(hsv_min, hsv_max)

    def _serialize(self, msg: vision_pb2.Channel, key: str) -> None:
        msg.key = key
        msg.blobs.hsv_min = BlobsChannel._pack(self.hsv_min)
        msg.blobs.hsv_max = BlobsChannel._pack(self.hsv_max)


Channel = Union[FacesChannel, BlobsChannel]


def _parse_channel(msg: vision_pb2.Channel) -> Tuple[str, Channel]:
    if msg.HasField('faces'):
        return FacesChannel._parse(msg)
    elif msg.HasField('blobs'):
        return BlobsChannel._parse(msg)
    else:  # pragma: nocover
        assert False


__all__ += [
    'ChannelOperation',
    'CREATE', 'READ', 'UPDATE', 'DELETE',
    'FacesChannel', 'BlobsChannel', 'Channel',
]
# </GSL customizable: module-header>


@protobuf.message(vision_pb2.VisionCameraAction, 'vision_camera_action', fields=())
@dataclass(frozen=True, repr=False)
class OpenCameraAction(Message):

    def __post_init__(self):
        # <default GSL customizable: OpenCameraAction-init-validation>
        pass
        # </GSL customizable: OpenCameraAction-init-validation>

    # <default GSL customizable: OpenCameraAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionCameraAction) -> None:
        msg.open = True


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


@protobuf.message(vision_pb2.VisionChannelMessage, 'vision_channel_message', fields=('channels',))
@dataclass(frozen=True, repr=False)
class CreateChannelAction(Message):
    channels: Dict[str, Channel]

    def __post_init__(self):
        # <default GSL customizable: CreateChannelAction-init-validation>
        pass
        # </GSL customizable: CreateChannelAction-init-validation>

    # <default GSL customizable: CreateChannelAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionChannelMessage) -> None:
        # <GSL customizable: CreateChannelAction-serialize-channels>
        msg.op = CREATE
        for key, channel in self.channels.items():
            channel._serialize(msg.channels.add(), key)
        # </GSL customizable: CreateChannelAction-serialize-channels>


@protobuf.message(vision_pb2.VisionChannelMessage, 'vision_channel_message', fields=('channels',))
@dataclass(frozen=True, repr=False)
class UpdateChannelAction(Message):
    channels: Dict[str, Channel]

    def __post_init__(self):
        # <default GSL customizable: UpdateChannelAction-init-validation>
        pass
        # </GSL customizable: UpdateChannelAction-init-validation>

    # <default GSL customizable: UpdateChannelAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionChannelMessage) -> None:
        # <GSL customizable: UpdateChannelAction-serialize-channels>
        msg.op = UPDATE
        for key, channel in self.channels.items():
            channel._serialize(msg.channels.add(), key)
        # </GSL customizable: UpdateChannelAction-serialize-channels>


@protobuf.message(vision_pb2.VisionChannelMessage, 'vision_channel_message', fields=('keys',))
@dataclass(frozen=True, repr=False)
class DeleteChannelAction(Message):
    keys: Set[str]

    def __post_init__(self):
        # <default GSL customizable: DeleteChannelAction-init-validation>
        pass
        # </GSL customizable: DeleteChannelAction-init-validation>

    # <default GSL customizable: DeleteChannelAction-extra-members />

    def _serialize(self, msg: vision_pb2.VisionChannelMessage) -> None:
        # <GSL customizable: DeleteChannelAction-serialize-keys>
        msg.op = DELETE
        for key in self.keys:
            msg.channels.add().key = key
        # </GSL customizable: DeleteChannelAction-serialize-keys>


@protobuf.message(vision_pb2.VisionChannelMessage, 'vision_channel_message', fields=('keys',))
@dataclass(frozen=True, repr=False)
class ChannelRequest(Message):
    keys: Set[str]

    def __post_init__(self):
        # <default GSL customizable: ChannelRequest-init-validation>
        pass
        # </GSL customizable: ChannelRequest-init-validation>

    # <default GSL customizable: ChannelRequest-extra-members />

    def _serialize(self, msg: vision_pb2.VisionChannelMessage) -> None:
        # <GSL customizable: ChannelRequest-serialize-keys>
        msg.op = READ
        for key in self.keys:
            msg.channels.add().key = key
        # </GSL customizable: ChannelRequest-serialize-keys>


@ReplyMsg.message(vision_pb2.VisionChannelMessage, 'vision_channel_message', fields=('channels',))
@dataclass(frozen=True, repr=False)
class ChannelReply(SimpleMessage):
    channels: Dict[str, Channel]

    def __post_init__(self):
        # <default GSL customizable: ChannelReply-init-validation>
        pass
        # </GSL customizable: ChannelReply-init-validation>

    # <default GSL customizable: ChannelReply-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionChannelMessage) -> 'ChannelReply':
        # <GSL customizable: ChannelReply-parse-channels>
        channels = {key: channel for key, channel in (_parse_channel(msg) for msg in msg.channels)}
        # </GSL customizable: ChannelReply-parse-channels>
        return cls(channels)

    def _serialize(self, msg: vision_pb2.VisionChannelMessage) -> None:
        # <GSL customizable: ChannelReply-serialize-channels>
        msg.op = READ
        for key, channel in self.channels.items():
            channel._serialize(msg.channels.add(), key)
        # </GSL customizable: ChannelReply-serialize-channels>


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
    highlight: Optional[str]

    def __post_init__(self):
        # <default GSL customizable: FrameRequest-init-validation>
        pass
        # </GSL customizable: FrameRequest-init-validation>

    # <default GSL customizable: FrameRequest-extra-members />

    @classmethod
    def _parse(cls, msg: vision_pb2.VisionFrameMessage) -> 'FrameRequest':
        highlight = msg.highlight
        return cls(highlight if highlight != '' else None)

    def _serialize(self, msg: vision_pb2.VisionFrameMessage) -> None:
        msg.highlight = self.highlight if self.highlight is not None else ''


@ReplyMsg.message(vision_pb2.VisionFrameMessage, 'vision_frame_message', fields=('highlight', 'frame',))
@dataclass(frozen=True, repr=False)
class FrameReply(SimpleMessage):
    highlight: Optional[str]
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
        return cls(highlight if highlight != '' else None, frame)

    def _serialize(self, msg: vision_pb2.VisionFrameMessage) -> None:
        msg.highlight = self.highlight if self.highlight is not None else ''
        msg.frame = self.frame


@RequestMsg.parser('vision_camera_action')
def _parse_vision_camera_action_request(msg: vision_pb2.VisionCameraAction) -> Union[OpenCameraAction, CloseCameraAction]:
    open = msg.open
    # <GSL customizable: _parse_vision_camera_action_request-return>
    if open:
        return OpenCameraAction()
    else:
        return CloseCameraAction()
    # </GSL customizable: _parse_vision_camera_action_request-return>


@RequestMsg.parser('vision_channel_message')
def _parse_vision_channel_message_request(msg: vision_pb2.VisionChannelMessage) -> Union[CreateChannelAction, UpdateChannelAction, DeleteChannelAction, ChannelRequest]:
    op = msg.op
    channels = msg.channels
    # <GSL customizable: _parse_vision_channel_message_request-return>
    if op in {READ, DELETE}:
        keys = {msg.key for msg in channels}
        if op == READ:
            return ChannelRequest(keys)
        else:
            return DeleteChannelAction(keys)
    elif op in {CREATE, UPDATE}:
        channels = {key: channel for key, channel in (_parse_channel(msg) for msg in msg.channels)}
        if op == CREATE:
            return CreateChannelAction(channels)
        else:
            return UpdateChannelAction(channels)
    else:  # pragma: nocover
        assert False
    # </GSL customizable: _parse_vision_channel_message_request-return>
