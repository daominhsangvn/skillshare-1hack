import sys, os
from skillshare import Skillshare
from magic import cookie

# or by class ID:
# dl.download_course_by_class_id(189505397)

def main():
    dl = Skillshare(cookie)
    target_folder = sys.argv[1]
    course_url = sys.argv[2]
    course_urls = course_url.split(',')
    print("Total courses: " + str(len(course_urls)))
    for co in course_urls:
        print("Starting: " + co)
        dl.download_course_by_url(co, target_folder)
        print("______________________ FINISHED ______________________")
        print("")


def info():
    print(r"""""")


if __name__ == "__main__":
    info()
    main()
