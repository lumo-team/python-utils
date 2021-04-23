from abc import abstractmethod
from typing import BinaryIO
from typing import Generic, TypeVar

__all__ = 'Encoder', 'Decoder', 'Codec',

_T = TypeVar('_T')


#


class Encoder(Generic[_T]):
    @abstractmethod
    def encode(self, stream: BinaryIO) -> int: ...

    @abstractmethod
    def remaining(self) -> int: ...

    def has_remaining(self) -> bool:
        return self.remaining() > 0


class Decoder(Generic[_T]):
    @abstractmethod
    def get(self) -> _T: ...

    @abstractmethod
    def decode(self, stream: BinaryIO) -> int: ...

    @abstractmethod
    def remaining(self) -> int: ...

    def has_remaining(self) -> bool:
        return self.remaining() > 0


class Codec(Generic[_T]):
    @abstractmethod
    def encoder(self, value: _T) -> Encoder[_T]: ...

    @abstractmethod
    def decoder(self) -> Decoder[_T]: ...
