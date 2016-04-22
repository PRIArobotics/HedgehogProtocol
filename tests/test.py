import unittest
from hedgehog.protocol import messages
from hedgehog.protocol.messages import analog, digital


class TestMessages(unittest.TestCase):
    def test_analog_request(self):
        payload = [0, 1]

        msg = messages.analog.Request(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)

    def test_analog_update(self):
        payload = {0: 2, 1: 1000}

        msg = messages.analog.Update(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)

    def test_analog_state_action(self):
        payload = {
            0: messages.analog.StateAction.State(True),
            1: messages.analog.StateAction.State(False),
        }

        msg = messages.analog.StateAction(payload)
        msg = messages.parse(msg.serialize())
        self.assertEqual(msg.sensors, payload)

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
