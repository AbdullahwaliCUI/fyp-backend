import os
import sys

# Add your project directory to the sys.path
# This is crucial for Hostinger to find your modules
sys.path.append(os.getcwd())

# Set the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# Import the standard WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
