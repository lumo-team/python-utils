from typing import Any, Optional, Union, Tuple, Dict, Callable
from typing import Generic, ForwardRef, get_origin, get_args
from collections import abc
import sys


__all__ = 'eval_type',


def eval_type(
        descriptor: Union[type, ForwardRef, str],
        namespace: Union[Dict[str, Any], type, None] = None,
        locals: Optional[Dict[str, Any]] = None
) -> type:
    if isinstance(descriptor, type):
        return descriptor

    if isinstance(namespace, type):
        if locals is None:
            locals = namespace.__dict__
        namespace = sys.modules[namespace.__module__].__dict__

    if isinstance(descriptor, ForwardRef):
        descriptor = descriptor.__forward_arg__

    if isinstance(descriptor, str):
        descriptor = eval(descriptor, namespace, locals)

    if isinstance(descriptor, type):
        return descriptor
    if descriptor is Generic:
        return descriptor

    origin = get_origin(descriptor)
    if origin is None:
        return descriptor

    args = get_args(descriptor)

    if origin is abc.Callable:
        args = [eval_type(arg, namespace, locals) for arg in args[0]], eval_type(args[1], namespace, locals)
        return Callable[args]

    args = tuple(eval_type(arg, namespace, locals) for arg in args)
    if origin is tuple:
        return Tuple[args]

    return descriptor.copy_with(args)
