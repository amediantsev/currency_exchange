import os

from currency_exchange.settings import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qkngi6q!7y74@lht)x2ivvzcd%^s@g0@_j$^78%$#nft828#dj'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

ALLOWED_HOSTS = ['*']

EMAIL_HOST_USER = 'testtestapp454545@gmail.com'
EMAIL_HOST_PASSWORD = 'qwerty123456qwerty'
STATIC_ROOT = os.path.join(BASE_DIR, '..', "static_content", 'static')

