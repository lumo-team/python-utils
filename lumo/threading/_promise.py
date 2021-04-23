from threading import Condition
from time import time
from typing import Generic, TypeVar
from typing import Optional

__all__ = 'FutureException', 'CancelledException', 'Future', 'Promise'

_T = TypeVar('_T')


class FutureException(Exception):
    pass


class CancelledException(FutureException):
    pass


class SharedState(Generic[_T]):
    def __init__(self):
        self._lock = Condition()
        self._state = 0
        self._value = None
        self._error = None

    def result(self, value: _T) -> None:
        with self._lock:
            if self._state != 0:
                raise ValueError()
            self._value = value
            self._state = 1
            self._lock.notify_all()

    def error(self, error: Exception) -> None:
        with self._lock:
            if self._state != 0:
                raise ValueError()
            self._error = error
            self._state = 2
            self._lock.notify_all()

    def cancel(self) -> bool:
        with self._lock:
            if self._state != 0:
                return False
            self._state = 3
            self._lock.notify_all()
        return True

    def get(self) -> _T:
        with self._lock:
            while self._state == 0:
                self._lock.wait()
        if self._state == 1:
            return self._value
        elif self._state == 2:
            raise self._error
        else:
            raise CancelledException()

    def wait(self, timeout: Optional[float]) -> bool:
        now = time()
        with self._lock:
            while self._state == 0:
                if timeout is not None:
                    left = timeout - (time() - now)
                    if left <= 0:
                        return False
                    self._lock.wait(left)
                else:
                    self._lock.wait()
        return True

    @property
    def ready(self):
        return self._state != 0

    @property
    def done(self):
        return self._state == 1

    @property
    def failed(self):
        return self._state == 2

    @property
    def cancelled(self):
        return self._state == 3


class Future(Generic[_T]):
    def __init__(self, state: SharedState[_T]):
        self._state = state

    def get(self) -> _T:
        return self._state.get()

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._state.wait(timeout)

    def cancel(self) -> bool:
        return self._state.cancel()

    @property
    def ready(self):
        return self._state.ready

    @property
    def done(self):
        return self._state.done

    @property
    def failed(self):
        return self._state.failed

    @property
    def cancelled(self):
        return self._state.cancelled


class Promise(Future[_T]):
    def __init__(self):
        super().__init__(SharedState())

    def result(self, value: _T) -> None:
        self._state.result(value)

    def error(self, error: Exception) -> None:
        self._state.error(error)

    def cancel(self) -> bool:
        return self._state.cancel()

    def future(self) -> Future[_T]:
        return Future(self._state)
