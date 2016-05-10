from .proto.ack_pb2 import UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND


class HedgehogCommandError(Exception):
    code = None

    def to_message(self):
        from .messages import ack
        return ack.Acknowledgement(self.code, self.args[0])


class UnknownCommandError(HedgehogCommandError):
    code = UNKNOWN_COMMAND


class InvalidCommandError(HedgehogCommandError):
    code = INVALID_COMMAND


class UnsupportedCommandError(HedgehogCommandError):
    code = UNSUPPORTED_COMMAND


class FailedCommandError(HedgehogCommandError):
    code = FAILED_COMMAND


_errors = {
    UNKNOWN_COMMAND: UnknownCommandError,
    INVALID_COMMAND: InvalidCommandError,
    UNSUPPORTED_COMMAND: UnsupportedCommandError,
    FAILED_COMMAND: FailedCommandError,
}


def error(code, *args, **kwargs):
    return _errors[code](*args, **kwargs)
