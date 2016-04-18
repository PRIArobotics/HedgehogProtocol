import zmq


class Killer:
    """
    `Killer` is a simple signaler using a pair of ZMQ sockets over the `inproc` transport.

    The name-giving use case is killing a thread that, other than being killable, runs an infinite loop:

        killer = Killer()

        def worker():
            kill_socket = killer.connect_receiver()
            while True:
                # include other relevant sockets in the select
                pollin, _, _ = zmq.select([kill_socket], [], [])
                # check other sockets
                if kill_socket in pollin:
                    break
            kill_socket.close()

        threading.Thread(target=worker).start()

        # ...

        killer.kill()

    Of course, `Killer` can also be used for other use cases of one-time `inproc` signaling.
    """

    def __init__(self):
        """Creates a `Killer`, including a sender socket for the kill signal."""
        self.context = zmq.Context()
        self.endpoint = 'inproc://killer'
        self.sender = self.context.socket(zmq.PAIR)
        self.sender.bind(self.endpoint)

    def connect_receiver(self):
        """Connects a PAIR socket to the one opened at construction time."""
        receiver = self.context.socket(zmq.PAIR)
        receiver.connect(self.endpoint)
        return receiver

    def kill(self):
        """Sends a message to the connected PAIR socket and the closes the sender socket."""
        self.sender.send(b'')
        self.sender.close()
