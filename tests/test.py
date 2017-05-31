import unittest
import zmq
from hedgehog.protocol import errors, sockets, CommSide, ServerSide, ClientSide
from hedgehog.protocol.proto.hedgehog_pb2 import HedgehogMessage
from hedgehog.protocol.messages import Message, ack, io, analog, digital, motor, servo, process


class TestMessages(unittest.TestCase):
    def assertTransmission(self, msg: Message, wire: HedgehogMessage, sender: CommSide, receiver: CommSide):
        on_wire = sender.serialize(msg)
        self.assertEqual(on_wire, wire.SerializeToString())
        received = receiver.parse(on_wire)
        self.assertEqual(received, msg)

    def assertTransmissionClientServer(self, msg: Message, wire: HedgehogMessage):
        self.assertTransmission(msg, wire, ClientSide, ServerSide)

    def assertTransmissionServerClient(self, msg: Message, wire: HedgehogMessage):
        self.assertTransmission(msg, wire, ServerSide, ClientSide)

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

    def test_io_state_action(self):
        msg = io.Action(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_action.flags = io.INPUT_PULLDOWN
        self.assertTransmissionClientServer(msg, proto)

        with self.assertRaises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLUP)

        with self.assertRaises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLDOWN)

        with self.assertRaises(errors.InvalidCommandError):
            io.Action(0, io.LEVEL)

        with self.assertRaises(errors.InvalidCommandError):
            io.Action(0, io.PULLUP | io.PULLDOWN)

    def test_io_command_request(self):
        msg = io.CommandRequest(0)
        proto = HedgehogMessage()
        proto.io_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_io_command_reply(self):
        msg = io.CommandReply(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_command_message.flags = io.INPUT_PULLDOWN
        self.assertTransmissionServerClient(msg, proto)

        with self.assertRaises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLUP)

        with self.assertRaises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLDOWN)

        with self.assertRaises(errors.InvalidCommandError):
            io.CommandReply(0, io.LEVEL)

        with self.assertRaises(errors.InvalidCommandError):
            io.CommandReply(0, io.PULLUP | io.PULLDOWN)

    def test_analog_request(self):
        msg = analog.Request(0)
        proto = HedgehogMessage()
        proto.analog_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_analog_reply(self):
        msg = analog.Reply(0, 2)
        proto = HedgehogMessage()
        proto.analog_message.value = 2
        self.assertTransmissionServerClient(msg, proto)

    def test_digital_request(self):
        msg = digital.Request(0)
        proto = HedgehogMessage()
        proto.digital_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_digital_reply(self):
        msg = digital.Reply(0, True)
        proto = HedgehogMessage()
        proto.digital_message.value = True
        self.assertTransmissionServerClient(msg, proto)

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

        with self.assertRaises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, relative=100, absolute=100)

        with self.assertRaises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, reached_state=motor.BRAKE)

        with self.assertRaises(errors.InvalidCommandError):
            motor.Action(0, motor.BRAKE, 100, absolute=100)

        with self.assertRaises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, -100, absolute=100)

        with self.assertRaises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 0, relative=100)

    def test_motor_command_request(self):
        msg = motor.CommandRequest(0)
        proto = HedgehogMessage()
        proto.motor_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_reply(self):
        msg = motor.CommandReply(0, motor.POWER, 1000)
        proto = HedgehogMessage()
        proto.motor_command_message.amount = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_state_request(self):
        msg = motor.StateRequest(0)
        proto = HedgehogMessage()
        proto.motor_state_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_state_reply(self):
        msg = motor.StateReply(0, 100, 1000)
        proto = HedgehogMessage()
        proto.motor_state_message.velocity = 100
        proto.motor_state_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_set_position_action(self):
        msg = motor.SetPositionAction(0, 0)
        proto = HedgehogMessage()
        proto.motor_set_position_action.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_action(self):
        msg = servo.Action(0, True, 512)
        proto = HedgehogMessage()
        proto.servo_action.active = True
        proto.servo_action.position = 512
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_request(self):
        msg = servo.CommandRequest(0)
        proto = HedgehogMessage()
        proto.servo_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_reply(self):
        msg = servo.CommandReply(0, True, 1000)
        proto = HedgehogMessage()
        proto.servo_command_message.active = True
        proto.servo_command_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_process_execute_action(self):
        msg = process.ExecuteAction('cat', working_dir='/home/pi')
        proto = HedgehogMessage()
        proto.process_execute_action.args.append('cat')
        proto.process_execute_action.working_dir = '/home/pi'
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

        with self.assertRaises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDOUT, b'abc')

        with self.assertRaises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDERR, b'abc')

    def test_process_stream_update(self):
        msg = process.StreamUpdate(123, process.STDOUT, b'abc')
        proto = HedgehogMessage()
        proto.process_stream_message.pid = 123
        proto.process_stream_message.fileno = process.STDOUT
        proto.process_stream_message.chunk = b'abc'
        self.assertTransmissionServerClient(msg, proto)

        with self.assertRaises(errors.InvalidCommandError):
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
        self.assertTransmissionServerClient(msg, proto)


class TestSockets(unittest.TestCase):
    def test_sockets_msg(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER, side=ServerSide)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ, side=ClientSide)
        req.connect(endpoint)

        old = analog.Request(1)  # type: Message
        req.send_msg(old)
        header, new = router.recv_msg()
        self.assertEqual(new, old)

        old = analog.Reply(1, 200)
        router.send_msg(header, old)
        new = req.recv_msg()
        self.assertEqual(new, old)

        router.close()
        req.close()

    def test_sockets_msgs(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER, side=ServerSide)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ, side=ClientSide)
        req.connect(endpoint)

        olds = [analog.Request(0), digital.Request(0)]
        req.send_msgs(olds)
        header, news = router.recv_msgs()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

        olds = [analog.Reply(0, 100), digital.Reply(0, True)]
        router.send_msgs(header, olds)
        news = req.recv_msgs()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

    def test_sockets_msg_raw(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER, side=ServerSide)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ, side=ClientSide)
        req.connect(endpoint)

        old = b'as'
        req.send_msg_raw(old)
        header, new = router.recv_msg_raw()
        self.assertEqual(new, old)

        old = b'df'
        router.send_msg_raw(header, old)
        new = req.recv_msg_raw()
        self.assertEqual(new, old)

        router.close()
        req.close()

    def test_sockets_msgs_raw(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER, side=ServerSide)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ, side=ClientSide)
        req.connect(endpoint)

        olds = [b'as', b'df']
        req.send_msgs_raw(olds)
        header, news = router.recv_msgs_raw()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

        olds = [b'fd', b'sa']
        router.send_msgs_raw(header, olds)
        news = req.recv_msgs_raw()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)


if __name__ == '__main__':
    unittest.main()
