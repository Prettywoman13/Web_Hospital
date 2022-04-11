def minute_to_hours(mixed_time):
    hours = mixed_time // 60
    minute = mixed_time % 60
    if minute == 0:
        minute = '00'
    return f'{hours}:{minute}'


def hours_to_min(mixed_time):
    mixed_time_list = list(map(int, mixed_time.split(':')))
    return mixed_time_list[0] * 60 + mixed_time_list[1]


def get_schedule_list(timelist, start_time, end_time, delim):
    if hours_to_min(start_time) >= hours_to_min(end_time):
        return timelist
    else:
        new_start_time = minute_to_hours(hours_to_min(start_time) + delim)
        timelist.append(new_start_time)
        get_schedule_list(timelist, start_time=new_start_time,
                          end_time=end_time, delim=delim)


def calc_time_list(start_time, end_time, lunch_start, lunch_end, delim):
    lunch_start = minute_to_hours(hours_to_min(lunch_start) - 1)
    time_list = []
    lunch_time_list = []
    get_schedule_list(time_list, start_time, end_time, delim)
    get_schedule_list(lunch_time_list, lunch_start, lunch_end, 1)
    for i in lunch_time_list:
        if i in time_list:
            time_list.remove(i)
    return time_list


calc_time_list(start_time='8:00', end_time='15:00', lunch_start='12:00', lunch_end='13:00', delim=10)
