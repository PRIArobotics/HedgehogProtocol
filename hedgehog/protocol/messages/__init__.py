import collections
from hedgehog.protocol.errors import UnknownCommandError
from hedgehog.protocol.proto.hedgehog_pb2 import HedgehogMessage


registry = {}


def register(class_):
    registry[class_._command_oneof] = class_
    return class_


def parse(data):
    msg = HedgehogMessage()
    msg.ParseFromString(data)
    key = msg.WhichOneof('command')
    try:
        msg_type = registry[key]
    except KeyError as err:
        raise UnknownCommandError(key)
    else:
        return msg_type.parse(msg)


class Message:
    _command_oneof = None
    name = None
    fields = None
    async = False

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
        msg = HedgehogMessage()
        self._serialize(self._get_oneof(msg))
        return msg.SerializeToString()

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        for field in self.fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    def __repr__(self):
        field_reprs = ('{}={}'.format(field, repr(getattr(self, field))) for field in self.fields)
        return '{}({})'.format(self.name, ', '.join(field_reprs))
