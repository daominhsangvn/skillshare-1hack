import sys
import os
from skillshare import Skillshare
from magic import cookie

# or by class ID:
# dl.download_course_by_class_id(189505397)


def main():
    dl = Skillshare(cookie)
    course_url = sys.argv[1]
    dl.download_course_by_url(course_url)


def info():
    if __name__ == "__main__":
        info()
        main()
