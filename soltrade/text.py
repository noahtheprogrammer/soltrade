import os
import datetime

# Required in order to display native colors on Windows
os.system("")

# Color class values appended to success and error messages
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class timestamp:
    def find_time():
        return '{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())