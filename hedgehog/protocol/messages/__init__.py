import collections
import hedgehog.protocol.proto.hedgehog_pb2


registry = {}


def register(class_):
    registry[class_._command_oneof] = class_
    return class_


def parse(msg):
    return registry[msg.WhichOneof('command')].parse(msg)


class Message:
    _command_oneof = None

    @classmethod
    def _get_oneof(cls, msg):
        return getattr(msg, cls._command_oneof)

    @classmethod
    def _parse(cls, msg):
        raise NotImplementedError

    def _serialize(self, msg):
        raise NotImplementedError

    @classmethod
    def parse(cls, msg):
        return cls._parse(cls._get_oneof(msg))

    def serialize(self):
        msg = hedgehog.protocol.proto.hedgehog_pb2.HedgehogMessage()
        self._serialize(self._get_oneof(msg))
        return msg
