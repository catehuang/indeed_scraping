# Libraries
import re
import time


from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Driver path
load_dotenv()
path = os.getenv("CHROME_DRIVER_PATH")
service = Service(path)
driver = webdriver.Chrome(service=service)

# Maximize Window
driver.maximize_window()
driver.minimize_window()
driver.maximize_window()
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

# Keywords for searching
# job position
what = os.getenv('WHAT')
# job location
where = os.getenv('WHERE')
# create url
url = 'https://ca.indeed.com/jobs?'
if what is not None:
    position_keywords = what.replace(' ', '+')
    url += 'q=' + position_keywords
if where is not None:
    location = where.replace(' ', '+').replace(',', '%2C')
    url += '&l=' + location
# days = 1/3/7/14
posted_within = os.getenv('WITHIN_DAYS')
if posted_within is not None:
    url += '&fromage=' + str(posted_within)
# is remote
if os.getenv('IS_REMOTE'):
    url += '&sc=0kf%3Aattr(DSQF7)%3B'

# Enter the url
driver.get(url)
time.sleep(2)

def next_page_number():
    """Return the next page number if there is a next page; otherwise return -1"""
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    page_block = job_list_block.find_element(By.CSS_SELECTOR, 'nav')
    # current page is button, otherwise anchors
    all_divs = page_block.find_elements(By.CSS_SELECTOR, 'div')
    # there is no any page number
    if all_divs is None:
        return -1

    current_number = 0

    for div in all_divs:
        is_button = None
        is_anchor = None
        try:
            is_anchor = div.find_element(By.CSS_SELECTOR, 'a')
        except NoSuchElementException as e:
            is_button = div.find_element(By.CSS_SELECTOR, 'button')

        if is_button is not None:
            current_number = int(is_button.text)
        else:
            # could be < or >
            if re.match(r'\d', is_anchor.text):
                index = int(is_anchor.text)
                if current_number != 0 and index == current_number + 1:
                    return index
    return -1


def go_to_next_page(page_number):
    """ Click the next page number """
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    page_block = job_list_block.find_element(By.CSS_SELECTOR, 'nav')
    # current page is button, otherwise anchors
    anchors = page_block.find_elements(By.CSS_SELECTOR, 'a')
    for anchor in anchors:
        # could be < or >
        if re.match(r'\d', anchor.text):
            if int(anchor.text) == page_number:
                anchor.click()
                time.sleep(5)
                return


def is_qualified(title):
    """ Return true if the title fits certain conditions """
    if len(os.getenv('RULES_INCLUDED').split(" ")) != 0:
        including_certain_words = os.getenv('RULES_INCLUDED').split(" ")
        rule_string = ""
        counter = 1
        for rule in including_certain_words:
            if counter > 1:
                rule_string += "|"
            rule_string += rule
            counter += 1

        if re.search(rf"({rule_string})", title, re.I) is None:
            print("no keywords included")
            return False

    if len(os.getenv('RULES_EXCLUDED').split(" ")) != 0:
        excluding_certain_words = os.getenv('RULES_EXCLUDED').split(" ")
        rule_string = ""
        counter = 1
        for rule in excluding_certain_words:
            if counter > 1:
                rule_string += "|"
            rule_string += rule
            counter += 1

        if re.search(rf"({rule_string})", title, re.I):
            print("included exclude keywords")
            return False
    return True


def scraping_a_page():
    """ Scraping data from a page """
    # Locate target block
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')

    # left column - job list and total number of jobs
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    job_lists = job_list_block.find_elements(By.CLASS_NAME, 'job_seen_beacon')

    # click qualified jobs and grep the content
    for job in job_lists:
        job_result_block = job.find_element(By.CSS_SELECTOR, 'td') and job.find_element(By.CLASS_NAME, 'resultContent')
        job_title_block = job_result_block.find_element(By.CSS_SELECTOR, 'h2')
        # filter jobs by their titles
        if is_qualified(job_title_block.text):
            company_name_block = job_result_block.find_element(By.CLASS_NAME, 'companyName')
            company_location_block = job_result_block.find_element(By.CLASS_NAME, 'companyLocation')
            job_title_block.click()
            time.sleep(2)
            # right column - content
            right_panel = main_block.find_element(By.CLASS_NAME, 'jobsearch-RightPane')
            apply_button_block = right_panel.find_element(By.ID, 'jobsearch-ViewJobButtons-container')
            # there are two kinds of button/link for applying a job
            # link - Apply on company website
            ''' need time to think about this part
            try:
                # is a button - Apply now
                apply_button = apply_button_block.find_element(By.CLASS_NAME, 'ia-IndeedApplyButton')
                apply_item = apply_button.find_element(By.CLASS_NAME, 'indeed-apply-widget')
                backurl = apply_item.get_attribute('data-indeed-apply-pingbackurl')
                token = apply_item.get_attribute('data-indeed-apply-apitocken')
            except NoSuchElementException:
                apply_item = apply_button_block.find_element(By.CLASS_NAME, 'a')
                company_url = apply_item.get_attribute('href')
            '''

            job_content_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-JobComponent-description')
            job_description = job_content_block.find_element(By.ID, 'jobDescriptionText')

            print(f"Found the job as {job_title_block.text}")
            # print(f"Position: {job_title_block.text}")
            # print(f"Company: {company_name_block.text}")
            # print(f"Location: {company_location_block.text}")
            # print("Job Description:")
            # print(job_description.text)
            # print()

            f.write(f"Position: {job_title_block.text}\n")
            f.write(f"Company: {company_name_block.text}\n")
            f.write(f"Location: {company_location_block.text}\n")
            f.write(f"Apply Link:\n")
            f.write("Job Description:\n")
            f.write(job_description.text)
            f.write('\n\n')
        # scroll down for each job element
        driver.execute_script("arguments[0].scrollIntoView();", job)


with open('job.txt', 'w', encoding="UTF-8") as f:
    max_page_index = 3
    keep_going = True
    print(f"# Collect page 1")
    while keep_going:
        scraping_a_page()
        next_page = next_page_number()
        current_page = next_page - 1
        if next_page != -1 and next_page < 4:
            print(f"\n# Collect page {next_page}")
            go_to_next_page(next_page)
        else:
            keep_going = False
f.close()
print("Done!")



