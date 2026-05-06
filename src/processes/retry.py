import threading
from src.core.logger.logging import logger


def connect_with_retry(
    driver,
    name: str,
    stop_event: threading.Event,
    max_tries: int = 3,
    base_delay: float = 30.0,
    max_delay: float = 120.0,
):
    """Returns a connection or None if retries exhausted or stop_event is set."""
    tries = 0
    while True:
        try:
            return driver.connection()
        except Exception as e:
            logger.debug(str(e))
            if tries >= max_tries:
                logger.error(f"{name} - não foi possivel estabelecer conexão. Encerrando.")
                return None
            tries += 1
            delay = min(base_delay * (2 ** (tries - 1)), max_delay)
            logger.warning(f"{name} - Erro ao tentar criar conexao, tentando novamente em {delay} segundos")
            if stop_event.wait(delay):
                return None
