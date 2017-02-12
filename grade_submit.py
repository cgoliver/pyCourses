import re
import time
import sys
import getpass
import argparse
import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

myCourses_login_URL = "https://mycourses2.mcgill.ca/Shibboleth.sso/Login"
course_url = "https://mycourses2.mcgill.ca/d2l/home/253655"
driver = webdriver.Chrome()


class MissingGradeException(Exception):
    pass
def login(uname, passwd):
    driver.get(myCourses_login_URL)
    username = driver.find_element_by_name('j_username')
    password = driver.find_element_by_name('j_password')

    username.send_keys(uname)
    password.send_keys(passwd)

    submit = driver.find_element_by_name('_eventId_proceed')
    submit.click()


def get_grade(feedback_string, submission):
    q_grade = re.compile(r"\d+/\d+") 
    matches = q_grade.findall(feedback_string)
    score = 0
    total = 0
    if len(matches) != 4:
        raise MissingGradeException
    for m in matches:
        nums = m.split("/")
        score += int(nums[0])
        total += int(nums[1])
   
    return int((float(score) / total) * 100)

def next_student(publish=False):
    js_wait(By.LINK_TEXT, "Save Draft").click()
    if publish:
        try:
            driver.find_element_by_link_text("Publish").click()
        except:
            driver.find_element_by_link_text("Update").click()
            
    try:
        driver.find_element_by_link_text("Next Student").click()
    except:
        print("no next student")
        sys.exit()
     
def js_wait(by, label, timeout=10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, label)))

def select_course(due_date, cutoff, publish=False):
    # driver.get("https://mycourses2.mcgill.ca/d2l/home/253655")
    driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=62409&ou=253655")

    name = js_wait(By.LINK_TEXT, "Draft Saved:")
    name.click()
    name.send_keys(Keys.RETURN) 

    submission = 1

    while True:
        text_box = js_wait(By.CLASS_NAME, "d2l-htmleditor-textarea")
        text = text_box.get_attribute("value")

        date_fields = driver.find_elements_by_class_name("ds_b")

        student = date_fields[2].text

        late_penalty = 0

        for d in date_fields:
            try:
                date = datetime.datetime.strptime(d.text, "%b %d, %Y %I:%M %p") 
                if due_date < date < cutoff:
                    late_penalty = 20
                    # print("\t".join([date,student,"penalty: {0}".format(late_penalty)]))
                elif date > cutoff:
                    late_penalty = 100
                    # print("\t".join([date, student,"penalty: {0}".format(late_penalty)]))
                else:
                    break
            except ValueError:
                continue

        try:
            grade = max(0, get_grade(text, submission) - late_penalty)
        except MissingGradeException:
            print("Submission {0} incomplete.".format(submission))
            next_student(publish=publish)
            submission += 1
            continue

        gradebox = js_wait(By.CSS_SELECTOR, ".d_edt.vui-input")
        gradebox.clear()
        gradebox.send_keys(str(grade))

        next_student(publish=publish)
        submission += 1

if __name__ == "__main__":
    pswd = getpass.getpass("McGill Password: ")
    due = datetime.datetime(2017, 2, 2, hour=2)
    cutoff = datetime.datetime(2017, 2, 3)
    login('carlos.gonzalezoliver@mail.mcgill.ca', pswd)
    # select_course(due, cutoff, publish=True)
