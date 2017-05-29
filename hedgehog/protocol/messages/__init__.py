from hedgehog.utils import protobuf
from ..proto import hedgehog_pb2


RequestMsg = protobuf.ContainerMessage(hedgehog_pb2.HedgehogMessage)
ReplyMsg = protobuf.ContainerMessage(hedgehog_pb2.HedgehogMessage)


class Message(protobuf.Message):
    async = False

    @classmethod
    def msg_name(cls):
        module, name = cls.__module__, cls.__name__
        module = module[module.rindex('.') + 1:]
        return module + '.' + name

    def __repr__(self):
        field_pairs = ((field, getattr(self, field)) for field in self.meta.fields)
        field_reprs = ('{}={}'.format(field, repr(value)) for field, value in field_pairs)
        return '{}({})'.format(self.msg_name(), ', '.join(field_reprs))


class SimpleMessage(Message, protobuf.SimpleMessageMixin):
    pass
