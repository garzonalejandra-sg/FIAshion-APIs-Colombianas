import time
from enum import Enum

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"

class CircuitOpenError(RuntimeError):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=20):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.opened_at = None
        self.state = CircuitState.CLOSED

    def call(self, operation, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.opened_at < self.recovery_timeout:
                raise CircuitOpenError("Circuit is OPEN")
            self.state = CircuitState.HALF_OPEN
        try:
            result = operation(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.state == CircuitState.HALF_OPEN or self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.monotonic()
            raise
        self.failures = 0
        self.state = CircuitState.CLOSED
        return result
