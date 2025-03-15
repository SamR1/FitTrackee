# source for StandaloneApplication class:
# http://docs.gunicorn.org/en/stable/custom.html
import os
from typing import TYPE_CHECKING, Dict, Optional

import gunicorn.app.base

from fittrackee import create_app, db

if TYPE_CHECKING:
    from flask import Flask
    from gunicorn.arbiter import Arbiter
    from gunicorn.workers.base import Worker

HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "5000")
WORKERS = os.getenv("APP_WORKERS", 1)
TIMEOUT = os.getenv("APP_TIMEOUT", 30)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = create_app()


def pre_fork(server: "Arbiter", worker: "Worker") -> None:
    """
    To use connection pools with a forked process (the new process will start
    with new connections).
    see: https://docs.sqlalchemy.org/en/20/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    """
    with app.app_context():
        db.engine.dispose()


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(
        self, current_app: "Flask", options: Optional[Dict] = None
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

    def load(self) -> "Flask":
        return self.application


def main() -> None:
    options = {
        "bind": f"{HOST}:{PORT}",
        "workers": WORKERS,
        "pre_fork": pre_fork,
        "timeout": TIMEOUT,
    }
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    app.run()
