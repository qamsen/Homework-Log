import config
import course
import write
import cmd
from timer import Timer

class Homework(cmd.Cmd):

    intro = """
        Homework log. Type help or ? to list commands.

        Semester : {}
        Classes  : {}
        """.format(config.current_semester, config.current_courses)

    prompt = '(Homework Log)'

    def stop(self):
        """Stop timer when user enter a non-escape command.
        """
        command = input("Enter anything to finish (or 'exit' to cancel)>>>")
        return command != 'exit'

    def do_start(self, input):
        """Logs an entry for the homework log using a timer

        Keyword Arguments:
        input -- the name of the course (if not, no action performed)
        """
        course_name = course.course_name(input)

        if course_name in config.current_courses:
            timer = Timer(course_name)
            timer.start()

            if self.stop():
                timer.stop()

    def is_float(self, input):
        """Determines if an input is a float.
        """
        try:
            float(input)
            return True
        except ValueError:
            return False

    def hours_studied(self):
        """Takes a valid float from the user or the escape command
        """
        value = input("Enter value (or 'exit')>>>")
        while not self.is_float(value):
            value = input("Enter value (or 'exit')>>>")

            # Escape command
            if value == 'exit':
                return value

        return float(value)

    def do_record(self, input):
        """Logs an entry for the homework log using a user-entered value

        Keyword Arguments:
        input -- the name of the course (if not, no action performed)
        """
        course_name = course.course_name(input)

        if course_name in config.current_courses:
            hours_studied = self.hours_studied()

            # Checks for escape command
            if hours_studied != 'exit':
                write.to_csv(course_name, hours_studied)

    def do_quit(self, input):
        """Terminates the program
        """
        return True

Homework().cmdloop()
