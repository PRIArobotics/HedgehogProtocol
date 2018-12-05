from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import process_pb2
from hedgehog.utils import protobuf

__all__ = ['ExecuteAction', 'ExecuteReply', 'StreamAction', 'StreamUpdate', 'SignalAction', 'ExitUpdate']

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.process_pb2 import STDIN, STDOUT, STDERR

__all__ += ['STDIN', 'STDOUT', 'STDERR']
# </GSL customizable: module-header>


@RequestMsg.message(process_pb2.ProcessExecuteAction, 'process_execute_action', fields=('args', 'working_dir',))
@dataclass(frozen=True, repr=False)
class ExecuteAction(SimpleMessage):
    args: Sequence[str]
    working_dir: str = None

    def __init__(self, *args: str, working_dir: str=None) -> None:
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'working_dir', working_dir)
        self.__post_init__()

    def __post_init__(self):
        # <default GSL customizable: ExecuteAction-init-validation>
        pass
        # </GSL customizable: ExecuteAction-init-validation>

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
@dataclass(frozen=True, repr=False)
class ExecuteReply(SimpleMessage):
    pid: int

    def __post_init__(self):
        # <default GSL customizable: ExecuteReply-init-validation>
        pass
        # </GSL customizable: ExecuteReply-init-validation>

    # <default GSL customizable: ExecuteReply-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExecuteReply) -> 'ExecuteReply':
        pid = msg.pid
        return cls(pid)

    def _serialize(self, msg: process_pb2.ProcessExecuteReply) -> None:
        msg.pid = self.pid


@RequestMsg.message(process_pb2.ProcessStreamMessage, 'process_stream_message', fields=('pid', 'fileno', 'chunk',))
@dataclass(frozen=True, repr=False)
class StreamAction(SimpleMessage):
    pid: int
    fileno: int
    chunk: bytes = b''

    def __post_init__(self):
        # <GSL customizable: StreamAction-init-validation>
        if self.fileno != STDIN:
            raise InvalidCommandError("only STDIN is writable")
        # </GSL customizable: StreamAction-init-validation>

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
@dataclass(frozen=True, repr=False)
class StreamUpdate(SimpleMessage):
    is_async = True

    pid: int
    fileno: int
    chunk: bytes = b''

    def __post_init__(self):
        # <GSL customizable: StreamUpdate-init-validation>
        if self.fileno not in (STDOUT, STDERR):
            raise InvalidCommandError("only STDOUT and STDERR are readable")
        # </GSL customizable: StreamUpdate-init-validation>

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
@dataclass(frozen=True, repr=False)
class SignalAction(SimpleMessage):
    pid: int
    signal: int

    def __post_init__(self):
        # <default GSL customizable: SignalAction-init-validation>
        pass
        # </GSL customizable: SignalAction-init-validation>

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
@dataclass(frozen=True, repr=False)
class ExitUpdate(SimpleMessage):
    is_async = True

    pid: int
    exit_code: int

    def __post_init__(self):
        # <default GSL customizable: ExitUpdate-init-validation>
        pass
        # </GSL customizable: ExitUpdate-init-validation>

    # <default GSL customizable: ExitUpdate-extra-members />

    @classmethod
    def _parse(cls, msg: process_pb2.ProcessExitUpdate) -> 'ExitUpdate':
        pid = msg.pid
        exit_code = msg.exit_code
        return cls(pid, exit_code)

    def _serialize(self, msg: process_pb2.ProcessExitUpdate) -> None:
        msg.pid = self.pid
        msg.exit_code = self.exit_code
