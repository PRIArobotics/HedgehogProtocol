import collections
import hedgehog.protocol.proto.hedgehog_pb2


def _message_init(func):
    """
    Augments `func(msg, ...)`, which modifies a `HedgehogMessage`, into `new_func(...)`, which creates a new message and
    applies the modifications from `func`.
    """
    def new_func(*args, **kwargs):
        msg = hedgehog.protocol.proto.hedgehog_pb2.HedgehogMessage()
        func(msg, *args, **kwargs)
        return msg
    return new_func


@_message_init
def parse(msg, data):
    """Parses the serialized message `data` into a `HedgehogMessage` object."""
    msg.ParseFromString(data)


@_message_init
def AnalogRequest(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `AnalogRequest` command."""
    msg.analog_request.sensors.extend(sensors)


@_message_init
def AnalogUpdate(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `AnalogUpdate` command."""
    msg.analog_update.sensors.update(sensors)


AnalogState = collections.namedtuple('AnalogState', ('pullup',))


@_message_init
def AnalogStateAction(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `AnalogPullupAction` command."""
    for port, state in sensors.items():
        msg.analog_state_action.sensors[port].pullup = state.pullup


@_message_init
def DigitalRequest(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `DigitalRequest` command."""
    msg.digital_request.sensors.extend(sensors)


@_message_init
def DigitalUpdate(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `DigitalUpdate` command."""
    msg.digital_update.sensors.update(sensors)


DigitalState = collections.namedtuple('DigitalState', ('pullup', 'output'))


@_message_init
def DigitalStateAction(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `DigitalStateAction` command."""
    for port, state in sensors.items():
        msg.digital_state_action.sensors[port].pullup = state.pullup
        msg.digital_state_action.sensors[port].output = state.output


@_message_init
def DigitalAction(msg, sensors):
    """Creates a `HedgehogMessage` object representing an `DigitalAction` command."""
    msg.digital_action.sensors.update(sensors)
