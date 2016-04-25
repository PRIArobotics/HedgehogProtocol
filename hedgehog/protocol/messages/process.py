from . import Message, register
from hedgehog.protocol.proto.process_pb2 import STDIN, STDOUT, STDERR


@register
class ExecuteRequest(Message):
    _command_oneof = 'process_execute_request'

    def __init__(self, *args, working_dir=None):
        self.working_dir = working_dir
        self.args = args

    @classmethod
    def _parse(cls, msg):
        return cls(
            *msg.args,
            working_dir=msg.working_dir if msg.working_dir != '' else None)

    def _serialize(self, msg):
        if self.working_dir is not None:
            msg.working_dir = self.working_dir
        msg.args.extend(self.args)


@register
class ExecuteReply(Message):
    _command_oneof = 'process_execute_reply'

    def __init__(self, pid):
        self.pid = pid

    @classmethod
    def _parse(cls, msg):
        return cls(msg.pid)

    def _serialize(self, msg):
        msg.pid = self.pid


@register
class StreamAction(Message):
    _command_oneof = 'process_stream_action'

    def __init__(self, pid, fileno, chunk=b''):
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    @classmethod
    def _parse(cls, msg):
        return cls(msg.pid, msg.fileno, msg.chunk)

    def _serialize(self, msg):
        msg.pid = self.pid
        msg.fileno = self.fileno
        msg.chunk = self.chunk


@register
class StreamUpdate(Message):
    _command_oneof = 'process_stream_update'

    def __init__(self, pid, fileno, chunk=b''):
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    @classmethod
    def _parse(cls, msg):
        return cls(msg.pid, msg.fileno, msg.chunk)

    def _serialize(self, msg):
        msg.pid = self.pid
        msg.fileno = self.fileno
        msg.chunk = self.chunk


@register
class ExitUpdate(Message):
    _command_oneof = 'process_exit_update'

    def __init__(self, pid, exit_code):
        self.pid = pid
        self.exit_code = exit_code

    @classmethod
    def _parse(cls, msg):
        return cls(msg.pid, msg.exit_code)

    def _serialize(self, msg):
        msg.pid = self.pid
        msg.exit_code = self.exit_code

# TODO implement killing processes
