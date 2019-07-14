from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import version_pb2
from hedgehog.utils import protobuf

__all__ = ['Request', 'Reply']

# <default GSL customizable: module-header />


@RequestMsg.message(version_pb2.VersionMessage, 'version_message', fields=())
@dataclass(frozen=True, repr=False)
class Request(SimpleMessage):

    def __post_init__(self):
        # <default GSL customizable: Request-init-validation>
        pass
        # </GSL customizable: Request-init-validation>

    # <default GSL customizable: Request-extra-members />

    @classmethod
    def _parse(cls, msg: version_pb2.VersionMessage) -> 'Request':
        return cls()

    def _serialize(self, msg: version_pb2.VersionMessage) -> None:
        msg.SetInParent()


@ReplyMsg.message(version_pb2.VersionMessage, 'version_message', fields=('uc_id', 'hardware_version', 'firmware_version', 'server_version',))
@dataclass(frozen=True, repr=False)
class Reply(SimpleMessage):
    uc_id: bytes
    hardware_version: str
    firmware_version: str
    server_version: str

    def __post_init__(self):
        # <default GSL customizable: Reply-init-validation>
        pass
        # </GSL customizable: Reply-init-validation>

    # <default GSL customizable: Reply-extra-members />

    @classmethod
    def _parse(cls, msg: version_pb2.VersionMessage) -> 'Reply':
        uc_id = msg.uc_id
        hardware_version = msg.hardware_version
        firmware_version = msg.firmware_version
        server_version = msg.server_version
        return cls(uc_id, hardware_version, firmware_version, server_version)

    def _serialize(self, msg: version_pb2.VersionMessage) -> None:
        msg.uc_id = self.uc_id
        msg.hardware_version = self.hardware_version
        msg.firmware_version = self.firmware_version
        msg.server_version = self.server_version
