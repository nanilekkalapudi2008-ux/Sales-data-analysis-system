import sys
import os
import urllib.parse

# Add parent directory to sys.path so app and modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathFix:
    """
    WSGI Middleware to fix Vercel internal rewrites.
    Restores the exact client requested path from ?path=/$1
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query = environ.get('QUERY_STRING', '')
        if 'path=' in query:
            params = urllib.parse.parse_qs(query)
            if 'path' in params and params['path']:
                target_path = params['path'][0]
                if not target_path.startswith('/'):
                    target_path = '/' + target_path
                while target_path.startswith('//'):
                    target_path = target_path[1:]
                environ['PATH_INFO'] = target_path
                clean_query = '&'.join(
                    f"{k}={v[0]}" for k, v in params.items() if k != 'path'
                )
                environ['QUERY_STRING'] = clean_query
        else:
            p = environ.get('PATH_INFO', '')
            if p in ('/api/index', '/api/index.py', '/api'):
                environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)

# Vercel entrypoint
app = app
