import unittest
import hedgehog.protocol


class TestProto(unittest.TestCase):
    def test_analog_request(self):
        msg = hedgehog.protocol.AnalogRequest([0, 1])
        self.assertEqual(msg.WhichOneof('command'), 'analog_request')
        self.assertEqual(msg.analog_request.sensors, [0, 1])

    def test_analog_update(self):
        msg = hedgehog.protocol.AnalogUpdate({0: 2, 1: 1000})
        self.assertEqual(msg.WhichOneof('command'), 'analog_update')
        self.assertEqual(msg.analog_update.sensors, {0: 2, 1: 1000})


if __name__ == '__main__':
    unittest.main()
