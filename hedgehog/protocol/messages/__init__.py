from typing import cast

from hedgehog.utils import protobuf
from ..proto import hedgehog_pb2

__all__ = ['Message', 'SimpleMessage', 'ContainerMessage', 'RequestMsg', 'ReplyMsg']


class Message(protobuf.Message):
    is_async = False

    @classmethod
    def msg_name(cls):
        module, name = cls.__module__, cls.__name__
        module = module[module.rindex('.') + 1:]
        return f'{module}.{name}'

    def __repr__(self):
        field_pairs = ((field, getattr(self, field)) for field in self.meta.fields)
        field_reprs = ', '.join(f'{field}={value!r}' for field, value in field_pairs)
        return f'{self.msg_name()}({field_reprs})'


class SimpleMessage(Message, protobuf.SimpleMessageMixin):
    pass


class ContainerMessage(protobuf.ContainerMessage):
    def parse(self, data: bytes) -> Message:
        return cast(Message, super(ContainerMessage, self).parse(data))


RequestMsg = ContainerMessage(hedgehog_pb2.HedgehogMessage)
ReplyMsg = ContainerMessage(hedgehog_pb2.HedgehogMessage)
