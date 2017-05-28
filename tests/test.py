import unittest
import zmq
from hedgehog.protocol import errors, sockets, ServerSide, ClientSide
from hedgehog.protocol.messages import ack, io, analog, digital, motor, servo, process


class TestMessages(unittest.TestCase):
    def test_acknowledgement(self):
        old = ack.Acknowledgement()
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

        old = ack.Acknowledgement(ack.FAILED_COMMAND, 'something went wrong')
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_io_state_action(self):
        old = io.StateAction(0, io.INPUT_PULLDOWN)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.OUTPUT | io.PULLUP)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.OUTPUT | io.PULLDOWN)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.LEVEL)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.PULLUP | io.PULLDOWN)

    def test_io_state_request(self):
        old = io.StateRequest(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_io_state_reply(self):
        old = io.StateReply(0, io.INPUT_PULLDOWN)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateReply(0, io.OUTPUT | io.PULLUP)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateReply(0, io.OUTPUT | io.PULLDOWN)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateReply(0, io.LEVEL)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateReply(0, io.PULLUP | io.PULLDOWN)

    def test_analog_request(self):
        old = analog.Request(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_analog_reply(self):
        old = analog.Reply(0, 2)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_digital_request(self):
        old = digital.Request(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_digital_reply(self):
        old = digital.Reply(0, True)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_motor_action(self):
        old = motor.Action(0, motor.POWER)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.VELOCITY, 100)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.POWER, 100, relative=-100)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.VELOCITY, 100, absolute=-100)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

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
        old = motor.CommandRequest(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_motor_command_reply(self):
        old = motor.CommandReply(0, motor.POWER, 1000)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_motor_state_request(self):
        old = motor.StateRequest(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_motor_state_reply(self):
        old = motor.StateReply(0, 100, 1000)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_motor_set_position_action(self):
        old = motor.SetPositionAction(0, 0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_servo_action(self):
        old = servo.Action(0, True, 512)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_servo_command_request(self):
        old = servo.CommandRequest(0)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_servo_command_reply(self):
        old = servo.CommandReply(0, True, 1000)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_execute_action(self):
        old = process.ExecuteAction('cat', working_dir='/home/pi')
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_execute_reply(self):
        old = process.ExecuteReply(123)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_stream_action(self):
        old = process.StreamAction(123, process.STDIN, b'abc')
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_stream_update(self):
        old = process.StreamUpdate(123, process.STDIN, b'abc')
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_signal_action(self):
        old = process.SignalAction(123, 1)
        new = ServerSide.parse(ClientSide.serialize(old))
        self.assertEqual(new, old)

    def test_process_exit_update(self):
        old = process.ExitUpdate(123, 0)
        new = ClientSide.parse(ServerSide.serialize(old))
        self.assertEqual(new, old)


class TestSockets(unittest.TestCase):
    def test_sockets_msg(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ)
        req.connect(endpoint)

        old = analog.Request(1)
        req.send_msg(old)
        header, new = router.recv_msg()
        self.assertEqual(new, old)

        old = analog.Update(1, 200)
        router.send_msg(header, old)
        new = req.recv_msg()
        self.assertEqual(new, old)

        router.close()
        req.close()

    def test_sockets_msgs(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ)
        req.connect(endpoint)

        olds = [analog.Request(0), digital.Request(0)]
        req.send_msgs(olds)
        header, news = router.recv_msgs()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

        olds = [analog.Update(0, 100), digital.Update(0, True)]
        router.send_msgs(header, olds)
        news = req.recv_msgs()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

    def test_sockets_msg_raw(self):
        ctx = zmq.Context()
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ)
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

        router = sockets.DealerRouterSocket(ctx, zmq.ROUTER)
        router.bind(endpoint)

        req = sockets.ReqSocket(ctx, zmq.REQ)
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
