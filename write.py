import csv
import config
from datetime import datetime

# Retrieves the header from the csv file
with open(config.log_file, newline='', encoding='utf-8-sig') as csv_reader:
    reader = csv.reader(csv_reader)
    header = next(reader)

def to_csv(course_name, hours_studied, date=datetime.today()):
    """Writes a log entry for study hours.

    Keyword arguments:
    course_name   -- name of course
    hours_studied -- total hours logged
    date          -- the date for log entry (default today)
    """
    log_dict = log_dictionary(date)
    log_dict[course_name] = hours_studied

    # Writes the dictionary to the csv file
    with open(config.log_file,
            'a',
            newline='',
            encoding='utf-8-sig'
            ) as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writerow(log_dict)

def given_dates(course_name, start_time, end_time):
    """Writes a log entry for the difference between two dates.

    Keyword arguments:
    course_name -- name of course
    start_time  -- datetime at the start of study
    end_time    -- datetime at the end of study
    """
    delta_time = end_time - start_time
    hours_studied = delta_time.seconds / 3600 \
                    + delta_time.microseconds / 3600000000 \
                    + delta_time.days * 24
    date = start_time.date()
    to_csv(course_name, hours_studied, date)

def log_dictionary(date):
    """Creates a dictionary for logging study hours.

    Keywords:
    date -- the date for log entry
    """
    log_dict = {'Date' : date.strftime('%Y/%m/%d')}
    for course in header[1:]:
        log_dict[course] = ''

    return log_dict
