import hashlib


def generate_rate_cache_key(source: int, currency:int) -> str:
    key = f'latest-rates-{source}-{currency}'.encode()
    return hashlib.md5(key).hexdigest()

    # hexdigest() переводит сложный объект хэша в шестнадцатиричную систему
