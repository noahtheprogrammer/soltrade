import time
from functools import wraps

from solana.exceptions import SolanaRpcException
from soltrade.log import log_general

def handle_rate_limiting(retry_attempts=3, retry_delay=10):
    def decorator(client_function):
        @wraps(client_function)
        def wrapper(*args, **kwargs):
            for _ in range(retry_attempts):
                try:
                    return client_function(*args, **kwargs)
                except SolanaRpcException as e:
                    if 'HTTPStatusError' in e.error_msg:
                        log_general.warning(f"Rate limit exceeded in {client_function.__name__}, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        raise
            log_general.warning("Rate limit error persisting, skipping this iteration.")
            return None

        return wrapper

    return decorator
