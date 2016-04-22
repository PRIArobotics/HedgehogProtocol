import unittest
from hedgehog.protocol import messages
from hedgehog.protocol.messages import analog, digital, motor, servo


class TestMessages(unittest.TestCase):
    def test_analog_request(self):
        old = messages.analog.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_analog_update(self):
        old = messages.analog.Update(0, 2)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.value, old.value)

    def test_analog_state_action(self):
        old = messages.analog.StateAction(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.pullup, old.pullup)

    def test_digital_request(self):
        old = messages.digital.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_digital_update(self):
        old = messages.digital.Update(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.value, old.value)

    def test_digital_state_action(self):
        old = messages.digital.StateAction(0, True, False)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.pullup, old.pullup)
        self.assertEqual(new.output, old.output)

    def test_digital_action(self):
        old = messages.digital.Action(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.level, old.level)

    def test_motor_action(self):
        old = messages.motor.Action(0, messages.motor.POWER, 0, relative=-100)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.state, old.state)
        self.assertEqual(new.amount, old.amount)
        self.assertEqual(new.reached_state, old.reached_state)
        self.assertEqual(new.relative, old.relative)
        self.assertEqual(new.absolute, old.absolute)

    def test_motor_request(self):
        old = messages.motor.Request(0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)

    def test_motor_update(self):
        old = messages.motor.Update(0, 100, 1000)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.velocity, old.velocity)
        self.assertEqual(new.position, old.position)

    def test_motor_state_update(self):
        old = messages.motor.StateUpdate(0, messages.motor.POWER)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.state, old.state)

    def test_motor_set_position_action(self):
        old = messages.motor.SetPositionAction(0, 0)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.position, old.position)

    def test_servo_action(self):
        old = messages.servo.Action(0, 512)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.position, old.position)

    def test_servo_state_action(self):
        old = messages.servo.StateAction(0, True)
        new = messages.parse(old.serialize())
        self.assertEqual(new.port, old.port)
        self.assertEqual(new.active, old.active)


if __name__ == '__main__':
    unittest.main()
