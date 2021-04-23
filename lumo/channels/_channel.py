from abc import abstractmethod
from typing import Optional, Iterable, Tuple, List
from typing import TypeVar
from lumo.codecs import Codec

__all__ = 'CloseableChannel', \
          'InputChannel', 'AsyncInputChannel', \
          'OutputChannel', 'AsyncOutputChannel', \
          'Channel', 'AsyncChannel', \
          'select'

#

_T = TypeVar('_T')


class CloseableChannel:
    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def closed(self) -> bool: ...


class SelectableChannel(CloseableChannel):
    @abstractmethod
    def __select__(self): ...


class InputChannel(CloseableChannel):
    @abstractmethod
    def recv(self, tp: _T, codec: Optional[Codec[_T]] = None) -> _T: ...


class AsyncInputChannel(InputChannel, SelectableChannel):
    @abstractmethod
    def recv(self, tp: _T, codec: Optional[Codec[_T]] = None, timeout: Optional[float] = None) -> _T: ...


class OutputChannel(CloseableChannel):
    @abstractmethod
    def send(self, payload: _T, codec: Optional[Codec[_T]] = None) -> None: ...


class AsyncOutputChannel(OutputChannel, SelectableChannel):
    @abstractmethod
    def send(self, payload: _T, codec: Optional[Codec[_T]] = None, timeout: Optional[float] = None) -> None: ...


class Channel(InputChannel, OutputChannel):
    pass


class AsyncChannel(AsyncInputChannel, AsyncOutputChannel):
    pass


def select(
        r: Iterable[AsyncInputChannel],
        w: Iterable[AsyncOutputChannel],
        x: Iterable[SelectableChannel],
        timeout: Optional[float] = None
) -> Tuple[List[AsyncInputChannel], List[AsyncOutputChannel], List[SelectableChannel]]:
    from select import select
    rmap = {channel.__select__(): channel for channel in r if channel is not None}
    wmap = {channel.__select__(): channel for channel in w if channel is not None}
    xmap = {channel.__select__(): channel for channel in x if channel is not None}
    r, w, x = select(rmap.keys(), wmap.keys(), [], timeout)
    return [rmap[channel] for channel in r], [wmap[channel] for channel in w], [xmap[channel] for channel in x]
