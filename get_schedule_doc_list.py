time_list = []


def minute_to_hours(mixed_time):
    hours = mixed_time // 60
    minute = mixed_time % 60
    if minute == 0:
        minute = '00'
    return f'{hours}:{minute}'


def hours_to_min(mixed_time):
    mixed_time_list = list(map(int, mixed_time.split(':')))
    return mixed_time_list[0] * 60 + mixed_time_list[1]


def get_schedule_list(start_time, end_time, lunch_start, lunch_lend, delim):
    if hours_to_min(start_time) == hours_to_min(end_time):
        return time_list
    else:
        new_start_time = minute_to_hours(hours_to_min(start_time) + delim)
        print(new_start_time)
        get_schedule_list(start_time=new_start_time,
                          end_time=end_time,
                          lunch_start=lunch_start,
                          lunch_lend=lunch_lend, delim=delim)


get_schedule_list('6:40', '18:40', '12:00', '13:00', 10)
