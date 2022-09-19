import logging

import click

from fittrackee.cli.app import app

from .clean import clean_tokens

handler = logging.StreamHandler()
logger = logging.getLogger('fittrackee_clean_oauth2_tokens')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@click.group(name='oauth2')
def oauth2_cli() -> None:
    """Manage OAuth2 tokens."""
    pass


@oauth2_cli.command('clean')
@click.option('--days', type=int, required=True, help='Number of days.')
def clean(
    days: int,
) -> None:
    """Clean tokens expired for more than provided number of days"""
    with app.app_context():
        deleted_rows = clean_tokens(days)
        logger.info(f'Expired deleted tokens: {deleted_rows}.')
