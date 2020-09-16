# source: http://docs.gunicorn.org/en/stable/custom.html
import os

import gunicorn.app.base
from fittrackee import create_app
from fittrackee.database_utils import init_database
from flask_dramatiq import worker
from flask_migrate import upgrade

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('API_PORT', '5000')
WORKERS = os.getenv('APP_WORKERS', 1)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = create_app()
dramatiq_worker = worker


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, current_app, options=None):
        self.options = options or {}
        self.application = current_app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def upgrade_db():
    with app.app_context():
        upgrade(directory=BASEDIR + '/migrations')


def init_data():
    with app.app_context():
        init_database(app)


def main():
    options = {'bind': f'{HOST}:{PORT}', 'workers': WORKERS}
    StandaloneApplication(app, options).run()


if __name__ == '__main__':
    main()
