from currency_exchange.settings import *

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.outbox'
SECRET_KEY = 'dasfdsgfrewgreqg43'
ALLOWED_HOSTS = ['*']

CELERY_ALWAYS_EAGER = CELERY_TASK_ALWAYS_EAGER = True   # run celery tasks as functions

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
