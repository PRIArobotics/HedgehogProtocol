from . import Message, register


@register
class Action(Message):
    _command_oneof = 'servo_action'

    def __init__(self, port, position):
        self.port = port
        self.position = position

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.position)

    def _serialize(self, msg):
        msg.port = self.port
        msg.position = self.position


@register
class StateAction(Message):
    _command_oneof = 'servo_state_action'

    def __init__(self, port, active):
        self.port = port
        self.active = active

    @classmethod
    def _parse(cls, msg):
        return cls(msg.port, msg.active)

    def _serialize(self, msg):
        msg.port = self.port
        msg.active = self.active
