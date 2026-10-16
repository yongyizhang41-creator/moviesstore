import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = [
    'ustinian.pythonanywhere.com', 
]

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True