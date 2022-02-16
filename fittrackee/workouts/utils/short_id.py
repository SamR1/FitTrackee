from uuid import UUID

import shortuuid


def encode_uuid(uuid_value: UUID) -> str:
    """
    Return short id string from a UUID
    """
    return shortuuid.encode(uuid_value)


def decode_short_id(short_id: str) -> UUID:
    """
    Return UUID from a short id string
    """
    return shortuuid.decode(short_id)
