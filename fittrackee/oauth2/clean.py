from fittrackee.utils import clean


def clean_tokens(days: int) -> int:
    sql = """
        DELETE FROM oauth2_token
        WHERE oauth2_token.issued_at + oauth2_token.expires_in < %(limit)s;
    """
    return clean(sql, days)
