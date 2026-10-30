import sys
import os
from dotenv import load_dotenv

# Path to your Django project (where manage.py lives)
path = '/home/Midex1/eventhub-django/event_management'
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables from your .env file
load_dotenv(os.path.join(path, '.env'))

# Tell Django which settings module to use
os.environ['DJANGO_SETTINGS_MODULE'] = 'event_management.settings'

# Get the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
