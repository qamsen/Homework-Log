import cmd, time, csv, configparser, os.path, calendar
from datetime import datetime, timedelta

class ReadWrite():

    def __init__(self, csvfile, has_header=False):
        """
        Assign values to csvfile, fieldnames, and has_header

        Parameters
        ----------
        csvfile : The file being read and written to.
        has_header : Whether the given CSV file has a header row.

        """

        # The file being changed
        self.csvfile = csvfile

        # Field names of the csv file
        if has_header:
            with open(csvfile) as csvreader:
                self.fieldnames = next(csv.reader(csvreader))

        self.has_header = has_header

    def log_hours(self, coursename, hourslogged):
        """
        Store hourslogged in the coursename key of a dict.

        Parameters
        ----------
        coursename : The course the hours are being logged for
        hourslogged : The hours studied for a given course

        Also See
        --------
        date_dictionary

        """

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
        """
        Return a dict with a key for the date and each cource.

        Parameters
        ----------
        date_fieldnames : The non-date field names.

        Returns
        -------
        date_dict : A dictionary with the date and each course

        """

        # Today's date in MM/DD/YYYY
        date_dict = {'Date' : time.strftime('%m/%d/%Y')}

        # First entry is 'Date', so ignore
        for course in self.fieldnames[1:]:

            # Initialize an empty value for the course
            date_dict[course] = ''

        return date_dict

    def remove_rows(self, n_of_rows):
        """
        Remove the last n lines from the CSV file.

        Parameters
        ----------
        n_of_rows : The number of rows removed from the CSV file.

        """

        # Stores every line currently in the file
        with open(self.csvfile) as readfile:
            lines = readfile.readlines()

        with open(self.csvfile, 'w', newline='') as writefile:

            # Overwrites the file, prints all but the last n rows
            writefile.writelines(lines[:-1 * n_of_rows])

    def read_csv(self):
        """
        Return the headers and data from an CSV file.

        Return
        ------
        headers : The header row of the CSV file.
        data_rows : The rows that stored data in the CSV file.

        """

        with open(self.csvfile) as csvreader:
            reader = csv.reader(csvreader)

            # Store the headers
            if self.has_header:
                headers = next(reader)

            data_rows = []

            # Store each row in file to data_row
            for row in reader:
                data_rows.append(row)

            # Return the data, and---if indicated---the headers.
            if self.has_header:
                return (headers, data_rows)
            else:
                return data_rows

    def write_csv(self, list_of_lists):
        """
        Write each entry in a list to an CSV file.

        Parameters
        ----------
        list_of_lists : A list that contains each list that will be
            written to the CSV file.

        """

        with open(self.csvfile, 'w', newline='') as csvwriter:
            writer = csv.writer(csvwriter)

            for row in list_of_lists:
                writer.writerow(row)

class AnalyzeData():

    def __init__(self, file, path, prefix):
        """
        Assign values to headers, data_rows, n_of_courses, path, and
        prefix.

        Parameters
        ----------
        file : The data that will be analyzed
        path : The path to which new files are written.
        prefix : An indicator for the name of new files.

        Instance Variables
        ------------------
        headers : The header row of the CSV file.
        data_rows : Other rows that hold numerical data.
        n_of_courses : The number of courses, denoted by non-Date
            columns in headers.
        path : The file path where new files will be saved.
        prefix : The prefix to every filename written
            E.g. 'Fall 2016'

        """

        reader = ReadWrite(file, has_header=True)
        self.headers, self.data_rows = reader.read_csv()
        self.n_of_courses = len(self.headers[1:])
        self.path = path
        self.prefix = prefix

    def sum_months(self):
        """
        Sum the total hours studied in each month.
        """

        months = []

        # The row of the previous month as an int
        previous_row_month = -1

        for row in self.data_rows:

            # Store date string 'MM/DD/YYYY' as a date object
            date = datetime.strptime(row[0], '%m/%d/%Y')
            row_month = date.month

            # Create a new list when a new month
            if row_month != previous_row_month:

                # The month as a string (e.g. 'January')
                month_str = date.strftime('%B')

                # A list with the month and columns for each course
                months.append([month_str] + [0] * self.n_of_courses)
                previous_row_month = row_month

            self.sum_row(months[-1], row)

        self.write_to_filename('Sum Months', self.total(months))

    def sum_weekdays(self):
        """
        Sum the total hours studied in each weekday.
        """

        weekdays = []

        # A list for each weekday, with a column for each course
        for day in calendar.Calendar().iterweekdays():

            # The name of the day
            day_name = calendar.day_name[day]
            weekdays.append([day_name] + [0] * self.n_of_courses)

        # Checks each entry
        for row in self.data_rows:

            # An int representing a weekday
            date = datetime.strptime(row[0], '%m/%d/%Y')
            day_of_week = date.weekday()

            self.sum_row(weekdays[day_of_week], row)

        self.write_to_filename('Sum Weekdays', self.total(weekdays))

    def sum_days(self):
        """
        Sum the total hours studied in each day.
        """

        # First and last date entries
        firstrow, lastrow = self.data_rows[0][0], self.data_rows[-1][0]

        # Store as datetime objects
        start_date = datetime.strptime(firstrow, '%m/%d/%Y')
        end_date = datetime.strptime(lastrow, '%m/%d/%Y')

        # Difference between start and finsih
        delta = end_date - start_date

        each_day = []

        # For each date between the start and finish
        for i in range(delta.days + 1):

            # Increment date and store as 'MM/DD/YYYY'
            date = start_date + timedelta(days=i)
            date_str = datetime.strftime(date, '%m/%d/%Y')

            # Append a row with the date and a column for each course
            each_day.append([date_str] + [0] * self.n_of_courses)

        each_day_iter = iter(each_day)
        each_day_date = None

        for row in self.data_rows:

            # Store date string 'MM/DD/YYYY' as date object
            data_row_date = datetime.strptime(row[0], '%m/%d/%Y')

            while each_day_date != data_row_date:

                # Move to the next day in the list
                each_day_row = next(each_day_iter)

                # Store the date string 'MM/DD/YYYY' as date object
                each_day_date = datetime.strptime(each_day_row[0], '%m/%d/%Y')

            self.sum_row(each_day_row, row)

        # Adds the sum for each row and seven day sum and averages
        each_day = self.total(each_day)
        self.write_to_filename('Sum Days', self.sum_totals(each_day))

    def total(self, rows, start_on_column=1):
        """
        Sum the values and append the result to each row.

        Parameters
        ----------
        rows : Rows the summation is performed on.
        start_on_column : Column the summation begins on.

        Return
        ------
        rows : The rows with the total appended to each row

        Example
        -------
        >>> a = [
                [1,2,3,4],
                [2,3,4,5]
                ]
        >>> total(a)
        >>> a
        [[1,2,3,4,10],[2,3,4,5,14]]

        """

        for i, row in enumerate(rows):

            # Add every value in the list with given start point
            total = sum(self.to_float(x) for x in row[start_on_column:])
            rows[i].append(total)

        return rows

    def sum_totals(self, rows, totals=7):
        """
        Calculate the sum and average of totals for a given value.

        Parameters
        ----------
        rows   : A collection of rows for which the averages are found.
        totals : The number of totals summed, default is 7 for total days
            in a week.

        Return
        ------
        rows : The rows updated to include the sum of totals and averages

        """

        sum_total = 0

        for i, row in enumerate(rows):

            # The total for a list is stored in it's last entry
            sum_total += self.to_float(row[-1])

            # When the row number exceeds the totals to be summed
            if i >= totals:

                # Total is third to last entry when accessing previous lists
                # Remove value outside the sum range.
                sum_total -= self.to_float(rows[i - totals][-3])

            # Append the current sum and average value
            rows[i] += [sum_total, sum_total / totals]

        return rows
        """
        Perform all methods for analyzing data.
        """

        self.sum_months()
        self.sum_days()
        self.sum_weekdays()

    def write_to_filename(self, suffix, rows):
        """
        Write a series of rows to an CSV file.

        Parameters
        ----------
        suffix : The second part of the filename.
        rows   : The rows written to the file.

        """

        filename = '{}/{} {}.csv'.format(self.path, self.prefix, suffix)
        ReadWrite(filename).write_csv(rows)

    def sum_row(self, sum_row, summed_row, start_on_column=1):
        """
        Sum each entry in the rows and store the result.

        Parameters
        ----------
        sum_row         : A row whose entries are summed with summed_row and
                          stored in this row.
        summed_row      : A row whose entries are summed with sum_row.
        start_on_column : The column summation begins on.

        Example
        -------
        >>> a = ['Filler', 1, 2, 3]
        >>> b = ['Filler', 1, 2, 3]
        >>> sum_row(a, b)
        >>> a
        ['Filler', 2, 4, 6]

        """

        for i, (entry1, entry2) in enumerate(zip(sum_row, summed_row)):
            if i >= start_on_column:
                sum_row[i] = self.to_float(entry1) + self.to_float(entry2)

    def to_float(self, value):
        """
        Return a float representation of the parameter.

        If the parameter is a string that can be converted to a float,
        said float value will be returned. Otherwise, the return value
        is 0.

        Parameters
        ----------
        value : A string that represents a value.

        Return
        ------
        A float representation of a string (0 for non-float values).

        """

        try:
            return float(value)
        except ValueError:
            return 0

class Homework(cmd.Cmd):
    """
    A command line interface for logging stuydy hours.

    Class Variables
    ---------------
    config          : A parser for the config file.
    semester        : The current semester.
    courses         : The current course schedule.
    school_dir_path : Path to the 'CWRU' folder.
    logpath         : Path to the current semester folder.
    logfile         : The file study hours are logged in.
    linesofdata     : The total lines of data added during the program.
    intro           : The opening dialogue when the program is started.
    prompt          : The prompt issued to solicit input.
    writer          : Writes data to the CSV file.

    """

    config = configparser.ConfigParser()
    config.read('Homework Log.ini')

    semester = config['Semester Info']['semester']
    courses = config['Semester Info']['courses'].split(', ')
    school_dir_path = config['Filepath']['filepath']
    logpath = '{}/{}'.format(school_dir_path, semester)
    logfile = '{}/{} Homework Log.csv'.format(logpath, semester)
    linesofdata = 0

    # Create the path
    if not os.path.exists(logpath):
        os.makedirs(logpath)

    # Create the file
    if not os.path.isfile(logfile):
        with open(logfile,'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date'] + courses)

    writer = ReadWrite(logfile,True)

    intro = """
        Homework log. Type help or ? to list commands.

        Semester : {}
        Classes  : {}
        """.format(semester, ', '.join(courses))
    prompt = '(Homework Log)'


    def do_start(self, coursename):
        """
        Prompt user to start a timer for logging time.

        Parameter
        ---------
        The name of the course.

        Example
        -------
        (Homework Log) start math305
        (Homework Log) start Math 305
        (Homework Log) start MATH 305

        """

        # Example format: 'math305' --> 'MATH 305'
        coursename = self.correctformat(coursename)

        if coursename in self.courses:
            self.record(coursename, self.timer())
        else:
            print('Invalid course name.')

    def do_record(self, coursename):
        """
        Prompt user to manually input time.

        Parameter
        ---------
        The name of the course.

        Example
        -------
        (Homework Log) record math305
        (Homework Log) record Math 305
        (Homework Log) record MATH 305

        """

        # Example format: 'math305' --> 'MATH 305'
        coursename = self.correctformat(coursename)

        if coursename in self.courses:
            self.record(coursename, self.checkvalue('', float))
        else:
            print('Invalid course name.')

    def do_undo(self, args):
        """
        Prompt user to input number of lines to undo.

        Example
        -------
        (Homework Log) undo

        """

        # Prints the amount of lines that can be undone
        print('{0} lines of data logged'.format(self.linesofdata))

        # Check to make sure linesundone is a valid int
        linesundone = self.checkvalue('', int)

        # Range of valid ints is 0 to the lines added during the program
        if linesundone in range(0, self.linesofdata+1):

            self.writer.remove_rows(linesundone)
            self.linesofdata -= linesundone
            print('{} lines removed.'.format(linesundone))

        # Ignore escape command
        elif linesundone != 'exit':
            print('Invalid value.')

    def do_quit(self, args):
        """
        Exit the program.

        Example
        -------
        (Homework Log) quit

        """

        print('{} lines of data recorded.'.format(self.linesofdata))

        if self.linesofdata > 0:

            analyze = AnalyzeData(self.logfile, self.logpath, self.semester)
            analyze.analyze_data()

        return True

    def record(self, coursename, hourslogged):
        """
        Write to the csv file and inform user of hours logged.

        Parameters
        ----------
        coursename  : The name of the course.
        hourslogged : The study hours logged.

        """

        # Ignores the exit command
        if hourslogged != 'exit':
            self.writer.log_hours(coursename, hourslogged)
            print('{} hours logged in {}.'.format(hourslogged, coursename))

            self.linesofdata += 1


    def timer(self):
        """
        Return the eclipsed time from the start of the timer to the end.

        """

        starttime = time.clock()

        # Stop the timer
        command = input("press any button to finish (or 'exit' to cancel)>>>")

        if command == 'exit':
            return command

        # Eclipsed time
        return (time.clock() - starttime) / 3600

    def correctformat(self, coursename):
        """
        Return the course name correctly formatted.

        Parameters
        ----------
        coursename : The unformated name of the course

        """

        if len(coursename) == 7:
            coursename = coursename[:4] + ' ' + coursename[4:]

        return coursename.upper()

    def checkvalue(self, value, valuetype):
        """
        Return either a value of a specified type of 'exit'

        parameters
        ----------
        value     : The value being checked.
        valuetype : The correct type.

        """

        while not isinstance(value, valuetype) and value != 'exit':

            value = input("Enter value (or 'exit')>>>")


            try:
                value = valuetype(value)
            except ValueError:
                pass

        return value

Homework().cmdloop()
