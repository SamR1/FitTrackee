from datetime import timedelta


def remove_microseconds(delta: "timedelta") -> "timedelta":
    return delta - timedelta(microseconds=delta.microseconds)
