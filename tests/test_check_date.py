import datetime


def date_checker(date: str):
    check_state = False
    # par format
    for format in ['%Y-%m-%d', '%Y-%m', '%Y']:
        try:
            datetime.datetime.strptime(date, format)
        except ValueError:
            pass
        else:
            check_state = True
    # au minimum deux chiffres par segment
    date_list = date.split("-")
    for date in date_list:
        if len(date) < 2:
            check_state = False
    return check_state


def date_checker2(date: str):
    check_state = False
    for format in ['%Y-%m-%d', '%Y-%m', '%Y']:
        try:
            datetime.datetime.strptime(date, format)
        except ValueError:
            pass
        else:
            check_state = True
    # au minimum deux chiffres par segment
    date_list = date.split("-")
    for i, date in enumerate(date_list):
        if i == 0:
            if len(date) < 4:
                check_state = False
        elif len(date) < 2:
            check_state = False
    return check_state


date = '2022-01-02'
print(date_checker2(date))
