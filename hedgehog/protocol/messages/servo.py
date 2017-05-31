from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.proto import servo_pb2


@RequestMsg.message(servo_pb2.ServoAction, 'servo_action')
class Action(SimpleMessage):
    def __init__(self, port: int, active: bool, position: int) -> None:
        self.port = port
        self.active = active
        self.position = position

    @classmethod
    def _parse(cls, msg: servo_pb2.ServoAction) -> 'Action':
        return cls(msg.port, msg.active, msg.position)

    def _serialize(self, msg: servo_pb2.ServoAction) -> None:
        msg.port = self.port
        msg.active = self.active
        msg.position = self.position


@RequestMsg.message(servo_pb2.ServoCommandMessage, 'servo_command_message', fields=('port',))
class CommandRequest(SimpleMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    @classmethod
    def _parse(cls, msg: servo_pb2.ServoCommandMessage) -> 'CommandRequest':
        return cls(msg.port)

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port


@ReplyMsg.message(servo_pb2.ServoCommandMessage, 'servo_command_message')
class CommandReply(SimpleMessage):
    def __init__(self, port: int, active: bool, position: int=0) -> None:
        self.port = port
        self.active = active
        self.position = position

    @classmethod
    def _parse(cls, msg: servo_pb2.ServoCommandMessage) -> 'CommandReply':
        return cls(msg.port, msg.active, msg.position)

    def _serialize(self, msg: servo_pb2.ServoCommandMessage) -> None:
        msg.port = self.port
        msg.active = self.active
        msg.position = self.position
