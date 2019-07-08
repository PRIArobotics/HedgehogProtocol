from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import emergency_pb2
from hedgehog.utils import protobuf

__all__ = ['ReleaseAction']

# <default GSL customizable: module-header />


@RequestMsg.message(emergency_pb2.ReleaseAction, 'emergency_release', fields=())
@dataclass(frozen=True, repr=False)
class ReleaseAction(SimpleMessage):

    def __post_init__(self):
        # <default GSL customizable: ReleaseAction-init-validation>
        pass
        # </GSL customizable: ReleaseAction-init-validation>

    # <default GSL customizable: ReleaseAction-extra-members />

    @classmethod
    def _parse(cls, msg: emergency_pb2.ReleaseAction) -> 'ReleaseAction':
        return cls()

    def _serialize(self, msg: emergency_pb2.ReleaseAction) -> None:
        msg.SetInParent()
