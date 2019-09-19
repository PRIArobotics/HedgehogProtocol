import pytest
from hedgehog.utils.test_utils import event_loop, zmq_ctx, zmq_aio_ctx, zmq_trio_ctx

import trio_asyncio
import zmq.asyncio
from hedgehog.protocol import errors, CommSide, ServerSide, ClientSide
from hedgehog.protocol import zmq as zmq_sync
from hedgehog.protocol.zmq import raw_to_delimited, raw_from_delimited, to_delimited, from_delimited
from hedgehog.protocol.zmq import asyncio as zmq_asyncio, trio as zmq_trio
from hedgehog.protocol.proto.hedgehog_pb2 import HedgehogMessage
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.protocol.messages import Message, ack, version, emergency, io, analog, digital, imu, motor, servo, process, speaker, vision


# Pytest fixtures
event_loop, zmq_ctx, zmq_aio_ctx, zmq_trio_ctx


class TestErrors(object):
    def test_errors(self):
        error = errors.UnknownCommandError("Unknown")

        msg = error.to_message()
        assert msg == ack.Acknowledgement(ack.UNKNOWN_COMMAND, "Unknown")

        error2 = errors.error(msg.code, msg.message)
        assert type(error2) == type(error)
        assert error2.args == error.args

    def test_emergency_stop(self):
        error = errors.EmergencyShutdown("Emergency Shutdown activated")

        msg = error.to_message()
        assert msg == ack.Acknowledgement(ack.FAILED_COMMAND, "Emergency Shutdown activated")

        error2 = errors.error(msg.code, msg.message)
        assert type(error2) == type(error)
        assert error2.args == error.args


class TestMessages(object):
    def assertTransmission(self, msg: Message, wire: HedgehogMessage, sender: CommSide, receiver: CommSide, is_async: bool=False):
        assert msg.is_async == is_async
        on_wire = sender.serialize(msg)
        assert on_wire == wire.SerializeToString()
        received = receiver.parse(on_wire)
        assert received == msg
        assert received.is_async == is_async

    def assertTransmissionClientServer(self, msg: Message, wire: HedgehogMessage, is_async: bool=False):
        self.assertTransmission(msg, wire, ClientSide, ServerSide, is_async)

    def assertTransmissionServerClient(self, msg: Message, wire: HedgehogMessage, is_async: bool=False):
        self.assertTransmission(msg, wire, ServerSide, ClientSide, is_async)

    def test_parse_invalid(self):
        proto = HedgehogMessage()
        proto.io_action.flags = io.OUTPUT | io.PULLUP
        with pytest.raises(errors.InvalidCommandError):
            ServerSide.parse(proto.SerializeToString())

    def test_parse_unknown(self):
        proto = HedgehogMessage()
        proto.io_action.flags = io.OUTPUT | io.PULLUP
        with pytest.raises(errors.UnknownCommandError):
            ClientSide.parse(proto.SerializeToString())

    def test_parse_malformed(self):
        with pytest.raises(errors.UnknownCommandError):
            ServerSide.parse(b'asdf')

    def test_repr(self):
        assert repr(io.Action(0, io.INPUT_PULLUP)) == f'io.Action(port=0, flags={io.INPUT_PULLUP})'

    def test_acknowledgement(self):
        msg = ack.Acknowledgement()
        proto = HedgehogMessage()
        proto.acknowledgement.SetInParent()
        self.assertTransmissionServerClient(msg, proto)

        msg = ack.Acknowledgement(ack.FAILED_COMMAND, 'something went wrong')
        proto = HedgehogMessage()
        proto.acknowledgement.code = ack.FAILED_COMMAND
        proto.acknowledgement.message = 'something went wrong'
        self.assertTransmissionServerClient(msg, proto)

    def test_version_request(self):
        msg = version.Request()
        proto = HedgehogMessage()
        proto.version_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_version_reply(self):
        msg = version.Reply(b"foo", "3", "0", "0.9.0a2")
        proto = HedgehogMessage()
        proto.version_message.uc_id = b"foo"
        proto.version_message.hardware_version = "3"
        proto.version_message.firmware_version = "0"
        proto.version_message.server_version = "0.9.0a2"
        self.assertTransmissionServerClient(msg, proto)

    def test_emergency_action(self):
        msg = emergency.Action(True)
        proto = HedgehogMessage()
        proto.emergency_action.activate = True
        self.assertTransmissionClientServer(msg, proto)

    def test_emergency_request(self):
        msg = emergency.Request()
        proto = HedgehogMessage()
        proto.emergency_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_emergency_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = emergency.Subscribe(sub)
        proto = HedgehogMessage()
        proto.emergency_message.subscription.subscribe = True
        proto.emergency_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_emergency_reply(self):
        msg = emergency.Reply(True)
        proto = HedgehogMessage()
        proto.emergency_message.active = True
        self.assertTransmissionServerClient(msg, proto)

    def test_emergency_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = emergency.Update(True, sub)
        proto = HedgehogMessage()
        proto.emergency_message.active = True
        proto.emergency_message.subscription.subscribe = True
        proto.emergency_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_io_action(self):
        msg = io.Action(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_action.flags = io.INPUT_PULLDOWN
        self.assertTransmissionClientServer(msg, proto)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLUP)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLDOWN)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.LEVEL)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.PULLUP | io.PULLDOWN)

    def test_io_command_request(self):
        msg = io.CommandRequest(0)
        proto = HedgehogMessage()
        proto.io_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_io_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = io.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.io_command_message.subscription.subscribe = True
        proto.io_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_io_command_reply(self):
        msg = io.CommandReply(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_command_message.flags = io.INPUT_PULLDOWN
        self.assertTransmissionServerClient(msg, proto)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLUP)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLDOWN)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.LEVEL)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.PULLUP | io.PULLDOWN)

    def test_io_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = io.CommandUpdate(0, io.INPUT_PULLDOWN, sub)
        proto = HedgehogMessage()
        proto.io_command_message.flags = io.INPUT_PULLDOWN
        proto.io_command_message.subscription.subscribe = True
        proto.io_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.OUTPUT | io.PULLUP, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.OUTPUT | io.PULLDOWN, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.LEVEL, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.PULLUP | io.PULLDOWN, sub)

    def test_analog_request(self):
        msg = analog.Request(0)
        proto = HedgehogMessage()
        proto.analog_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_analog_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        sub.int_granularity = 20
        sub.granularity_timeout = 200
        msg = analog.Subscribe(0, sub)
        proto = HedgehogMessage()
        proto.analog_message.subscription.subscribe = True
        proto.analog_message.subscription.timeout = 10
        proto.analog_message.subscription.int_granularity = 20
        proto.analog_message.subscription.granularity_timeout = 200
        self.assertTransmissionClientServer(msg, proto)

    def test_analog_reply(self):
        msg = analog.Reply(0, 2)
        proto = HedgehogMessage()
        proto.analog_message.value = 2
        self.assertTransmissionServerClient(msg, proto)

    def test_analog_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        sub.int_granularity = 20
        sub.granularity_timeout = 200
        msg = analog.Update(0, 2, sub)
        proto = HedgehogMessage()
        proto.analog_message.value = 2
        proto.analog_message.subscription.subscribe = True
        proto.analog_message.subscription.timeout = 10
        proto.analog_message.subscription.int_granularity = 20
        proto.analog_message.subscription.granularity_timeout = 200
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_digital_request(self):
        msg = digital.Request(0)
        proto = HedgehogMessage()
        proto.digital_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_digital_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        msg = digital.Subscribe(0, sub)
        proto = HedgehogMessage()
        proto.digital_message.subscription.subscribe = True
        self.assertTransmissionClientServer(msg, proto)

    def test_digital_reply(self):
        msg = digital.Reply(0, True)
        proto = HedgehogMessage()
        proto.digital_message.value = True
        self.assertTransmissionServerClient(msg, proto)

    def test_digital_update(self):
        sub = Subscription()
        sub.subscribe = True
        msg = digital.Update(0, True, sub)
        proto = HedgehogMessage()
        proto.digital_message.value = True
        proto.digital_message.subscription.subscribe = True
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_imu_rate_request(self):
        msg = imu.RateRequest()
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.RATE
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_rate_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.RateSubscribe(sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.RATE
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_rate_reply(self):
        msg = imu.RateReply(0, 0, 0)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.RATE
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        self.assertTransmissionServerClient(msg, proto)

    def test_imu_rate_update(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.RateUpdate(0, 0, 0, sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.RATE
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_imu_acceleration_request(self):
        msg = imu.AccelerationRequest()
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.ACCELERATION
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_acceleration_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.AccelerationSubscribe(sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.ACCELERATION
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_acceleration_reply(self):
        msg = imu.AccelerationReply(0, 0, 0)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.ACCELERATION
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        self.assertTransmissionServerClient(msg, proto)

    def test_imu_acceleration_update(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.AccelerationUpdate(0, 0, 0, sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.ACCELERATION
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_imu_pose_request(self):
        msg = imu.PoseRequest()
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.POSE
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_pose_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.PoseSubscribe(sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.POSE
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionClientServer(msg, proto)

    def test_imu_pose_reply(self):
        msg = imu.PoseReply(0, 0, 0)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.POSE
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        self.assertTransmissionServerClient(msg, proto)

    def test_imu_pose_update(self):
        sub = Subscription()
        sub.subscribe = True
        msg = imu.PoseUpdate(0, 0, 0, sub)
        proto = HedgehogMessage()
        proto.imu_message.kind = imu.POSE
        proto.imu_message.x = 0
        proto.imu_message.y = 0
        proto.imu_message.z = 0
        proto.imu_message.subscription.subscribe = True
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_motor_action(self):
        msg = motor.Action(0, motor.POWER)
        proto = HedgehogMessage()
        proto.motor_action.state = motor.POWER
        self.assertTransmissionClientServer(msg, proto)

        msg = motor.Action(0, motor.VELOCITY, 100)
        proto = HedgehogMessage()
        proto.motor_action.state = motor.VELOCITY
        proto.motor_action.amount = 100
        self.assertTransmissionClientServer(msg, proto)

        msg = motor.Action(0, motor.POWER, 100, relative=-100)
        proto = HedgehogMessage()
        proto.motor_action.amount = 100
        proto.motor_action.relative = -100
        self.assertTransmissionClientServer(msg, proto)

        msg = motor.Action(0, motor.VELOCITY, 100, absolute=-100)
        proto = HedgehogMessage()
        proto.motor_action.state = motor.VELOCITY
        proto.motor_action.amount = 100
        proto.motor_action.absolute = -100
        self.assertTransmissionClientServer(msg, proto)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, relative=100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, reached_state=motor.BRAKE)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.BRAKE, 100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, -100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 0, relative=100)

    def test_motor_config_action(self):
        msg = motor.ConfigAction(0, motor.DcConfig())
        proto = HedgehogMessage()
        proto.motor_config_action.dc.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

        msg = motor.ConfigAction(0, motor.EncoderConfig(0, 1))
        proto = HedgehogMessage()
        proto.motor_config_action.encoder.encoder_a_port = 0
        proto.motor_config_action.encoder.encoder_b_port = 1
        self.assertTransmissionClientServer(msg, proto)

        msg = motor.ConfigAction(0, motor.StepperConfig())
        proto = HedgehogMessage()
        proto.motor_config_action.stepper.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_request(self):
        msg = motor.CommandRequest(0)
        proto = HedgehogMessage()
        proto.motor_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.motor_command_message.subscription.subscribe = True
        proto.motor_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_reply(self):
        msg = motor.CommandReply(0, motor.DcConfig(), motor.POWER, 1000)
        proto = HedgehogMessage()
        proto.motor_command_message.dc.SetInParent()
        proto.motor_command_message.amount = 1000
        self.assertTransmissionServerClient(msg, proto)

        msg = motor.CommandReply(0, motor.EncoderConfig(0, 1), motor.POWER, 1000)
        proto.motor_command_message.encoder.encoder_a_port = 0
        proto.motor_command_message.encoder.encoder_b_port = 1
        self.assertTransmissionServerClient(msg, proto)

        msg = motor.CommandReply(0, motor.StepperConfig(), motor.POWER, 1000)
        proto.motor_command_message.stepper.SetInParent()
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.CommandUpdate(0, motor.DcConfig(), motor.POWER, 1000, sub)
        proto = HedgehogMessage()
        proto.motor_command_message.dc.SetInParent()
        proto.motor_command_message.amount = 1000
        proto.motor_command_message.subscription.subscribe = True
        proto.motor_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        msg = motor.CommandUpdate(0, motor.EncoderConfig(0, 1), motor.POWER, 1000, sub)
        proto.motor_command_message.encoder.encoder_a_port = 0
        proto.motor_command_message.encoder.encoder_b_port = 1
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        msg = motor.CommandUpdate(0, motor.StepperConfig(), motor.POWER, 1000, sub)
        proto.motor_command_message.stepper.SetInParent()
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_motor_state_request(self):
        msg = motor.StateRequest(0)
        proto = HedgehogMessage()
        proto.motor_state_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_state_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.StateSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.motor_state_message.subscription.subscribe = True
        proto.motor_state_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_state_reply(self):
        msg = motor.StateReply(0, 100, 1000)
        proto = HedgehogMessage()
        proto.motor_state_message.velocity = 100
        proto.motor_state_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_state_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.StateUpdate(0, 100, 1000, sub)
        proto = HedgehogMessage()
        proto.motor_state_message.velocity = 100
        proto.motor_state_message.position = 1000
        proto.motor_state_message.subscription.subscribe = True
        proto.motor_state_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_motor_set_position_action(self):
        msg = motor.SetPositionAction(0, 0)
        proto = HedgehogMessage()
        proto.motor_set_position_action.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_action(self):
        msg = servo.Action(0, 512)
        proto = HedgehogMessage()
        proto.servo_action.active = True
        proto.servo_action.position = 512
        self.assertTransmissionClientServer(msg, proto)

        msg = servo.Action(0, None)
        proto = HedgehogMessage()
        proto.servo_action.active = False
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_request(self):
        msg = servo.CommandRequest(0)
        proto = HedgehogMessage()
        proto.servo_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = servo.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.SetInParent()
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_reply(self):
        msg = servo.CommandReply(0, 1000)
        proto = HedgehogMessage()
        proto.servo_command_message.active = True
        proto.servo_command_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

        msg = servo.CommandReply(0, None)
        proto = HedgehogMessage()
        proto.servo_command_message.active = False
        self.assertTransmissionServerClient(msg, proto)

    def test_servo_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = servo.CommandUpdate(0, 1000, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.active = True
        proto.servo_command_message.position = 1000
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        msg = servo.CommandUpdate(0, None, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.active = False
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_process_execute_action(self):
        msg = process.ExecuteAction('cat', working_dir='/home/pi')
        proto = HedgehogMessage()
        proto.process_execute_action.args.append('cat')
        proto.process_execute_action.working_dir = '/home/pi'
        self.assertTransmissionClientServer(msg, proto)

        msg = process.ExecuteAction('cat')
        proto = HedgehogMessage()
        proto.process_execute_action.args.append('cat')
        self.assertTransmissionClientServer(msg, proto)

    def test_process_execute_reply(self):
        msg = process.ExecuteReply(123)
        proto = HedgehogMessage()
        proto.process_execute_reply.pid = 123
        self.assertTransmissionServerClient(msg, proto)

    def test_process_stream_action(self):
        msg = process.StreamAction(123, process.STDIN, b'abc')
        proto = HedgehogMessage()
        proto.process_stream_message.pid = 123
        proto.process_stream_message.fileno = process.STDIN
        proto.process_stream_message.chunk = b'abc'
        self.assertTransmissionClientServer(msg, proto)

        with pytest.raises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDOUT, b'abc')

        with pytest.raises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDERR, b'abc')

    def test_process_stream_update(self):
        msg = process.StreamUpdate(123, process.STDOUT, b'abc')
        proto = HedgehogMessage()
        proto.process_stream_message.pid = 123
        proto.process_stream_message.fileno = process.STDOUT
        proto.process_stream_message.chunk = b'abc'
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        with pytest.raises(errors.InvalidCommandError):
            process.StreamUpdate(123, process.STDIN, b'abc')

    def test_process_signal_action(self):
        msg = process.SignalAction(123, 1)
        proto = HedgehogMessage()
        proto.process_signal_action.pid = 123
        proto.process_signal_action.signal = 1
        self.assertTransmissionClientServer(msg, proto)

    def test_process_exit_update(self):
        msg = process.ExitUpdate(123, 0)
        proto = HedgehogMessage()
        proto.process_exit_update.pid = 123
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_speaker_action(self):
        msg = speaker.Action(1000)
        proto = HedgehogMessage()
        proto.speaker_action.frequency = 1000
        self.assertTransmissionClientServer(msg, proto)

        msg = speaker.Action(None)
        proto = HedgehogMessage()
        proto.speaker_action.frequency = 0
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_open_camera_action(self):
        msg = vision.OpenCameraAction()
        proto = HedgehogMessage()
        proto.vision_camera_action.open = True
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_close_camera_action(self):
        msg = vision.CloseCameraAction()
        proto = HedgehogMessage()
        proto.vision_camera_action.open = False
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_create_channel_action(self):
        msg = vision.CreateChannelAction({
            'foo': vision.FacesChannel(),
        })
        proto = HedgehogMessage()
        proto.vision_channel_message.op = vision.CREATE
        channel = proto.vision_channel_message.channels.add()
        channel.key = 'foo'
        channel.faces.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_update_channel_action(self):
        msg = vision.UpdateChannelAction({
            'foo': vision.BlobsChannel((0x22, 0x22, 0x22), (0x88, 0x88, 0x88)),
        })
        proto = HedgehogMessage()
        proto.vision_channel_message.op = vision.UPDATE
        channel = proto.vision_channel_message.channels.add()
        channel.key = 'foo'
        channel.blobs.hsv_min = 0x222222
        channel.blobs.hsv_max = 0x888888
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_delete_channel_action(self):
        msg = vision.DeleteChannelAction({
            'foo',
        })
        proto = HedgehogMessage()
        proto.vision_channel_message.op = vision.DELETE
        proto.vision_channel_message.channels.add().key = 'foo'
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_channel_request(self):
        msg = vision.ChannelRequest({
            'foo',
        })
        proto = HedgehogMessage()
        proto.vision_channel_message.op = vision.READ
        proto.vision_channel_message.channels.add().key = 'foo'
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_channel_reply(self):
        msg = vision.ChannelReply({
            'foo': vision.FacesChannel(),
        })
        proto = HedgehogMessage()
        proto.vision_channel_message.op = vision.READ
        channel = proto.vision_channel_message.channels.add()
        channel.key = 'foo'
        channel.faces.SetInParent()
        self.assertTransmissionServerClient(msg, proto)

    def test_vision_capture_frame_action(self):
        msg = vision.CaptureFrameAction()
        proto = HedgehogMessage()
        proto.vision_capture_frame_action.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_frame_request(self):
        msg = vision.FrameRequest(None)
        proto = HedgehogMessage()
        proto.vision_frame_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

        msg = vision.FrameRequest('foo')
        proto = HedgehogMessage()
        proto.vision_frame_message.highlight = 'foo'
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_frame_reply(self):
        msg = vision.FrameReply(None, bytes())
        proto = HedgehogMessage()
        proto.vision_frame_message.frame = bytes()
        self.assertTransmissionServerClient(msg, proto)

        msg = vision.FrameReply('foo', bytes())
        proto = HedgehogMessage()
        proto.vision_frame_message.highlight = 'foo'
        proto.vision_frame_message.frame = bytes()
        self.assertTransmissionServerClient(msg, proto)

    def test_vision_feature_request(self):
        msg = vision.FeatureRequest('foo')
        proto = HedgehogMessage()
        proto.vision_feature_message.channel = 'foo'
        self.assertTransmissionClientServer(msg, proto)

    def test_vision_feature_reply(self):
        msg = vision.FeatureReply('foo', vision.FacesFeature([
            vision.Face((0, 10, 100, 50)),
        ]))
        proto = HedgehogMessage()
        proto.vision_feature_message.channel = 'foo'
        face = proto.vision_feature_message.feature.faces.faces.add()
        face.y = 10
        face.width = 100
        face.height = 50
        self.assertTransmissionServerClient(msg, proto)

        msg = vision.FeatureReply('foo', vision.BlobsFeature([
            vision.Blob((0, 10, 100, 50), (50, 35), 0.5),
        ]))
        proto = HedgehogMessage()
        proto.vision_feature_message.channel = 'foo'
        blob = proto.vision_feature_message.feature.blobs.blobs.add()
        blob.y = 10
        blob.width = 100
        blob.height = 50
        blob.cx = 50
        blob.cy = 35
        blob.confidence = 0.5
        self.assertTransmissionServerClient(msg, proto)


class TestSockets(object):
    def test_raw_to_from_delimited(self):
        header = (b'asdf',)
        raw_payload = (b'foo', b'bar')

        delimited = raw_to_delimited(header, raw_payload)
        assert delimited == (b'asdf', b'', b'foo', b'bar')
        assert raw_from_delimited(delimited) == (header, raw_payload)

    def test_to_from_delimited(self):
        header = (b'asdf',)
        payload = (io.Action(0, io.INPUT_PULLUP), servo.Action(0, False))
        raw1, raw2 = [ClientSide.serialize(msg) for msg in payload]

        delimited = to_delimited(header, payload, ClientSide)
        assert delimited == (b'asdf', b'', raw1, raw2)
        assert from_delimited(delimited, ServerSide) == (header, payload)

    def test_sockets_msg(self, zmq_ctx):
        endpoint = "inproc://test"

        router = zmq_sync.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_sync.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = analog.Request(1)  # type: Message
            req.send_msg(old)
            header, new = router.recv_msg()
            assert new == old

            old = analog.Reply(1, 200)
            router.send_msg(header, old)
            new = req.recv_msg()
            assert new == old

    def test_sockets_msgs(self, zmq_ctx):
        endpoint = "inproc://test"

        router = zmq_sync.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_sync.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [analog.Request(0), digital.Request(0)]
            req.send_msgs(olds)
            header, news = router.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

            olds = [analog.Reply(0, 100), digital.Reply(0, True)]
            router.send_msgs(header, olds)
            news = req.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

    def test_sockets_msg_raw(self, zmq_ctx):
        endpoint = "inproc://test"

        router = zmq_sync.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_sync.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = b'as'
            req.send_msg_raw(old)
            header, new = router.recv_msg_raw()
            assert new == old

            old = b'df'
            router.send_msg_raw(header, old)
            new = req.recv_msg_raw()
            assert new == old

    def test_sockets_msgs_raw(self, zmq_ctx):
        endpoint = "inproc://test"

        router = zmq_sync.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_sync.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [b'as', b'df']
            req.send_msgs_raw(olds)
            header, news = router.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

            olds = [b'fd', b'sa']
            router.send_msgs_raw(header, olds)
            news = req.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

    @pytest.mark.asyncio
    async def test_asyncio_sockets_msg(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = zmq_asyncio.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_asyncio.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = analog.Request(1)  # type: Message
            await req.send_msg(old)
            header, new = await router.recv_msg()
            assert new == old

            old = analog.Reply(1, 200)
            await router.send_msg(header, old)
            new = await req.recv_msg()
            assert new == old

    @pytest.mark.asyncio
    async def test_asyncio_sockets_msgs(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = zmq_asyncio.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_asyncio.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [analog.Request(0), digital.Request(0)]
            await req.send_msgs(olds)
            header, news = await router.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

            olds = [analog.Reply(0, 100), digital.Reply(0, True)]
            await router.send_msgs(header, olds)
            news = await req.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

    @pytest.mark.asyncio
    async def test_asyncio_sockets_msg_raw(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = zmq_asyncio.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_asyncio.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = b'as'
            await req.send_msg_raw(old)
            header, new = await router.recv_msg_raw()
            assert new == old

            old = b'df'
            await router.send_msg_raw(header, old)
            new = await req.recv_msg_raw()
            assert new == old

    @pytest.mark.asyncio
    async def test_asyncio_sockets_msgs_raw(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = zmq_asyncio.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = zmq_asyncio.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [b'as', b'df']
            await req.send_msgs_raw(olds)
            header, news = await router.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

            olds = [b'fd', b'sa']
            await router.send_msgs_raw(header, olds)
            news = await req.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

    @pytest.mark.trio
    async def test_trio_sockets_msg(self, zmq_trio_ctx, autojump_clock):
        async with trio_asyncio.open_loop():
            endpoint = "inproc://test"

            router = zmq_trio.DealerRouterSocket(zmq_trio_ctx, zmq.ROUTER, side=ServerSide)
            req = zmq_trio.ReqSocket(zmq_trio_ctx, zmq.REQ, side=ClientSide)
            with router, req:
                router.bind(endpoint)
                req.connect(endpoint)

                old = analog.Request(1)  # type: Message
                await req.send_msg(old)
                header, new = await router.recv_msg()
                assert new == old

                old = analog.Reply(1, 200)
                await router.send_msg(header, old)
                new = await req.recv_msg()
                assert new == old

    @pytest.mark.trio
    async def test_trio_sockets_msgs(self, zmq_trio_ctx, autojump_clock):
        async with trio_asyncio.open_loop():
            endpoint = "inproc://test"

            router = zmq_trio.DealerRouterSocket(zmq_trio_ctx, zmq.ROUTER, side=ServerSide)
            req = zmq_trio.ReqSocket(zmq_trio_ctx, zmq.REQ, side=ClientSide)
            with router, req:
                router.bind(endpoint)
                req.connect(endpoint)

                olds = [analog.Request(0), digital.Request(0)]
                await req.send_msgs(olds)
                header, news = await router.recv_msgs()
                for old, new in zip(olds, news):
                    assert new == old

                olds = [analog.Reply(0, 100), digital.Reply(0, True)]
                await router.send_msgs(header, olds)
                news = await req.recv_msgs()
                for old, new in zip(olds, news):
                    assert new == old

    @pytest.mark.trio
    async def test_trio_sockets_msg_raw(self, zmq_trio_ctx, autojump_clock):
        async with trio_asyncio.open_loop():
            endpoint = "inproc://test"

            router = zmq_trio.DealerRouterSocket(zmq_trio_ctx, zmq.ROUTER, side=ServerSide)
            req = zmq_trio.ReqSocket(zmq_trio_ctx, zmq.REQ, side=ClientSide)
            with router, req:
                router.bind(endpoint)
                req.connect(endpoint)

                old = b'as'
                await req.send_msg_raw(old)
                header, new = await router.recv_msg_raw()
                assert new == old

                old = b'df'
                await router.send_msg_raw(header, old)
                new = await req.recv_msg_raw()
                assert new == old

    @pytest.mark.trio
    async def test_trio_sockets_msgs_raw(self, zmq_trio_ctx, autojump_clock):
        async with trio_asyncio.open_loop():
            endpoint = "inproc://test"

            router = zmq_trio.DealerRouterSocket(zmq_trio_ctx, zmq.ROUTER, side=ServerSide)
            req = zmq_trio.ReqSocket(zmq_trio_ctx, zmq.REQ, side=ClientSide)
            with router, req:
                router.bind(endpoint)
                req.connect(endpoint)

                olds = [b'as', b'df']
                await req.send_msgs_raw(olds)
                header, news = await router.recv_msgs_raw()
                for old, new in zip(olds, news):
                    assert new == old

                olds = [b'fd', b'sa']
                await router.send_msgs_raw(header, olds)
                news = await req.recv_msgs_raw()
                for old, new in zip(olds, news):
                    assert new == old
