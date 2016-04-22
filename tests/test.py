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


if __name__ == '__main__':
    unittest.main()
