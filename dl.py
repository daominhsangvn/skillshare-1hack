import sys, os
from skillshare import Skillshare
from magic import cookie

# or by class ID:
# dl.download_course_by_class_id(189505397)

def main():
    target_folder = sys.argv[1]
    
    downloaded_history_file_name = "downloaded.txt"
    downloaded_history_file_path = "{target_folder}/{file_name}".format(target_folder=target_folder, file_name=downloaded_history_file_name)
    if not os.path.exists(downloaded_history_file_path):
        downloaded_history_file = open(downloaded_history_file_path, "w") 
        downloaded_history_file.write("")
        downloaded_history_file.close()
    
    course_url = sys.argv[2]
    course_urls = course_url.split(',')
    print("+ Total courses: " + str(len(course_urls)))
    print("")
    dl = Skillshare(cookie, downloaded_history_file_path)
    
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
