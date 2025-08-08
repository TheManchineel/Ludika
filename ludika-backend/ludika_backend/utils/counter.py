from threading import Lock

class AtomicCounter:
    def __init__(self, initial_value=0):
        self._value = initial_value
        self._lock = Lock()

    def increment(self, amount=1):
        with self._lock:
            self._value += amount
            return self._value

    def get_value(self):
        with self._lock:
            return self._value

    def reset(self):
        with self._lock:
            self._value = 0