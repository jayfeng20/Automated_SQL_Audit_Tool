import random
from datetime import datetime, timedelta


def get_datetime():
    # Generate a random datetime between two specific dates
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)

    # Calculate the time difference between start and end dates
    time_difference = end_date - start_date

    # Generate a random number of seconds within the time difference
    random_seconds = random.randint(0, int(time_difference.total_seconds()))

    # Add the random number of seconds to the start date
    random_datetime = start_date + timedelta(seconds=random_seconds)

    # Format the random datetime as a string in SQL DATETIME format
    sql_datetime = random_datetime.strftime("%Y-%m-%d %H:%M:%S")
    print(sql_datetime)
    return sql_datetime


get_datetime()
