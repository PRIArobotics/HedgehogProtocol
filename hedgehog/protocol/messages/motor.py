from typing import Any, Sequence, Union
from dataclasses import dataclass

from . import RequestMsg, ReplyMsg, Message, SimpleMessage
from hedgehog.protocol.proto import motor_pb2
from hedgehog.utils import protobuf

__all__ = ['Action', 'ConfigAction', 'CommandRequest', 'CommandReply', 'CommandSubscribe', 'CommandUpdate', 'StateRequest', 'StateReply', 'StateSubscribe', 'StateUpdate', 'SetPositionAction']

# <GSL customizable: module-header>
from hedgehog.protocol.errors import InvalidCommandError
from hedgehog.protocol.proto.motor_pb2 import POWER, BRAKE, VELOCITY
from hedgehog.protocol.proto.subscription_pb2 import Subscription


@dataclass
class DcConfig:
    pass


@dataclass
class EncoderConfig:
    encoder_a_port: int
    encoder_b_port: int


@dataclass
class StepperConfig:
    pass


Config = Union[DcConfig, EncoderConfig, StepperConfig]


__all__ += [
    'DcConfig', 'EncoderConfig', 'StepperConfig', 'Config',
    'POWER', 'BRAKE', 'VELOCITY',
    'Subscription',
]
# </GSL customizable: module-header>


@RequestMsg.message(motor_pb2.MotorAction, 'motor_action', fields=('port', 'state', 'amount', 'reached_state', 'relative', 'absolute',))
@dataclass(frozen=True, repr=False)
class Action(SimpleMessage):
    port: int
    state: int
    amount: int = 0
    reached_state: int = POWER
    relative: int = None
    absolute: int = None

    def __post_init__(self):
        # <GSL customizable: Action-init-validation>
        if self.relative is not None and self.absolute is not None:
            raise InvalidCommandError("relative and absolute are mutually exclusive")
        if self.relative is None and self.absolute is None:
            if self.reached_state != 0:
                raise InvalidCommandError(
                    "reached_state must be kept at its default value for non-positional motor commands")
        else:
            if self.state == BRAKE:
                raise InvalidCommandError("state can't be BRAKE for positional motor commands")
            if self.amount <= 0:
                raise InvalidCommandError("velocity/power must be positive for positional motor commands")
        # </GSL customizable: Action-init-validation>

    # <default GSL customizable: Action-extra-members />

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorAction) -> 'Action':
        port = msg.port
        state = msg.state
        amount = msg.amount
        reached_state = msg.reached_state
        relative = msg.relative if msg.HasField('relative') else None
        absolute = msg.absolute if msg.HasField('absolute') else None
        return cls(port, state, amount, reached_state=reached_state, relative=relative, absolute=absolute)

    def _serialize(self, msg: motor_pb2.MotorAction) -> None:
        msg.port = self.port
        msg.state = self.state
        msg.amount = self.amount
        msg.reached_state = self.reached_state
        if self.relative is not None:
            msg.relative = self.relative
        if self.absolute is not None:
            msg.absolute = self.absolute


@RequestMsg.message(motor_pb2.MotorConfigAction, 'motor_config_action', fields=('port', 'config',))
@dataclass(frozen=True, repr=False)
class ConfigAction(SimpleMessage):
    port: int
    config: Any

    def __post_init__(self):
        # <default GSL customizable: ConfigAction-init-validation>
        pass
        # </GSL customizable: ConfigAction-init-validation>

    # <default GSL customizable: ConfigAction-extra-members />

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorConfigAction) -> 'ConfigAction':
        port = msg.port
        # <GSL customizable: ConfigAction-parse-config>
        if msg.HasField('dc'):
            config = DcConfig()
        elif msg.HasField('encoder'):
            config = EncoderConfig(msg.encoder.encoder_a_port, msg.encoder.encoder_b_port)
        elif msg.HasField('stepper'):
            config = StepperConfig()
        else:  # pragma: nocover
            assert False
        # </GSL customizable: ConfigAction-parse-config>
        return cls(port, config)

    def _serialize(self, msg: motor_pb2.MotorConfigAction) -> None:
        msg.port = self.port
        # <GSL customizable: ConfigAction-serialize-config>
        if isinstance(self.config, DcConfig):
            msg.dc.SetInParent()
        elif isinstance(self.config, EncoderConfig):
            msg.encoder.encoder_a_port = self.config.encoder_a_port
            msg.encoder.encoder_b_port = self.config.encoder_b_port
        elif isinstance(self.config, StepperConfig):
            msg.stepper.SetInParent()
        else:  # pragma: nocover
            assert False
        # </GSL customizable: ConfigAction-serialize-config>


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port',))
@dataclass(frozen=True, repr=False)
class CommandRequest(Message):
    port: int

    def __post_init__(self):
        # <default GSL customizable: CommandRequest-init-validation>
        pass
        # </GSL customizable: CommandRequest-init-validation>

    # <default GSL customizable: CommandRequest-extra-members />

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'config', 'state', 'amount',))
@dataclass(frozen=True, repr=False)
class CommandReply(Message):
    port: int
    config: Any
    state: int
    amount: int

    def __post_init__(self):
        # <default GSL customizable: CommandReply-init-validation>
        pass
        # </GSL customizable: CommandReply-init-validation>

    # <default GSL customizable: CommandReply-extra-members />

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        # <GSL customizable: CommandReply-serialize-config>
        if isinstance(self.config, DcConfig):
            msg.dc.SetInParent()
        elif isinstance(self.config, EncoderConfig):
            msg.encoder.encoder_a_port = self.config.encoder_a_port
            msg.encoder.encoder_b_port = self.config.encoder_b_port
        elif isinstance(self.config, StepperConfig):
            msg.stepper.SetInParent()
        else:  # pragma: nocover
            assert False
        # </GSL customizable: CommandReply-serialize-config>
        msg.state = self.state
        msg.amount = self.amount


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandSubscribe(Message):
    port: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: CommandSubscribe-init-validation>
        pass
        # </GSL customizable: CommandSubscribe-init-validation>

    # <default GSL customizable: CommandSubscribe-extra-members />

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(motor_pb2.MotorCommandMessage, 'motor_command_message', fields=('port', 'config', 'state', 'amount', 'subscription',))
@dataclass(frozen=True, repr=False)
class CommandUpdate(Message):
    is_async = True

    port: int
    config: Any
    state: int
    amount: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: CommandUpdate-init-validation>
        pass
        # </GSL customizable: CommandUpdate-init-validation>

    # <default GSL customizable: CommandUpdate-extra-members />

    def _serialize(self, msg: motor_pb2.MotorCommandMessage) -> None:
        msg.port = self.port
        # <GSL customizable: CommandUpdate-serialize-config>
        if isinstance(self.config, DcConfig):
            msg.dc.SetInParent()
        elif isinstance(self.config, EncoderConfig):
            msg.encoder.encoder_a_port = self.config.encoder_a_port
            msg.encoder.encoder_b_port = self.config.encoder_b_port
        elif isinstance(self.config, StepperConfig):
            msg.stepper.SetInParent()
        else:  # pragma: nocover
            assert False
        # </GSL customizable: CommandUpdate-serialize-config>
        msg.state = self.state
        msg.amount = self.amount
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port',))
@dataclass(frozen=True, repr=False)
class StateRequest(Message):
    port: int

    def __post_init__(self):
        # <default GSL customizable: StateRequest-init-validation>
        pass
        # </GSL customizable: StateRequest-init-validation>

    # <default GSL customizable: StateRequest-extra-members />

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'velocity', 'position',))
@dataclass(frozen=True, repr=False)
class StateReply(Message):
    port: int
    velocity: int
    position: int

    def __post_init__(self):
        # <default GSL customizable: StateReply-init-validation>
        pass
        # </GSL customizable: StateReply-init-validation>

    # <default GSL customizable: StateReply-extra-members />

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'subscription',))
@dataclass(frozen=True, repr=False)
class StateSubscribe(Message):
    port: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: StateSubscribe-init-validation>
        pass
        # </GSL customizable: StateSubscribe-init-validation>

    # <default GSL customizable: StateSubscribe-extra-members />

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.subscription.CopyFrom(self.subscription)


@protobuf.message(motor_pb2.MotorStateMessage, 'motor_state_message', fields=('port', 'velocity', 'position', 'subscription',))
@dataclass(frozen=True, repr=False)
class StateUpdate(Message):
    is_async = True

    port: int
    velocity: int
    position: int
    subscription: Subscription

    def __post_init__(self):
        # <default GSL customizable: StateUpdate-init-validation>
        pass
        # </GSL customizable: StateUpdate-init-validation>

    # <default GSL customizable: StateUpdate-extra-members />

    def _serialize(self, msg: motor_pb2.MotorStateMessage) -> None:
        msg.port = self.port
        msg.velocity = self.velocity
        msg.position = self.position
        msg.subscription.CopyFrom(self.subscription)


@RequestMsg.message(motor_pb2.MotorSetPositionAction, 'motor_set_position_action', fields=('port', 'position',))
@dataclass(frozen=True, repr=False)
class SetPositionAction(SimpleMessage):
    port: int
    position: int

    def __post_init__(self):
        # <default GSL customizable: SetPositionAction-init-validation>
        pass
        # </GSL customizable: SetPositionAction-init-validation>

    # <default GSL customizable: SetPositionAction-extra-members />

    @classmethod
    def _parse(cls, msg: motor_pb2.MotorSetPositionAction) -> 'SetPositionAction':
        port = msg.port
        position = msg.position
        return cls(port, position)

    def _serialize(self, msg: motor_pb2.MotorSetPositionAction) -> None:
        msg.port = self.port
        msg.position = self.position


@RequestMsg.parser('motor_command_message')
def _parse_motor_command_message_request(msg: motor_pb2.MotorCommandMessage) -> Union[CommandRequest, CommandSubscribe]:
    port = msg.port
    dc = msg.dc if msg.HasField('dc') else None
    encoder = msg.encoder if msg.HasField('encoder') else None
    stepper = msg.stepper if msg.HasField('stepper') else None
    state = msg.state
    amount = msg.amount
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_motor_command_message_request-return>
    if subscription is None:
        return CommandRequest(port)
    else:
        return CommandSubscribe(port, subscription)
    # </GSL customizable: _parse_motor_command_message_request-return>


@ReplyMsg.parser('motor_command_message')
def _parse_motor_command_message_reply(msg: motor_pb2.MotorCommandMessage) -> Union[CommandReply, CommandUpdate]:
    port = msg.port
    dc = msg.dc if msg.HasField('dc') else None
    encoder = msg.encoder if msg.HasField('encoder') else None
    stepper = msg.stepper if msg.HasField('stepper') else None
    state = msg.state
    amount = msg.amount
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_motor_command_message_reply-return>
    if dc:
        config = DcConfig()
    elif encoder:
        config = EncoderConfig(msg.encoder.encoder_a_port, msg.encoder.encoder_b_port)
    elif stepper:
        config = StepperConfig()
    else:  # pragma: nocover
        assert False

    if subscription is None:
        return CommandReply(port, config, state, amount)
    else:
        return CommandUpdate(port, config, state, amount, subscription)
    # </GSL customizable: _parse_motor_command_message_reply-return>


@RequestMsg.parser('motor_state_message')
def _parse_motor_state_message_request(msg: motor_pb2.MotorStateMessage) -> Union[StateRequest, StateSubscribe]:
    port = msg.port
    velocity = msg.velocity
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_motor_state_message_request-return>
    if subscription is None:
        return StateRequest(port)
    else:
        return StateSubscribe(port, subscription)
    # </GSL customizable: _parse_motor_state_message_request-return>


@ReplyMsg.parser('motor_state_message')
def _parse_motor_state_message_reply(msg: motor_pb2.MotorStateMessage) -> Union[StateReply, StateUpdate]:
    port = msg.port
    velocity = msg.velocity
    position = msg.position
    subscription = msg.subscription if msg.HasField('subscription') else None
    # <GSL customizable: _parse_motor_state_message_reply-return>
    if subscription is None:
        return StateReply(port, velocity, position)
    else:
        return StateUpdate(port, velocity, position, subscription)
    # </GSL customizable: _parse_motor_state_message_reply-return>
