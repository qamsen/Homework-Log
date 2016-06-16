import cmd, time, csv, configparser, os.path, calendar
from datetime import datetime, timedelta

class ReadWrite():

    def __init__(self, csvfile, header=False):

        # The file being changed
        self.csvfile = csvfile

        # Field names of the csv file
        if header:
            with open(csvfile) as csvreader:
                self.fieldnames = next(csv.reader(csvreader))

    def log_hours(self, coursename, hourslogged):

        # Add the hours studied to the specified course
        dict = self.date_dictionary(self.fieldnames)
        dict[coursename] = hourslogged

        # Open the csv file 
        with open(self.csvfile, 'a', newline='') as csvfile:

            # Writer for the csv file
            writer = csv.DictWriter(csvfile, self.fieldnames)

            # Write a row with the information in the dictionary
            writer.writerow(dict)

    def date_dictionary(self, date_fieldnames):

        # Creates the dictionary with today's date
        date_dict = {'Date' : time.strftime('%m/%d/%Y')}

        # Adds a dictionary entry for each course
        for course in self.fieldnames[1:]:
            date_dict[course] = ''

        return date_dict

    def remove_rows(self, n_of_rows):

        # Stores every line currently in the file
        with open(self.csvfile) as readfile:
            lines = readfile.readlines()

        with open(self.csvfile, 'w', newline='') as writefile:

            # Overwrites the file, prints all but the last n rows
            writefile.writelines(lines[:-1 * n_of_rows])

    def read_csv(self):
        """
        Reads the CSV file, returns the headers and data rows separately
        """
        with open(self.csvfile) as csvreader:
            reader = csv.reader(csvreader)

            headers = next(reader)
            data_rows = []

            for row in reader:
                data_rows.append(row)

            return (headers, data_rows)
    
    def write_csv(self, list_of_lists):
        """
        Writes an CSV file, with a row for each list in the parameter
        """
        with open(self.csvfile, 'w', newline='') as csvwriter:
            writer = csv.writer(csvwriter)

            for row in list_of_lists:
                writer.writerow(row)

def to_float(value):
    """
    Either converts a String to a float or returns 0
    """
    try:
        return float(value)
    except ValueError:
        return 0

def sum_row(sum_row, summed_row):
    """
    Adds the second row to the first row, ignores row indicators
    """
    index = 1

    for entry in summed_row[1:]:
        sum_row[index] += to_float(entry)
        index += 1

def sumweekdays(readfile, writefile):
    """
    Sums the total study hours during each weekday and stores the
    result in an CSV file
    """

    # Stores the header and the data from the CSV file
    header, data_rows = ReadWrite(readfile, True).read_csv()

    # A list for each weekday, with an entry for each course
    weekdays = []
    for day in calendar.Calendar().iterweekdays():
        weekdays.append([calendar.day_name[day]] + [0] * len(header[1:]))

    for row in data_rows:

        # Stores an int representing the day of the week in the first column
        date = datetime.strptime(row[0], '%m/%d/%Y')
        day_of_week = date.weekday()

        sum_row(weekdays[day_of_week], row)

    ReadWrite(writefile).write_csv(weekdays)

def sum_months(readfile, writefile):
    """
    Sums the total study hours during each month.
    """

    # Stores the header and the data fom the CSV file
    header, data_rows = ReadWrite(readfile, True).read_csv()

    # The number of courses
    n_of_courses = len(header[1:])

    # A list of months
    months = []

    # no previous row month to start
    previous_row_month = -1

    for row in data_rows:

        # Store the month of the date
        date = datetime.strptime(row[0], '%m/%d/%Y')
        row_month = date.month

        # Create a new list for a new month
        if row_month != previous_row_month:
            months.append([date.strftime('%B')] + [0] * n_of_courses)
            previous_row_month = row_month

        sum_row(months[-1], row)

    ReadWrite(writefile).write_csv(months)

def sum_days(readfile, writefile):
    """
    Sums the total study hours for each day
    """

    # Stores the header and the data from the CSV file
    header,data_rows = ReadWrite(readfile, True).read_csv()

    # Number of courses
    n_of_courses = len(header[1:])

    # Date of first and last entries, and the difference between them
    start_date = datetime.strptime(data_rows[0][0], '%m/%d/%Y')
    end_date = datetime.strptime(data_rows[-1][0], '%m/%d/%Y')
    delta = end_date - start_date

    each_day = []

    for i in range(delta.days + 1):
        date = datetime.strftime(start_date + timedelta(days=i), '%m/%d/%Y')
        each_day.append([date] + [0] * n_of_courses)

    index = 0

    for day in each_day:

        date1 = datetime.strptime(day[0], '%m/%d/%Y')
        date2 = datetime.strptime(data_rows[index][0], '%m/%d/%Y')

        while date1 == date2 and index + 1 < len(data_rows):
            try:
                sum_row(day, data_rows[index])
                index += 1
                date2 = datetime.strptime(data_rows[index][0], '%m/%d/%Y')
            except IndexError:
                date2 = None

    ReadWrite(writefile).write_csv(each_day)

class Homework(cmd.Cmd):
    
    # ----- Variables from config file -----

    # Parses the config file
    config = configparser.ConfigParser()
    config.read('Homework Log.ini')

    # The current semester
    semester = config['Semester Info']['semester']

    # Current course schedule
    courses = config['Semester Info']['courses'].split(', ')

    # Path to school folder
    school_dir_path = config['Filepath']['filepath']

    # ----- Homework Log CSV file -----

    logpath = '{}/{}'.format(school_dir_path, semester)

    # Creates semester directory if it doesn't exist already
    if not os.path.exists(logpath):
        os.makedirs(logpath)

    logfile = '{}/{} Homework Log.csv'.format(logpath, semester)

    # Creates the file with a column for the date and each course
    if not os.path.isfile(logfile):
        with open(logfile,'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date'] + courses)

    # ----- CMD intro and prompt -----

    intro = """
        Homework log. Type help or ? to list commands.

        Semester: {}
        Classes: {}
        """.format(semester, ', '.join(courses))

    prompt = '(Homework Log)' 

    # ----- Misc. Class Variables -----

    # Lines of data added during the duration of the program
    linesofdata = 0

    writer =ReadWrite(logfile,True)
    
    # ----- Commands -----

    def do_start(self, coursename):
        """
        Records study time for a course.
        Ex. 'start MATH 305', 'start math 305', 'start math305'
        """
        coursename = self.correctformat(coursename)

        if coursename in self.courses:
            self.record(coursename, self.timer())
        else:
            print('Invalid course name.')

    def do_record(self, coursename):
        """
        Manually log study hours.
        Ex. 'record MATH 305', 'record math 305', 'record math305'
        """
        coursename = self.correctformat(coursename)
        
        if coursename in self.courses:
            self.record(coursename, self.checkvalue('', float))
        else:
            print('Invalid course name.')

    def do_undo(self, args):
        """
        Undos specified number of lines. Only data added during the duration 
        of the program can be undone. 
        Ex. undo
        """

        # Prints the amount of lines that can be undone
        print('{0} lines of data logged'.format(self.linesofdata))
        
        # The number of lines to undo
        linesundone = self.checkvalue('', int)
        
        # Must be non-negative and less than or equal to lines added
        if linesundone in range(0, self.linesofdata+1):
            # Removes rows and adjusts the lines added to reflec the change
            self.writer.remove_rows(linesundone)
            self.linesofdata -= linesundone
            print('{} lines removed.'.format(linesundone))

        # Ignore escape command
        elif linesundone != 'exit':
            print('Invalid value.')

    def do_quit(self, args):
        """
        Exits the program.
        Ex. quit
        """

        sum_days(self.logfile, '{}/{} Sum Days.csv'.format(self.logpath, self.semester))
        sum_months(self.logfile, '{}/{} Sum Months.csv'.format(self.logpath, self.semester))
        sumweekdays(self.logfile, '{}/{} Sum Weekdays.csv'.format(self.logpath, self.semester))
        print('Goodbye.')
        return True

    # ----- Helper Methods -----

    def record(self, coursename, hourslogged):
        """
        Writes to the csv file and informs user of hours logged
        """

        if hourslogged != 'exit':
            self.writer.log_hours(coursename, hourslogged)
            print('{} hours logged in {}.'.format(hourslogged, coursename))

            # Number of lines recorded increases by 1
            self.linesofdata += 1


    def timer(self):
        """
        Return the eclipsed time from the start of the timer to the end.
        """

        # Start time of the timer
        starttime = time.clock()
        
        # Any command will stop the timer
        command = input("Press any button to finish (or 'exit' to cancel)>>>")
        
        if command == 'exit':
            return command

        # Eclipsed time
        return (time.clock() - starttime) / 3600
    
    def correctformat(self, coursename):
        """
        Return the course name correctly formatted.
        Ex. 'math305' --> 'MATH 305', 'math 305' --> 'MATH 305'
        """

        # When there is no space between department and number
        try:
            if coursename[4] != ' ':
                coursename = coursename[:4] + ' ' + coursename[4:]
        except IndexError:
            pass

        return coursename.upper()

    def checkvalue(self, value, valuetype):
        """
        Return either a value of a specified type of 'exit'
        """

        # Prompts user for a value of valuetype or the escape command
        while not isinstance(value, valuetype) and value != 'exit':

            # A String representing an input
            value = input("Enter value (or 'exit')>>>")

            try:
                value = valuetype(value)
            except ValueError:
                pass

        return value

Homework().cmdloop()
