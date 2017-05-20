"""
Errors that may be caused by Hedgehog commands.

Every error corresponds to one acknowledge code from ack.proto; the `OK` code naturally has no corresponding error.
"""

from .proto.ack_pb2 import UNKNOWN_COMMAND, INVALID_COMMAND, UNSUPPORTED_COMMAND, FAILED_COMMAND


class HedgehogCommandError(Exception):
    """Superclass of all errors caused by Hedgehog commands."""
    code = None
    """Class property containing the acknowledgement code"""

    def to_message(self):
        """
        Creates an error Acknowledgement message.
        The message's code and message are taken from this exception.

        :return: the message representing this exception
        """
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


class EmergencyShutdown(FailedCommandError):
    pass


_errors = {
    UNKNOWN_COMMAND: UnknownCommandError,
    INVALID_COMMAND: InvalidCommandError,
    UNSUPPORTED_COMMAND: UnsupportedCommandError,
    FAILED_COMMAND: FailedCommandError,
}


def error(code, *args, **kwargs):
    """
    Creates an error from the given code, and args and kwargs.

    :param code: The acknowledgement code
    :param args: Exception args
    :param kwargs: Exception kwargs
    :return: the error for the given acknowledgement code
    """
    # TODO add proper error code
    if code == FAILED_COMMAND and len(args) >= 1 and args[0] == "Emergency Shutdown activated":
        return EmergencyShutdown(*args, **kwargs)
    return _errors[code](*args, **kwargs)
