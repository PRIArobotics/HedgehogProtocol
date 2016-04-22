import collections
from . import Message, register


@register
class Request(Message):
    _command_oneof = 'digital_request'

    def __init__(self, sensors):
        self.sensors = sensors

    @classmethod
    def _parse(cls, msg):
        return cls([port for port in msg.sensors])

    def _serialize(self, msg):
        msg.sensors.extend(self.sensors)


@register
class Update(Message):
    _command_oneof = 'digital_update'

    def __init__(self, sensors):
        self.sensors = sensors

    @classmethod
    def _parse(cls, msg):
        return cls({port: value for port, value in msg.sensors.items()})

    def _serialize(self, msg):
        msg.sensors.update(self.sensors)


@register
class StateAction(Message):
    State = collections.namedtuple('State', ('pullup', 'output'))

    _command_oneof = 'digital_state_action'

    def __init__(self, sensors):
        self.sensors = sensors

    @classmethod
    def _parse(cls, msg):
        return cls({port: StateAction.State(state.pullup, state.output) for port, state in msg.sensors.items()})

    def _serialize(self, msg):
        for port, state in self.sensors.items():
            msg.sensors[port].pullup = state.pullup
            msg.sensors[port].output = state.output
