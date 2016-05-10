from . import Message, register


@register
class Action(Message):
    _command_oneof = 'servo_action'

    def __init__(self, port, active, position):
        self.port = port
        self.active = active
        self.position = position

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.active, msg.position)

    def _serialize(self, msg):
        msg.port = self.port
        msg.active = self.active
        msg.position = self.position
