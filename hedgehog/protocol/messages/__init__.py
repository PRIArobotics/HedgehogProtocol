from hedgehog.utils import protobuf
from ..proto import hedgehog_pb2


RequestMsg = protobuf.ContainerMessage(hedgehog_pb2.HedgehogMessage)
ReplyMsg = protobuf.ContainerMessage(hedgehog_pb2.HedgehogMessage)


class Message(protobuf.Message):
    async = False


class SimpleMessage(Message, protobuf.SimpleMessageMixin):
    pass
