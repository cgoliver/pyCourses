import re
import time
import sys
import getpass
import argparse
import datetime
import cPickle as pickle

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

myCourses_login_URL = "https://mycourses2.mcgill.ca/Shibboleth.sso/Login"
course_url = "https://mycourses2.mcgill.ca/d2l/home/271835"
driver = webdriver.Chrome('/Users/carlosgonzalezoliver/Downloads/chromedriver')

class MissingGradeException(Exception):
    pass
def login(uname, passwd):
    print("logging in")
    driver.get(myCourses_login_URL)
    username = driver.find_element_by_name('j_username')
    password = driver.find_element_by_name('j_password')

    username.send_keys(uname)
    password.send_keys(passwd)

    submit = driver.find_element_by_name('_eventId_proceed')
    submit.click()


def get_grade(feedback_string, submission, base=None):
    q_grade = re.compile(r"\d+/\d+") 
    matches = q_grade.findall(feedback_string)
    score = 0
    total = 0
    if len(matches) != 2:
        raise MissingGradeException
    for m in matches:
        nums = m.split("/")
        score += int(nums[0])
        total += int(nums[1])
   
    if not base:
        return int((float(score) / total) * 100)
    else:
        return score

def next_student(publish=False):
    # js_wait(By.LINK_TEXT, "Save Draft").click()
    if publish:
        try:
            driver.find_element_by_link_text("Update").click()
        except:
            driver.find_element_by_link_text("Publish").click()
            
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
    # driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=64199&ou=253655")
    #a1
    driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=65797&ou=271835")
    #a2
    # driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=65885&ou=271835")
    #a3
    # driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=65996&ou=271835")
    #a4
    # driver.get("https://mycourses2.mcgill.ca/d2l/lms/dropbox/admin/mark/folder_submissions_users.d2l?db=66268&ou=271835")


    # name = js_wait(By.LINK_TEXT, "Published:")
    name = js_wait(By.LINK_TEXT, "Published:")
    name.click()
    # name.send_keys(Keys.RETURN) 

    submission = 1

    ass_info = {}

    while True:
        text_box = js_wait(By.CLASS_NAME, "d2l-htmleditor-textarea")
        text = text_box.get_attribute("value")

        date_fields = driver.find_elements_by_class_name("ds_b")

        student = date_fields[2].text
        print(student)
        #Yahya Abdul Aziz (Id: 260640407)
        # student_info = driver.find_element_by_xpath("//*[@id=\"z_ba\"]/div[1]/div/div/div/div/div/div[1]/div/table/tbody/tr/td[2]/table/tbody/tr[1]/td/label/strong").text
        student_info = driver.find_elements_by_xpath("//*[contains(text(),\
            'Id:')]")[1].text
        student_name = student_info.split("(")[0]
        student_id = student_info.split()[-1].strip(")")

        late_penalty = 0

        # for d in date_fields:
            # try:
                # date = datetime.datetime.strptime(d.text, "%b %d, %Y %I:%M %p") 
                # if due_date < date < cutoff:
                    # print("late!")
                    # print(due_date, date, cutoff)
                    # late_penalty = 4
                    # # print("\t".join([date,student,"penalty: {0}".format(late_penalty)]))
                # elif date > cutoff:
                    # late_penalty = 20
                    # # print("\t".join([date, student,"penalty: {0}".format(late_penalty)]))
                # else:
                    # break
            # except ValueError:
                # continue

        try:
            grade = get_grade(text, submission, base=100)
            # grade = max(0, get_grade(text, submission, base=20) - late_penalty)
            print(grade)
        except MissingGradeException:
            print("Submission {0} incomplete.".format(submission))
            # next_student(publish=publish)
            gradebox = js_wait(By.CSS_SELECTOR, ".d_edt.vui-input")
            print(gradebox.__dict__)
            grade = gradebox.text
            submission += 1

        print(ass_info)
        ass_info[int(student_id)] = {'grade': int(grade), 'name': student_name, 'feedback':\
            text}
        with open("202_a1_grading_box.pickle", "wb") as p:
            pickle.dump(ass_info, p)

        # gradebox = js_wait(By.CSS_SELECTOR, ".d_edt.vui-input")
        # gradebox.clear()
        # gradebox.send_keys(str(grade))

        next_student(publish=publish)
        submission += 1

if __name__ == "__main__":
    # pswd = getpass.getpass("McGill Password: ")
    pswd = "sasjajuli_milojuli"
    due = datetime.datetime(2017, 3, 27, hour=2)
    cutoff = datetime.datetime(2017, 3, 27, hour=23, minute=59)
    login('carlos.gonzalezoliver@mail.mcgill.ca', pswd)
    select_course(due, cutoff, publish=False)
