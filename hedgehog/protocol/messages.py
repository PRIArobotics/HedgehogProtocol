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
