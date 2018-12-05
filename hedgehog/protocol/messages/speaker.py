from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import speaker_pb2
from hedgehog.utils import protobuf

__all__ = ['Action']

# <default GSL customizable: module-header />


@RequestMsg.message(speaker_pb2.SpeakerAction, 'speaker_action', fields=('frequency',))
@dataclass(frozen=True, repr=False)
class Action(SimpleMessage):
    frequency: int

    def __post_init__(self):
        # <default GSL customizable: Action-init-validation>
        pass
        # </GSL customizable: Action-init-validation>

    # <default GSL customizable: Action-extra-members />

    @classmethod
    def _parse(cls, msg: speaker_pb2.SpeakerAction) -> 'Action':
        frequency = msg.frequency
        return cls(frequency)

    def _serialize(self, msg: speaker_pb2.SpeakerAction) -> None:
        msg.frequency = self.frequency
