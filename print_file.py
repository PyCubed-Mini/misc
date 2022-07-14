def print_file(filedir=None):
    """
    DEBUGGING
    print a file given its directory; file directory is by default None
    """
    # if no file directory is passed, use the directory of the log file
    if filedir is None:
        filedir = logfile

    print('--- Printing File: {} ---'.format(filedir))

    # open the current file directory as read only, print line by line
    # (removing whitespace)
    with open(filedir, "r") as file:
        for line in file:
            print(line.strip())
