import unittest
import zmq
from hedgehog.protocol import errors, messages, sockets
from hedgehog.protocol.messages import Msg, ack, io, analog, digital, motor, servo, process


class TestMessages(unittest.TestCase):
    def test_acknowledgement(self):
        old = ack.Acknowledgement()
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

        old = ack.Acknowledgement(ack.FAILED_COMMAND, 'something went wrong')
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_io_state_action(self):
        old = io.StateAction(0, io.INPUT_PULLDOWN)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.OUTPUT | io.PULLUP)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.OUTPUT | io.PULLDOWN)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.LEVEL)

        with self.assertRaises(errors.InvalidCommandError):
            io.StateAction(0, io.PULLUP | io.PULLDOWN)

    def test_analog_request(self):
        old = analog.Request(0)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_analog_update(self):
        old = analog.Update(0, 2)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_digital_request(self):
        old = digital.Request(0)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_digital_update(self):
        old = digital.Update(0, True)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_motor_action(self):
        old = motor.Action(0, motor.POWER)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.VELOCITY, 100)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.POWER, 100, relative=-100)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

        old = motor.Action(0, motor.VELOCITY, 100, absolute=-100)
        new = Msg.parse(Msg.serialize(old))
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

    def test_motor_request(self):
        old = motor.Request(0)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_motor_update(self):
        old = motor.Update(0, 100, 1000)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_motor_state_update(self):
        old = motor.StateUpdate(0, motor.POWER)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_motor_set_position_action(self):
        old = motor.SetPositionAction(0, 0)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_servo_action(self):
        old = servo.Action(0, True, 512)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_process_execute_request(self):
        old = process.ExecuteRequest('cat', working_dir='/home/hedgehog')
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_process_stream_action(self):
        old = process.StreamAction(123, process.STDIN, b'abc')
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_process_stream_update(self):
        old = process.StreamUpdate(123, process.STDIN, b'abc')
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_process_signal_action(self):
        old = process.SignalAction(123, 1)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)

    def test_process_exit_update(self):
        old = process.ExitUpdate(123, 0)
        new = Msg.parse(Msg.serialize(old))
        self.assertEqual(new, old)


class TestSockets(unittest.TestCase):
    def test_sockets_multipart(self):
        context = zmq.Context()
        endpoint = "inproc://test"

        router = context.socket(zmq.ROUTER)
        router.bind(endpoint)
        router = sockets.DealerRouterWrapper(router)

        req = context.socket(zmq.REQ)
        req.connect(endpoint)
        req = sockets.ReqWrapper(req)

        olds = [analog.Request(0), digital.Request(0)]
        req.send_multipart(olds)
        header, news = router.recv_multipart()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

        olds = [analog.Update(0, 100), digital.Update(0, True)]
        router.send_multipart(header, olds)
        news = req.recv_multipart()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

    def test_sockets_singlepart(self):
        context = zmq.Context()
        endpoint = "inproc://test"

        router = context.socket(zmq.ROUTER)
        router.bind(endpoint)
        router = sockets.DealerRouterWrapper(router)

        req = context.socket(zmq.REQ)
        req.connect(endpoint)
        req = sockets.ReqWrapper(req)

        old = analog.Request(1)
        req.send(old)
        header, new = router.recv()
        self.assertEqual(new, old)

        old = analog.Update(1, 200)
        router.send(header, old)
        new = req.recv()
        self.assertEqual(new, old)

        router.close()
        req.close()
    def test_sockets_multipart_raw(self):
        context = zmq.Context()
        endpoint = "inproc://test"

        router = context.socket(zmq.ROUTER)
        router.bind(endpoint)
        router = sockets.DealerRouterWrapper(router)

        req = context.socket(zmq.REQ)
        req.connect(endpoint)
        req = sockets.ReqWrapper(req)

        olds = [b'as', b'df']
        req.send_multipart_raw(olds)
        header, news = router.recv_multipart_raw()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

        olds = [b'fd', b'sa']
        router.send_multipart_raw(header, olds)
        news = req.recv_multipart_raw()
        for old, new in zip(olds, news):
            self.assertEqual(new, old)

    def test_sockets_singlepart_raw(self):
        context = zmq.Context()
        endpoint = "inproc://test"

        router = context.socket(zmq.ROUTER)
        router.bind(endpoint)
        router = sockets.DealerRouterWrapper(router)

        req = context.socket(zmq.REQ)
        req.connect(endpoint)
        req = sockets.ReqWrapper(req)

        old = b'as'
        req.send_raw(old)
        header, new = router.recv_raw()
        self.assertEqual(new, old)

        old = b'df'
        router.send_raw(header, old)
        new = req.recv_raw()
        self.assertEqual(new, old)

        router.close()
        req.close()


if __name__ == '__main__':
    unittest.main()
