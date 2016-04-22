import collections
from . import Message, register


@register
class Request(Message):
    _command_oneof = 'analog_request'

    def __init__(self, port):
        self.port = port

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port)

    def _serialize(self, msg):
        msg.port = self.port


@register
class Update(Message):
    _command_oneof = 'analog_update'

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
    _command_oneof = 'analog_state_action'

    def __init__(self, port, pullup):
        self.port = port
        self.pullup = pullup

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.pullup)

    def _serialize(self, msg):
        msg.port = self.port
        msg.pullup = self.pullup
