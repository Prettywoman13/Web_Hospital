from datetime import datetime
from datetime import timedelta
from datetime import date


def get_schedule_list(time_list, start_time, end_time, delim):

    if start_time >= end_time:
        return time_list
    start_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=delim)).time()
    time_list.append(start_time.strftime("%H:%M"))
    return get_schedule_list(time_list, start_time, end_time, delim)



