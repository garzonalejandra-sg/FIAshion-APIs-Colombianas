import time
import httpx

RETRYABLE = (httpx.TimeoutException, httpx.ConnectError)

def retry(operation, max_attempts=3, base_delay=0.25, sleep=time.sleep):
    for attempt in range(max_attempts):
        try:
            response = operation()
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == max_attempts - 1:
                    response.raise_for_status()
                sleep(base_delay * (2 ** attempt))
                continue
            response.raise_for_status()
            return response
        except RETRYABLE:
            if attempt == max_attempts - 1:
                raise
            sleep(base_delay * (2 ** attempt))
    raise RuntimeError("Retry attempts exhausted")
