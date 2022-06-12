import time

from fittrackee import db


def clean_tokens(days: int) -> int:
    limit = int(time.time()) - (days * 86400)
    sql = """
        DELETE FROM oauth2_token
        WHERE oauth2_token.issued_at + oauth2_token.expires_in < %(limit)s;
    """
    result = db.engine.execute(sql, {'limit': limit})
    return result.rowcount
