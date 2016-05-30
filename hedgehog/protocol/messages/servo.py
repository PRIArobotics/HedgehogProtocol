from . import Msg, Message
from hedgehog.protocol.proto import servo_pb2


@Msg.register(servo_pb2.ServoAction, 'servo_action')
class Action(Message):
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
