from .gen.analog_pb2 import *
from .gen.hedgehog_pb2 import *


def _message_init(func):
    def new_func(*args, **kwargs):
        msg = HedgehogMessage()
        func(msg, *args, **kwargs)
        return msg
    return new_func


@_message_init
def AnalogRequest(msg, sensors):
    msg.analog_request.sensors.extend(sensors)


@_message_init
def AnalogUpdate(msg, sensors):
    msg.analog_update.sensors.update(sensors)
