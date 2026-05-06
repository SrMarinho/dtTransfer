import secrets

_current_hash: str = ''


def set_run_hash(hash_: str = '') -> str:
    global _current_hash
    _current_hash = hash_ or secrets.token_hex(3)
    return _current_hash


def get_run_hash() -> str:
    return _current_hash


def clear_run_hash() -> None:
    global _current_hash
    _current_hash = ''
