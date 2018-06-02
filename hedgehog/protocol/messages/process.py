from typing import Union

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import process_pb2
from hedgehog.utils import protobuf

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.process_pb2 import STDIN, STDOUT, STDERR
# </GSL customizable: module-header>


@RequestMsg.message(process_pb2.ProcessExecuteAction, 'process_execute_action', fields=('args', 'working_dir',))
class ExecuteAction(SimpleMessage):
    def __init__(self, *args: str, working_dir: str=None) -> None:
        # <default GSL customizable: ExecuteAction-init-validation />
        self.args = args
        self.working_dir = working_dir

    # <default GSL customizable: ExecuteAction-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExecuteAction) -> 'ExecuteAction':
        args = msg.args
        working_dir = msg.working_dir if msg.working_dir != '' else None
        return cls(*args, working_dir=working_dir)

    def _serialize(self, msg: process_pb2.ProcessExecuteAction) -> None:
        msg.args.extend(self.args)
        if self.working_dir is not None:
            msg.working_dir = self.working_dir


@ReplyMsg.message(process_pb2.ProcessExecuteReply, 'process_execute_reply', fields=('pid',))
class ExecuteReply(SimpleMessage):
    def __init__(self, pid: int) -> None:
        # <default GSL customizable: ExecuteReply-init-validation />
        self.pid = pid

    # <default GSL customizable: ExecuteReply-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExecuteReply) -> 'ExecuteReply':
        pid = msg.pid
        return cls(pid)

    def _serialize(self, msg: process_pb2.ProcessExecuteReply) -> None:
        msg.pid = self.pid


@RequestMsg.message(process_pb2.ProcessStreamMessage, 'process_stream_message', fields=('pid', 'fileno', 'chunk',))
class StreamAction(SimpleMessage):
    def __init__(self, pid: int, fileno: int, chunk: bytes=b'') -> None:
        # <GSL customizable: StreamAction-init-validation>
        if fileno != STDIN:
            raise InvalidCommandError("only STDIN is writable")
        # </GSL customizable: StreamAction-init-validation>
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    # <default GSL customizable: StreamAction-extra-members />

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


@ReplyMsg.message(process_pb2.ProcessStreamMessage, 'process_stream_message', fields=('pid', 'fileno', 'chunk',))
class StreamUpdate(SimpleMessage):
    is_async = True

    def __init__(self, pid: int, fileno: int, chunk: bytes=b'') -> None:
        # <GSL customizable: StreamUpdate-init-validation>
        if fileno not in (STDOUT, STDERR):
            raise InvalidCommandError("only STDOUT and STDERR are readable")
        # </GSL customizable: StreamUpdate-init-validation>
        self.pid = pid
        self.fileno = fileno
        self.chunk = chunk

    # <default GSL customizable: StreamUpdate-extra-members />

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


@RequestMsg.message(process_pb2.ProcessSignalAction, 'process_signal_action', fields=('pid', 'signal',))
class SignalAction(SimpleMessage):
    def __init__(self, pid: int, signal: int) -> None:
        # <default GSL customizable: SignalAction-init-validation />
        self.pid = pid
        self.signal = signal

    # <default GSL customizable: SignalAction-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessSignalAction) -> 'SignalAction':
        pid = msg.pid
        signal = msg.signal
        return cls(pid, signal)

    def _serialize(self, msg: process_pb2.ProcessSignalAction) -> None:
        msg.pid = self.pid
        msg.signal = self.signal


@ReplyMsg.message(process_pb2.ProcessExitUpdate, 'process_exit_update', fields=('pid', 'exit_code',))
class ExitUpdate(SimpleMessage):
    is_async = True

    def __init__(self, pid: int, exit_code: int) -> None:
        # <default GSL customizable: ExitUpdate-init-validation />
        self.pid = pid
        self.exit_code = exit_code

    # <default GSL customizable: ExitUpdate-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExitUpdate) -> 'ExitUpdate':
        pid = msg.pid
        exit_code = msg.exit_code
        return cls(pid, exit_code)

    def _serialize(self, msg: process_pb2.ProcessExitUpdate) -> None:
        msg.pid = self.pid
        msg.exit_code = self.exit_code
