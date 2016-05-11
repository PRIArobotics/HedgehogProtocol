from . import Message, register


@register
class Request(Message):
    _command_oneof = 'analog_request'
    name = 'AnalogRequest'
    fields = ('port',)

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
    name = 'AnalogUpdate'
    fields = ('port', 'value')

    def __init__(self, port, value):
        self.port = port
        self.value = value

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.value)

    def _serialize(self, msg):
        msg.port = self.port
        msg.value = self.value
