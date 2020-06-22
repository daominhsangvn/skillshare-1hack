import sys, os
from skillshare import Skillshare
from magic import cookie

# or by class ID:
# dl.download_course_by_class_id(189505397)

def main():
    dl = Skillshare(cookie)
    course_url = sys.argv[1]
    course_urls = course_url.split(',')
    print(course_urls)
    for co in course_urls:
        print(co)
        dl.download_course_by_url(co)


def info():
    print(r"""""")


if __name__ == "__main__":
    info()
    main()
