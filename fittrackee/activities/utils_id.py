import shortuuid


def encode_uuid(uuid_value):
    return shortuuid.encode(uuid_value)


def decode_short_id(short_id):
    return shortuuid.decode(short_id)
