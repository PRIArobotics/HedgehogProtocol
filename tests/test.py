import unittest
from hedgehog.protocol import messages


class TestMessages(unittest.TestCase):
    def test_analog_request(self):
        msg = messages.AnalogRequest([0, 1])
        self.assertEqual(msg.WhichOneof('command'), 'analog_request')
        self.assertEqual(msg.analog_request.sensors, [0, 1])

    def test_analog_update(self):
        msg = messages.AnalogUpdate({0: 2, 1: 1000})
        self.assertEqual(msg.WhichOneof('command'), 'analog_update')
        self.assertEqual(msg.analog_update.sensors, {0: 2, 1: 1000})

    def test_analog_state_action(self):
        msg = messages.AnalogStateAction({0: messages.AnalogState(True)})
        self.assertEqual(msg.WhichOneof('command'), 'analog_state_action')
        self.assertEqual(len(msg.analog_state_action.sensors), 1)
        self.assertEqual(msg.analog_state_action.sensors.get(0).pullup, True)

    def test_digital_request(self):
        msg = messages.DigitalRequest([0, 1])
        self.assertEqual(msg.WhichOneof('command'), 'digital_request')
        self.assertEqual(msg.digital_request.sensors, [0, 1])

    def test_digital_update(self):
        msg = messages.DigitalUpdate({0: True, 1: False})
        self.assertEqual(msg.WhichOneof('command'), 'digital_update')
        self.assertEqual(msg.digital_update.sensors, {0: True, 1: False})

    def test_digital_state_action(self):
        msg = messages.DigitalStateAction({0: messages.DigitalState(True, False)})
        self.assertEqual(msg.WhichOneof('command'), 'digital_state_action')
        self.assertEqual(len(msg.digital_state_action.sensors), 1)
        self.assertEqual(msg.digital_state_action.sensors.get(0).pullup, True)
        self.assertEqual(msg.digital_state_action.sensors.get(0).output, False)

    def test_digital_action(self):
        msg = messages.DigitalAction({0: True, 1: False})
        self.assertEqual(msg.WhichOneof('command'), 'digital_action')
        self.assertEqual(msg.digital_action.sensors, {0: True, 1: False})


if __name__ == '__main__':
    unittest.main()
