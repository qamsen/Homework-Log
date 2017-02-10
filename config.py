import os.path
import os
import csv
import configparser

# Reads the config file
parser = configparser.ConfigParser()
parser.read('homework.ini')

# String of the semester in the config file
current_semester = parser['Semester Info']['semester']
# A list contains a string for each class in the config file
current_courses = parser['Semester Info']['courses'].split(',')

# Creates the directory for the homework log
log_path = 'data/{}'.format(current_semester)
if not os.path.exists(log_path):
    os.makedirs(log_path)

log_file = '{}/log.csv'.format(log_path)

def create_new_file():

    with open(log_file, 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer  = csv.writer(csv_file)
        # Format of csv file: first row=dates, other rows=courses
        writer.writerow(['Date'] + current_courses)

def update_file():

    temp_csv = 'temp'

    # ahh
    with open(
            log_file,
            'r',
            newline='',
            encoding='utf-8-sig'
            ) as readfile, open(
            temp_csv,
            'w',
            newline='',
            encoding='utf-8-sig'
            ) as writefile:

        r = csv.reader(readfile)
        w = csv.writer(writefile)

        # Skip the header
        next(r, None)
        # Write new header
        w.writerow(['Date'] + current_courses)

        # Copy the rest
        for row in r:
            w.writerow(row)

    os.remove(log_file)
    os.rename(temp_csv, log_file)

# Creates the homework log file
if not os.path.isfile(log_file):
    create_new_file()
else:
    update_file()
