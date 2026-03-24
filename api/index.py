import os
import sys

# Add the backend directory to python path for Vercel
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application

# Vercel needs the 'app' or 'application' variable exposed
application = get_wsgi_application()
app = application
