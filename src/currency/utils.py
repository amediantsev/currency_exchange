import hashlib


def generate_rate_cache_key(source: int, currency:int) -> str:
    key = f'latest-rates-{source}-{currency}'.encode()
    return hashlib.md5(key).hexdigest()

    # hexdigest() переводит сложный объект хэша в шестнадцатиричную систему


def save_rate(last_rate, new_rate):
    if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
        new_rate.save()
