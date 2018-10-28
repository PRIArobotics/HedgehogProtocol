import pytest
from hedgehog.utils.test_utils import event_loop, zmq_ctx, zmq_aio_ctx

import zmq.asyncio
from hedgehog.protocol import errors, sockets, async_sockets, CommSide, ServerSide, ClientSide
from hedgehog.protocol.proto.hedgehog_pb2 import HedgehogMessage
from hedgehog.protocol.proto.subscription_pb2 import Subscription
from hedgehog.protocol.messages import Message, ack, io, analog, digital, motor, servo, process


# Pytest fixtures
event_loop, zmq_ctx, zmq_aio_ctx


class TestMessages(object):
    def assertTransmission(self, msg: Message, wire: HedgehogMessage, sender: CommSide, receiver: CommSide, is_async: bool=False):
        assert msg.is_async == is_async
        on_wire = sender.serialize(msg)
        assert on_wire == wire.SerializeToString()
        received = receiver.parse(on_wire)
        assert received == msg
        assert received.is_async == is_async

    def assertTransmissionClientServer(self, msg: Message, wire: HedgehogMessage, is_async: bool=False):
        self.assertTransmission(msg, wire, ClientSide, ServerSide, is_async)

    def assertTransmissionServerClient(self, msg: Message, wire: HedgehogMessage, is_async: bool=False):
        self.assertTransmission(msg, wire, ServerSide, ClientSide, is_async)

    def test_parse_invalid(self):
        proto = HedgehogMessage()
        proto.io_action.flags = io.OUTPUT | io.PULLUP
        with pytest.raises(errors.InvalidCommandError):
            ServerSide.parse(proto.SerializeToString())

    def test_parse_unknown(self):
        proto = HedgehogMessage()
        proto.io_action.flags = io.OUTPUT | io.PULLUP
        with pytest.raises(errors.UnknownCommandError):
            ClientSide.parse(proto.SerializeToString())

    def test_parse_malformed(self):
        with pytest.raises(errors.UnknownCommandError):
            ServerSide.parse(b'asdf')

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

    def test_io_action(self):
        msg = io.Action(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_action.flags = io.INPUT_PULLDOWN
        self.assertTransmissionClientServer(msg, proto)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLUP)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.OUTPUT | io.PULLDOWN)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.LEVEL)

        with pytest.raises(errors.InvalidCommandError):
            io.Action(0, io.PULLUP | io.PULLDOWN)

    def test_io_command_request(self):
        msg = io.CommandRequest(0)
        proto = HedgehogMessage()
        proto.io_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_io_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = io.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.io_command_message.subscription.subscribe = True
        proto.io_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_io_command_reply(self):
        msg = io.CommandReply(0, io.INPUT_PULLDOWN)
        proto = HedgehogMessage()
        proto.io_command_message.flags = io.INPUT_PULLDOWN
        self.assertTransmissionServerClient(msg, proto)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLUP)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.OUTPUT | io.PULLDOWN)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.LEVEL)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandReply(0, io.PULLUP | io.PULLDOWN)

    def test_io_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = io.CommandUpdate(0, io.INPUT_PULLDOWN, sub)
        proto = HedgehogMessage()
        proto.io_command_message.flags = io.INPUT_PULLDOWN
        proto.io_command_message.subscription.subscribe = True
        proto.io_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        assert not msg.output
        assert not msg.pullup
        assert msg.pulldown
        assert not msg.level

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.OUTPUT | io.PULLUP, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.OUTPUT | io.PULLDOWN, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.LEVEL, sub)

        with pytest.raises(errors.InvalidCommandError):
            io.CommandUpdate(0, io.PULLUP | io.PULLDOWN, sub)

    def test_analog_request(self):
        msg = analog.Request(0)
        proto = HedgehogMessage()
        proto.analog_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_analog_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        sub.int_granularity = 20
        sub.granularity_timeout = 200
        msg = analog.Subscribe(0, sub)
        proto = HedgehogMessage()
        proto.analog_message.subscription.subscribe = True
        proto.analog_message.subscription.timeout = 10
        proto.analog_message.subscription.int_granularity = 20
        proto.analog_message.subscription.granularity_timeout = 200
        self.assertTransmissionClientServer(msg, proto)

    def test_analog_reply(self):
        msg = analog.Reply(0, 2)
        proto = HedgehogMessage()
        proto.analog_message.value = 2
        self.assertTransmissionServerClient(msg, proto)

    def test_analog_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        sub.int_granularity = 20
        sub.granularity_timeout = 200
        msg = analog.Update(0, 2, sub)
        proto = HedgehogMessage()
        proto.analog_message.value = 2
        proto.analog_message.subscription.subscribe = True
        proto.analog_message.subscription.timeout = 10
        proto.analog_message.subscription.int_granularity = 20
        proto.analog_message.subscription.granularity_timeout = 200
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_digital_request(self):
        msg = digital.Request(0)
        proto = HedgehogMessage()
        proto.digital_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_digital_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        msg = digital.Subscribe(0, sub)
        proto = HedgehogMessage()
        proto.digital_message.subscription.subscribe = True
        self.assertTransmissionClientServer(msg, proto)

    def test_digital_reply(self):
        msg = digital.Reply(0, True)
        proto = HedgehogMessage()
        proto.digital_message.value = True
        self.assertTransmissionServerClient(msg, proto)

    def test_digital_update(self):
        sub = Subscription()
        sub.subscribe = True
        msg = digital.Update(0, True, sub)
        proto = HedgehogMessage()
        proto.digital_message.value = True
        proto.digital_message.subscription.subscribe = True
        self.assertTransmissionServerClient(msg, proto, is_async=True)

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

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, relative=100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 100, reached_state=motor.BRAKE)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.BRAKE, 100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, -100, absolute=100)

        with pytest.raises(errors.InvalidCommandError):
            motor.Action(0, motor.POWER, 0, relative=100)

    def test_motor_command_request(self):
        msg = motor.CommandRequest(0)
        proto = HedgehogMessage()
        proto.motor_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.motor_command_message.subscription.subscribe = True
        proto.motor_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_command_reply(self):
        msg = motor.CommandReply(0, motor.POWER, 1000)
        proto = HedgehogMessage()
        proto.motor_command_message.amount = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.CommandUpdate(0, motor.POWER, 1000, sub)
        proto = HedgehogMessage()
        proto.motor_command_message.amount = 1000
        proto.motor_command_message.subscription.subscribe = True
        proto.motor_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_motor_state_request(self):
        msg = motor.StateRequest(0)
        proto = HedgehogMessage()
        proto.motor_state_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_state_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.StateSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.motor_state_message.subscription.subscribe = True
        proto.motor_state_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_motor_state_reply(self):
        msg = motor.StateReply(0, 100, 1000)
        proto = HedgehogMessage()
        proto.motor_state_message.velocity = 100
        proto.motor_state_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

    def test_motor_state_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = motor.StateUpdate(0, 100, 1000, sub)
        proto = HedgehogMessage()
        proto.motor_state_message.velocity = 100
        proto.motor_state_message.position = 1000
        proto.motor_state_message.subscription.subscribe = True
        proto.motor_state_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

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

        msg = servo.Action(0, False)
        proto = HedgehogMessage()
        proto.servo_action.active = False
        self.assertTransmissionClientServer(msg, proto)

        with pytest.raises(errors.InvalidCommandError):
            servo.Action(0, True)

    def test_servo_command_request(self):
        msg = servo.CommandRequest(0)
        proto = HedgehogMessage()
        proto.servo_command_message.SetInParent()
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_subscribe(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = servo.CommandSubscribe(0, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.SetInParent()
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionClientServer(msg, proto)

    def test_servo_command_reply(self):
        msg = servo.CommandReply(0, True, 1000)
        proto = HedgehogMessage()
        proto.servo_command_message.active = True
        proto.servo_command_message.position = 1000
        self.assertTransmissionServerClient(msg, proto)

        msg = servo.CommandReply(0, False, 0)
        proto = HedgehogMessage()
        proto.servo_command_message.active = False
        self.assertTransmissionServerClient(msg, proto)

    def test_servo_command_update(self):
        sub = Subscription()
        sub.subscribe = True
        sub.timeout = 10
        msg = servo.CommandUpdate(0, True, 1000, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.active = True
        proto.servo_command_message.position = 1000
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        msg = servo.CommandUpdate(0, False, 0, sub)
        proto = HedgehogMessage()
        proto.servo_command_message.active = False
        proto.servo_command_message.subscription.subscribe = True
        proto.servo_command_message.subscription.timeout = 10
        self.assertTransmissionServerClient(msg, proto, is_async=True)

    def test_process_execute_action(self):
        msg = process.ExecuteAction('cat', working_dir='/home/pi')
        proto = HedgehogMessage()
        proto.process_execute_action.args.append('cat')
        proto.process_execute_action.working_dir = '/home/pi'
        self.assertTransmissionClientServer(msg, proto)

        msg = process.ExecuteAction('cat')
        proto = HedgehogMessage()
        proto.process_execute_action.args.append('cat')
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

        with pytest.raises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDOUT, b'abc')

        with pytest.raises(errors.InvalidCommandError):
            process.StreamAction(123, process.STDERR, b'abc')

    def test_process_stream_update(self):
        msg = process.StreamUpdate(123, process.STDOUT, b'abc')
        proto = HedgehogMessage()
        proto.process_stream_message.pid = 123
        proto.process_stream_message.fileno = process.STDOUT
        proto.process_stream_message.chunk = b'abc'
        self.assertTransmissionServerClient(msg, proto, is_async=True)

        with pytest.raises(errors.InvalidCommandError):
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
        self.assertTransmissionServerClient(msg, proto, is_async=True)


class TestSockets(object):
    def test_raw_to_from_delimited(self):
        header = (b'asdf',)
        raw_payload = (b'foo', b'bar')

        delimited = sockets.raw_to_delimited(header, raw_payload)
        assert delimited == (b'asdf', b'', b'foo', b'bar')
        assert sockets.raw_from_delimited(delimited) == (header, raw_payload)

    def test_to_from_delimited(self):
        header = (b'asdf',)
        payload = (io.Action(0, io.INPUT_PULLUP), servo.Action(0, False))
        raw1, raw2 = [ClientSide.serialize(msg) for msg in payload]

        delimited = sockets.to_delimited(header, payload, ClientSide)
        assert delimited == (b'asdf', b'', raw1, raw2)
        assert sockets.from_delimited(delimited, ServerSide) == (header, payload)

    def test_sockets_msg(self, zmq_ctx):
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = sockets.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = analog.Request(1)  # type: Message
            req.send_msg(old)
            header, new = router.recv_msg()
            assert new == old

            old = analog.Reply(1, 200)
            router.send_msg(header, old)
            new = req.recv_msg()
            assert new == old

    def test_sockets_msgs(self, zmq_ctx):
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = sockets.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [analog.Request(0), digital.Request(0)]
            req.send_msgs(olds)
            header, news = router.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

            olds = [analog.Reply(0, 100), digital.Reply(0, True)]
            router.send_msgs(header, olds)
            news = req.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

    def test_sockets_msg_raw(self, zmq_ctx):
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = sockets.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = b'as'
            req.send_msg_raw(old)
            header, new = router.recv_msg_raw()
            assert new == old

            old = b'df'
            router.send_msg_raw(header, old)
            new = req.recv_msg_raw()
            assert new == old

    def test_sockets_msgs_raw(self, zmq_ctx):
        endpoint = "inproc://test"

        router = sockets.DealerRouterSocket(zmq_ctx, zmq.ROUTER, side=ServerSide)
        req = sockets.ReqSocket(zmq_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [b'as', b'df']
            req.send_msgs_raw(olds)
            header, news = router.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

            olds = [b'fd', b'sa']
            router.send_msgs_raw(header, olds)
            news = req.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

    @pytest.mark.asyncio
    async def test_async_sockets_msg(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = async_sockets.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = async_sockets.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = analog.Request(1)  # type: Message
            await req.send_msg(old)
            header, new = await router.recv_msg()
            assert new == old

            old = analog.Reply(1, 200)
            await router.send_msg(header, old)
            new = await req.recv_msg()
            assert new == old

    @pytest.mark.asyncio
    async def test_async_sockets_msgs(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = async_sockets.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = async_sockets.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [analog.Request(0), digital.Request(0)]
            await req.send_msgs(olds)
            header, news = await router.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

            olds = [analog.Reply(0, 100), digital.Reply(0, True)]
            await router.send_msgs(header, olds)
            news = await req.recv_msgs()
            for old, new in zip(olds, news):
                assert new == old

    @pytest.mark.asyncio
    async def test_async_sockets_msg_raw(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = async_sockets.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = async_sockets.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            old = b'as'
            await req.send_msg_raw(old)
            header, new = await router.recv_msg_raw()
            assert new == old

            old = b'df'
            await router.send_msg_raw(header, old)
            new = await req.recv_msg_raw()
            assert new == old

    @pytest.mark.asyncio
    async def test_async_sockets_msgs_raw(self, zmq_aio_ctx):
        endpoint = "inproc://test"

        router = async_sockets.DealerRouterSocket(zmq_aio_ctx, zmq.ROUTER, side=ServerSide)
        req = async_sockets.ReqSocket(zmq_aio_ctx, zmq.REQ, side=ClientSide)
        with router, req:
            router.bind(endpoint)
            req.connect(endpoint)

            olds = [b'as', b'df']
            await req.send_msgs_raw(olds)
            header, news = await router.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old

            olds = [b'fd', b'sa']
            await router.send_msgs_raw(header, olds)
            news = await req.recv_msgs_raw()
            for old, new in zip(olds, news):
                assert new == old
