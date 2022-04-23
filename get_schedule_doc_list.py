from datetime import datetime
from datetime import timedelta
from datetime import date


def get_schedule_list(time_list: list, start_time: object, end_time: object, lunch_start: object, lunch_end: object, delim: object) -> object:
    ''' Фунция для получения талонов, на вход принимает list куда сохранять талоны,
    начальное время(формат времени библы datetime(далее он используется везде)),
     конечное время приема, время начало обеда, время окончания обеда, время на один прием  '''
    if start_time >= end_time:
        return time_list
    if not(lunch_start <= start_time <= lunch_end) and not (lunch_start <= (datetime.combine(date.today(), start_time) + timedelta(minutes=delim)).time() <= lunch_end):

        time_list.append(start_time.strftime("%H:%M"))
    start_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=delim)).time()
    return get_schedule_list(time_list, start_time, end_time, lunch_start, lunch_end, delim)



