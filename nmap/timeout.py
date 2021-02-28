import ctypes
import threading
from typing import Type

NULL = 0

"""
import nmap
try:
    with nmap.TimeoutAfter(timeout=1):
        nm = nmap.PortScanner()
        nm.scan('127.0.0.1', '22-40043')
        print(nm.all_hosts())
except nmap.TimeoutException:
    print('Timeout reached')
"""


class TimeoutException(Exception):
    pass


class TimeoutAfter:
    def __init__(self, timeout: int, exception: Type[Exception] = TimeoutException):
        self._exception = exception
        self._caller_thread = threading.current_thread()
        self._timeout = timeout
        self._timer = threading.Timer(self._timeout, self.raise_caller)
        self._timer.daemon = True
        self._timer.start()

    def __enter__(self):
        try:
            yield
        finally:
            self._timer.cancel()

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._timer.cancel()

    def raise_caller(self):
        ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self._caller_thread._ident), ctypes.py_object(self._exception)
        )
        if ret == 0:
            raise ValueError("Invalid thread ID")
        elif ret > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self._caller_thread._ident, NULL)
            raise SystemError("PyThreadState_SetAsyncExc failed")
