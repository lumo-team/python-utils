from abc import abstractmethod
from typing import Optional, Union, ForwardRef

from ._codec import *

__all__ = 'CodecContext', 'CodecRegistry',


class CodecContext:
    def __init__(self, registry: 'CodecRegistry'):
        self.registry = registry

    def codec(self, descriptor: Union[type, ForwardRef, str]) -> Optional[Codec]:
        return self.registry.codec(descriptor, self)


class CodecRegistry:
    @abstractmethod
    def codec(
            self,
            descriptor: Union[type, ForwardRef, str],
            context: Optional[CodecContext] = None
    ) -> Optional[Codec]:
        ...

    @abstractmethod
    def register(self, descriptor: type, codec: Codec): ...

    @abstractmethod
    def unregister(self, descriptor: type, codec: Codec): ...
