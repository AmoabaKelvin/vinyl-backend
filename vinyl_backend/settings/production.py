import dj_database_url

from .base import *

DEBUG = os.environ['DEBUG'] == 'True'

ALLOWED_HOSTS = ['project-vinyl-backend.herokuapp.com']


DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
STATIC_ROOT = 'static'

CLOUDINARY_URL = os.environ['CLOUDINARY_URL']

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'
