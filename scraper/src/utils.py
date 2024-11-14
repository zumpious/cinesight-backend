def convert_to_minutes(duration):
    hours = int(duration[2:duration.index('H')])

    minutes = int(duration[duration.index('H') + 1:duration.index('M')]) if 'M' in duration else 0

    total_minutes = hours * 60 + minutes

    return total_minutes
