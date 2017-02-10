import config

def strip_string(input):
    """Return the string in lowercase without whitespace.

    Keyword Arguments:
    input -- the string to be lowercased and stripped of whitespace
    """
    return input.lower().replace(" ", "")

def course_name(input):
    """Returns the correctly formatted course name or the initial input

    Keyword Arguments:
    input -- the possible key to the course name.
    """
    for course in config.current_courses:
        if strip_string(course) == strip_string(input):
            return course

    return input
