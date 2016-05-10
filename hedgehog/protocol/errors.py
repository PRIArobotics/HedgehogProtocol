from .proto.ack_pb2 import UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND


class HedgehogCommandError(Exception):
    code = None


class UnknownCommandError(HedgehogCommandError):
    code = UNKNOWN_COMMAND


class InvalidCommandError(HedgehogCommandError):
    code = INVALID_COMMAND


class UnsupportedCommandError(HedgehogCommandError):
    code = UNSUPPORTED_COMMAND


class FailedCommandError(HedgehogCommandError):
    code = FAILED_COMMAND
