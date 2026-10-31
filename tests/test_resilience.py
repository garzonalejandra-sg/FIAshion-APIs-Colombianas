import pytest
from app.infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from app.infrastructure.resilience.retry import retry
import httpx

def test_circuit_breaker_opens_and_recovers(monkeypatch):
    clock = {"now": 0.0}
    monkeypatch.setattr("app.infrastructure.resilience.circuit_breaker.time.monotonic",
                        lambda: clock["now"])
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
    def fail():
        raise RuntimeError("offline")
    for _ in range(2):
        with pytest.raises(RuntimeError):
            breaker.call(fail)
    assert breaker.state == CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        breaker.call(lambda: "ok")
    clock["now"] = 6
    assert breaker.call(lambda: "ok") == "ok"
    assert breaker.state == CircuitState.CLOSED

def test_retry_reintenta_errores_temporales():
    calls = {"n": 0}
    def operation():
        calls["n"] += 1
        return httpx.Response(503 if calls["n"] < 3 else 200, request=httpx.Request("GET", "https://test.local"))
    result = retry(operation, max_attempts=3, base_delay=0, sleep=lambda _: None)
    assert result.status_code == 200
    assert calls["n"] == 3

def test_retry_no_reintenta_error_permanente():
    calls = {"n": 0}
    def operation():
        calls["n"] += 1
        return httpx.Response(404, request=httpx.Request("GET", "https://test.local"))
    with pytest.raises(httpx.HTTPStatusError):
        retry(operation, max_attempts=3, base_delay=0, sleep=lambda _: None)
    assert calls["n"] == 1
