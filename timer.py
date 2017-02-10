import write
from datetime import datetime

class Timer:

    def __init__(self, course_name):
        self.course_name = course_name
        self.start_time = None
        self.end_time = None

    def start(self):
        """Starts the timer."""
        self.start_time = datetime.today()

    def stop(self):
        """Ends the timer."""
        self.end_time = datetime.today()
        self.log(self.start_time, self.end_time)

    def log(self, time_one, time_two):
        """
        Creates a log entry for each day the timer runs.

        Keyword arguments:
        time_one -- the start time for the log entry
        time_two -- the end time for the log entry
        """
        if time_one.date() == time_two.date():
            write.given_dates(self.course_name, time_one, time_two)

        else:
            # temp_time is the day after time_one
            temp_time = datetime(
                    time_one.year,
                    time_one.month,
                    time_one.day + 1
                    )
            write.given_dates(self.course_name, time_one, temp_time)
            # Creates new log entry for the next day
            self.log(temp_time, time_two)
