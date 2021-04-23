from io import BytesIO
from select import select
from socket import socket
from threading import RLock
from time import time
from typing import Optional, Type
from typing import TypeVar

from lumo.codecs import Codec, CodecRegistry
from ._channel import AsyncChannel

__all__ = 'SocketChannel',

#

_T = TypeVar('_T')


class SocketChannel(AsyncChannel):
    def __init__(self, sock: socket, registry: Optional[CodecRegistry] = None):
        self._registry = registry
        self._wlock = RLock()
        self._rlock = RLock()
        self._socket = sock
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __select__(self):
        return self._socket if not self._closed else None

    def close(self) -> None:
        with self._wlock:
            if self._closed:
                return
            self._closed = True

    def send(self, payload: _T, codec: Optional[Codec[_T]] = None, timeout: Optional[float] = None) -> None:
        if codec is None:
            tp = type(payload)
            codec = self._registry.codec(tp)
            if codec is None:
                msg = f'No codec for type {tp.__name__}'
                raise ValueError(msg)

        with self._wlock:
            if self._closed:
                raise EOFError()

            encoder = codec.encoder(payload)
            stream = BytesIO()
            while encoder.has_remaining():
                encoder.encode(stream)
            buffer = bytes(stream.getbuffer())

            start = time()
            while buffer:
                if self._closed:
                    raise EOFError()

                if timeout is not None:
                    left = timeout - (time() - start)
                else:
                    left = None
                if left < 0:
                    raise TimeoutError()

                r, w, x = select([], [self._socket], [], left)
                if self._socket in w:
                    n = self._socket.send(buffer)
                    if n > 0:
                        buffer = buffer[n:]

    def recv(self, tp: Type[_T], codec: Optional[Codec[_T]] = None, timeout: Optional[float] = None) -> Optional[_T]:
        if codec is None:
            codec = self._registry.codec(tp)
            if codec is None:
                msg = f'No codec for class {tp.__name__}'
                raise ValueError(msg)

        buffer = b''
        decoder = codec.decoder()

        start = time()
        count = 0
        with self._rlock:
            while decoder.has_remaining():
                if self._closed:
                    if count > 0:
                        raise EOFError()
                    return None

                if timeout is not None:
                    left = timeout - (time() - start)
                else:
                    left = None
                if left < 0:
                    raise TimeoutError()

                r, w, x = select([self._socket], [], [], left)
                if self._socket in r:
                    data = self._socket.recv(decoder.remaining())
                    if data is None:
                        continue
                    count += len(data)
                    if not data:
                        if count > 0:
                            raise EOFError()
                        return None
                    buffer += data

            return decoder.get()

    @property
    def closed(self) -> bool:
        return self._closed
