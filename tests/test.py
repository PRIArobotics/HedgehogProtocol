import unittest
import zmq
from hedgehog.protocol import messages, sockets
from hedgehog.protocol.messages import ack, io, analog, digital, motor, servo, process


class TestMessages(unittest.TestCase):
    def test_acknowledgement(self):
        old = ack.Acknowledgement()
        new = messages.parse(old.serialize())
        self.assertEqual(new.code, old.code)
        self.assertEqual(new.message, old.message)

    def test_io_state_action(self):
        old = io.StateAction(0, io.ANALOG_PULLDOWN)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.flags, old.flags)

    def test_analog_request(self):
        old = analog.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_analog_update(self):
        old = analog.Update(0, 2)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.value, old.value)

    def test_digital_request(self):
        old = digital.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_digital_update(self):
        old = digital.Update(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.value, old.value)

    def test_motor_action(self):
        old = motor.Action(0, motor.POWER, 100, relative=-100)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.state, old.state)
        self.assertEqual(new.amount, old.amount)
        self.assertEqual(new.reached_state, old.reached_state)
        self.assertEqual(new.relative, old.relative)
        self.assertEqual(new.absolute, old.absolute)

    def test_motor_request(self):
        old = motor.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_motor_update(self):
        old = motor.Update(0, 100, 1000)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.velocity, old.velocity)
        self.assertEqual(new.position, old.position)

    def test_motor_state_update(self):
        old = motor.StateUpdate(0, motor.POWER)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.state, old.state)

    def test_motor_set_position_action(self):
        old = motor.SetPositionAction(0, 0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.position, old.position)

    def test_servo_action(self):
        old = servo.Action(0, 512)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.position, old.position)

    def test_servo_state_action(self):
        old = servo.StateAction(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.active, old.active)

    def test_process_execute_request(self):
        old = process.ExecuteRequest('cat', working_dir='/home/hedgehog')
        new = messages.parse(old.serialize())
        self.assertEqual(new.args, old.args)
        self.assertEqual(new.working_dir, old.working_dir)

    def test_process_stream_action(self):
        old = process.StreamAction(123, process.STDIN, b'abc')
        new = messages.parse(old.serialize())
        self.assertEqual(new.pid, old.pid)
        self.assertEqual(new.fileno, old.fileno)
        self.assertEqual(new.chunk, old.chunk)

    def test_process_stream_update(self):
        old = process.StreamUpdate(123, process.STDIN, b'abc')
        new = messages.parse(old.serialize())
        self.assertEqual(new.pid, old.pid)
        self.assertEqual(new.fileno, old.fileno)
        self.assertEqual(new.chunk, old.chunk)

    def test_process_exit_update(self):
        old = process.ExitUpdate(123, 0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.pid, old.pid)
        self.assertEqual(new.exit_code, old.exit_code)


class TestSockets(unittest.TestCase):
    def test_sockets(self):
        context = zmq.Context()
        endpoint = "inproc://test"
        router = context.socket(zmq.ROUTER)
        router.bind(endpoint)
        router = sockets.DealerRouterWrapper(router)
        req = context.socket(zmq.REQ)
        req.connect(endpoint)
        req = sockets.ReqWrapper(req)

        old = [analog.Request(0), digital.Request(0)]
        req.send_multipart(old)
        header, new = router.recv_multipart()
        self.assertEqual(new[0].port, old[0].port)
        self.assertEqual(new[1].port, old[1].port)

        old = [analog.Update(0, 100), digital.Update(0, True)]
        router.send_multipart(header, old)
        new = req.recv_multipart()
        self.assertEqual(new[0].port, old[0].port)
        self.assertEqual(new[0].value, old[0].value)
        self.assertEqual(new[1].port, old[1].port)
        self.assertEqual(new[1].value, old[1].value)

        router.close()
        req.close()


if __name__ == '__main__':
    unittest.main()
