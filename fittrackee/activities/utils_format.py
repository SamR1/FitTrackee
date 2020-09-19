from datetime import timedelta


def convert_in_duration(value):
    hours = int(value.split(':')[0])
    minutes = int(value.split(':')[1])
    return timedelta(seconds=(hours * 3600 + minutes * 60))


def convert_timedelta_to_integer(value):
    hours, minutes, seconds = str(value).split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def convert_value_to_integer(record_type, val):
    if val is None:
        return None

    if record_type == 'LD':
        return convert_timedelta_to_integer(val)
    elif record_type in ['AS', 'MS']:
        return int(val * 100)
    else:  # 'FD'
        return int(val * 1000)
