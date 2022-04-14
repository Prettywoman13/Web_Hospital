from datetime import datetime
from datetime import timedelta
from datetime import date


def get_schedule_list(time_list, start_time, end_time, lunch_start, lunch_end, delim):

    if start_time >= end_time:
        return time_list
    if not(lunch_start <= start_time <= lunch_end) and not (lunch_start <= (datetime.combine(date.today(), start_time) + timedelta(minutes=delim)).time() <= lunch_end):

        time_list.append(start_time.strftime("%H:%M"))
    start_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=delim)).time()
    return get_schedule_list(time_list, start_time, end_time, lunch_start, lunch_end, delim)



