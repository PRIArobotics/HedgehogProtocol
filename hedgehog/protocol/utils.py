import zmq


class Killer:
    def __init__(self, context=None):
        self.context = context or zmq.Context.instance()
        self.endpoint = 'inproc://killer'
        self.sender = self.context.socket(zmq.PAIR)
        self.sender.bind(self.endpoint)

    def connect_receiver(self):
        receiver = self.context.socket(zmq.PAIR)
        receiver.connect(self.endpoint)
        return receiver

    def kill(self):
        self.sender.send(b'')
        self.sender.close()
