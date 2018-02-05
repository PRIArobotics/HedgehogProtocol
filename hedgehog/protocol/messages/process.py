from . import RequestMsg, ReplyMsg, SimpleMessage
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto import process_pb2
from hedgehog.protocol.proto.process_pb2 import STDIN, STDOUT, STDERR


@RequestMsg.message(process_pb2.ProcessExecuteAction, 'process_execute_action')
class ExecuteAction(SimpleMessage):
    def __init__(self, *args: str, working_dir: str=None) -> None:
        self.args = args
        self.working_dir = working_dir

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExecuteAction) -> 'ExecuteAction':
        args = msg.args
        working_dir = msg.working_dir if msg.working_dir != '' else None
        return cls(*args, working_dir=working_dir)

    def _serialize(self, msg: process_pb2.ProcessExecuteAction) -> None:
        msg.args.extend(self.args)
        if self.working_dir is not None:
            msg.working_dir = self.working_dir


@ReplyMsg.message(process_pb2.ProcessExecuteReply, 'process_execute_reply')
class ExecuteReply(SimpleMessage):
    def __init__(self, pid: int) -> None:
        self.pid = pid

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExecuteReply) -> 'ExecuteReply':
        pid = msg.pid
        return cls(pid)

    def _serialize(self, msg: process_pb2.ProcessExecuteReply) -> None:
        msg.pid = self.pid


@RequestMsg.message(process_pb2.ProcessStreamMessage, 'process_stream_message')
class StreamAction(SimpleMessage):
    def __init__(self, pid: int, fileno: int, chunk: bytes=b'') -> None:
        if fileno != STDIN:
            raise InvalidCommandError("only STDIN is writable")
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessStreamMessage) -> 'StreamAction':
        pid = msg.pid
        fileno = msg.fileno
        chunk = msg.chunk
        return cls(pid, fileno, chunk)

    def _serialize(self, msg: process_pb2.ProcessStreamMessage) -> None:
        msg.pid = self.pid
        msg.fileno = self.fileno
        msg.chunk = self.chunk


@ReplyMsg.message(process_pb2.ProcessStreamMessage, 'process_stream_message')
class StreamUpdate(SimpleMessage):
    is_async = True

    def __init__(self, pid: int, fileno: int, chunk: bytes=b'') -> None:
        if fileno not in (STDOUT, STDERR):
            raise InvalidCommandError("only STDOUT and STDERR are readable")
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessStreamMessage) -> 'StreamUpdate':
        pid = msg.pid
        fileno = msg.fileno
        chunk = msg.chunk
        return cls(pid, fileno, chunk)

    def _serialize(self, msg: process_pb2.ProcessStreamMessage) -> None:
        msg.pid = self.pid
        msg.fileno = self.fileno
        msg.chunk = self.chunk


@RequestMsg.message(process_pb2.ProcessSignalAction, 'process_signal_action')
class SignalAction(SimpleMessage):
    def __init__(self, pid: int, signal: int) -> None:
        self.pid = pid
        self.signal = signal

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessSignalAction) -> 'SignalAction':
        pid = msg.pid
        signal = msg.signal
        return cls(pid, signal)

    def _serialize(self, msg: process_pb2.ProcessSignalAction) -> None:
        msg.pid = self.pid
        msg.signal = self.signal


@ReplyMsg.message(process_pb2.ProcessExitUpdate, 'process_exit_update')
class ExitUpdate(SimpleMessage):
    is_async = True

    def __init__(self, pid: int, exit_code: int) -> None:
        self.pid = pid
        self.exit_code = exit_code

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExitUpdate) -> 'ExitUpdate':
        pid = msg.pid
        exit_code = msg.exit_code
        return cls(pid, exit_code)

    def _serialize(self, msg: process_pb2.ProcessExitUpdate) -> None:
        msg.pid = self.pid
        msg.exit_code = self.exit_code
