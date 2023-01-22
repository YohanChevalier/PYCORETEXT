from datetime import datetime as dt
from datetime import date as d
from datetime import timedelta as td
from time import strftime

# TODAY
today = d.today() 
print(today)

# YESTERDAY
diff1 = td(days=1)

yesterday = today - diff1
print(yesterday)
str_yesterday = str(yesterday)
print('en strings', str_yesterday)

# WEEK BEFORE
diff2 = td(days=7)
week_before = today - diff2
print(week_before)

# 1er jour du mois en cours
first_day_month = today.replace(day=1)
print(first_day_month)

# mois
print(dt.now().month)

# previous month
last_day_of_prev_month = today.replace(day=1) - td(days=1)

start_day_of_prev_month = today.replace(day=1) - td(days=last_day_of_prev_month.day)

# For printing results
print("First day of prev month:", start_day_of_prev_month)
print("Last day of prev month:", last_day_of_prev_month)