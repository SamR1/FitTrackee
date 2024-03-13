import os
import shutil

import click
from flask_migrate import upgrade

from fittrackee import db
from fittrackee.cli.app import app

BASEDIR = os.path.abspath(os.path.dirname(__file__))
app_settings = os.getenv('APP_SETTINGS', 'fittrackee.config.ProductionConfig')


@click.group(name='db')
def db_cli() -> None:
    """Manage database."""
    pass


@db_cli.command('upgrade')
def upgrade_db() -> None:
    """Apply migrations."""
    with app.app_context():
        upgrade(directory=BASEDIR)


@db_cli.command('drop')
def drop_db() -> None:
    """Empty database and delete uploaded files for dev environments."""
    with app.app_context():
        if app_settings == 'fittrackee.config.ProductionConfig':
            click.echo(
                click.style(
                    'This is a production server, aborting!', bold=True
                ),
                err=True,
            )
            return
        db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
        db.drop_all()
        db.session.commit()
        click.echo('Database dropped.')
        shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
        click.echo('Uploaded files deleted.')
