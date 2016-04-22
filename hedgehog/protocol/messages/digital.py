import collections
from . import Message, register


@register
class Request(Message):
    _command_oneof = 'digital_request'

    def __init__(self, port):
        self.port = port

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port)

    def _serialize(self, msg):
        msg.port = self.port


@register
class Update(Message):
    _command_oneof = 'digital_update'

    def __init__(self, port, value):
        self.port = port
        self.value = value

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.value)

    def _serialize(self, msg):
        msg.port = self.port
        msg.value = self.value


@register
class StateAction(Message):
    _command_oneof = 'digital_state_action'

    def __init__(self, port, pullup, output):
        self.port = port
        self.pullup = pullup
        self.output = output

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.pullup, msg.output)

    def _serialize(self, msg):
        msg.port = self.port
        msg.pullup = self.pullup
        msg.output = self.output


@register
class Action(Message):
    _command_oneof = 'digital_action'

    def __init__(self, port, level):
        self.port = port
        self.level = level

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.level)

    def _serialize(self, msg):
        msg.port = self.port
        msg.level = self.level
