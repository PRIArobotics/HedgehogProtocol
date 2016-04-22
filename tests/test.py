import unittest
from hedgehog.protocol import messages
from hedgehog.protocol.messages import analog, digital


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
        payload = [0, 1]

        msg = messages.digital.Request(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)

    def test_digital_update(self):
        payload = {0: True, 1: False}

        msg = messages.digital.Update(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)

    def test_digital_state_action(self):
        payload = {
            0: messages.digital.StateAction.State(True, False),
            1: messages.digital.StateAction.State(False, True),
        }

        msg = messages.digital.StateAction(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)


if __name__ == '__main__':
    unittest.main()
