from hedgehog.protocol import CommSide
from hedgehog.utils.zmq.trio import Socket

from . import raw_to_delimited, to_delimited, raw_from_delimited, from_delimited
from .asyncio import DealerRouterMixin, ReqMixin

__all__ = [
    'raw_to_delimited', 'to_delimited', 'raw_from_delimited', 'from_delimited',
    'DealerRouterMixin', 'DealerRouterSocket', 'ReqMixin', 'ReqSocket',
]


class DealerRouterSocket(DealerRouterMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(DealerRouterSocket, self).__init__(*args, **kwargs)
        self.side = side


class ReqSocket(ReqMixin, Socket):
    side = None

    def __init__(self, *args, side: CommSide, **kwargs) -> None:
        super(ReqSocket, self).__init__(*args, **kwargs)
        self.side = side
