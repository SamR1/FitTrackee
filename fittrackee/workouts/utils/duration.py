from datetime import timedelta


def _remove_microseconds(delta: "timedelta") -> "timedelta":
    return delta - timedelta(microseconds=delta.microseconds)
