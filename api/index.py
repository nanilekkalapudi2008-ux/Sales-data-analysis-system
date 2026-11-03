import sys
import os

# Add parent directory to sys.path so app and modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathFix:
    """
    WSGI Middleware to fix Vercel internal rewrites.
    Restores original requested path (e.g. /, /login, /dashboard, /static/...)
    instead of the internal destination path /api/index.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        original = (
            environ.get('HTTP_X_FORWARDED_URI') 
            or environ.get('HTTP_X_MATCHED_PATH')
        )
        if original and not original.startswith('/api'):
            environ['PATH_INFO'] = original.split('?')[0]
        else:
            p = environ.get('PATH_INFO', '')
            if p.startswith('/api/index'):
                new_p = p[len('/api/index'):]
                environ['PATH_INFO'] = new_p if (new_p and new_p.startswith('/')) else '/'
            elif p.startswith('/api'):
                new_p = p[len('/api'):]
                environ['PATH_INFO'] = new_p if (new_p and new_p.startswith('/')) else '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)

# Vercel entrypoint
app = app
