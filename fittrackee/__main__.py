# source for StandaloneApplication class:
# http://docs.gunicorn.org/en/stable/custom.html
import os
import shutil
from typing import Dict, Optional

import gunicorn.app.base
from flask import Flask
from flask_dramatiq import worker
from flask_migrate import upgrade

from fittrackee import create_app, db

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', '5000')
WORKERS = os.getenv('APP_WORKERS', 1)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = create_app()
dramatiq_worker = worker


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(
        self, current_app: Flask, options: Optional[Dict] = None
    ) -> None:
        self.options = options or {}
        self.application = current_app
        super().__init__()

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Flask:
        return self.application


def upgrade_db() -> None:
    with app.app_context():
        upgrade(directory=BASEDIR + '/migrations')


@app.cli.command('drop-db')
def drop_db() -> None:
    """Empty database and delete uploaded files for dev environments."""
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
    db.drop_all()
    db.session.commit()
    print('Database dropped.')
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    print('Uploaded files deleted.')


def main() -> None:
    options = {'bind': f'{HOST}:{PORT}', 'workers': WORKERS}
    StandaloneApplication(app, options).run()


if __name__ == '__main__':
    app.run()
