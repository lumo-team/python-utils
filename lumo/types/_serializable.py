from typing import Any, Union, Tuple, Mapping, Dict, ForwardRef
from typing import Generic, TypeVar, ClassVar, get_type_hints, get_origin, get_args
import sys


__all__ = 'SerializableMeta', 'Serializable'


_T = TypeVar('_T', bound='Serializable')


def _fields(annotations: Dict[str, type], result: Dict[str, type]):
    for key, value in annotations.items():
        if key.startswith('_') or get_origin(value) is ClassVar:
            continue
        if isinstance(value, str):
            value = ForwardRef(value)
        result[key] = value


class SerializableMeta(type):
    __fields__: Mapping[str, type]

    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]):
        if '__fields__' not in namespace:
            fields = {}
            for base in bases:
                _fields(get_type_hints(base), fields)
            _fields(namespace.get('__annotations__', {}), fields)
            namespace['__fields__'] = fields

        return super().__new__(mcs, name, bases, namespace)


class Serializable(Generic[_T], metaclass=SerializableMeta):
    __fields__: Mapping[str, type]

    def dump(self) -> Mapping[str, Any]:
        result = {}
        for key in self.__fields__:
            result[key] = getattr(self, key)
        return result

    @classmethod
    def load(cls, namespace: Mapping[str, Any]) -> _T:
        result = object.__new__(cls)
        for key, type in cls.__fields__.items():
            if get_origin(type) is Union and None in get_args(type):
                value = namespace.get(key, None)
            else:
                value = namespace[key]
            setattr(result, key, value)
        return result
