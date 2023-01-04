# Libraries
import datetime
import math
import re
import sys
import time
import os
from dotenv import load_dotenv
import pandas as pd
from bs4 import BeautifulSoup
import requests

import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Driver path
load_dotenv()
path = os.environ.get("CHROME_DRIVER_PATH")
if path is None:
    raise ValueError('Please specify the path of Chrome Drive!')
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
what = os.environ.get('WHAT')
if what is None:
    raise ValueError('Please specify the job title you are looking for!')

# job location
where = os.environ.get('WHERE')
if where is None:
    raise ValueError('Please specify the job location you prefer!')

# create url
url = 'https://ca.indeed.com/jobs?'
if what is not None:
    position_keywords = what.replace(' ', '+')
    url += 'q=' + position_keywords
if where is not None:
    location = where.replace(' ', '+').replace(',', '%2C')
    url += '&l=' + location

# days = 1/3/7/14
posted_within = os.environ.get('WITHIN_DAYS')
if posted_within is not None:
    url += '&fromage=' + str(posted_within)

# is remote
if os.environ.get('IS_REMOTE'):
    url += '&sc=0kf%3Aattr(DSQF7)%3B'

# Enter the url
driver.get(url)
time.sleep(2)

# counter for collected jobs
collected_jobs = 0
# store data
job_titles = []
company_names = []
company_locations = []
apply_links = []
job_descriptions = []


def get_total_number_of_jobs():
    try:
        main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
        job_count_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')
        job_count_span = job_count_block.find_elements(By.CSS_SELECTOR, 'span')
        job_count = job_count_span.__getitem__(0).text
        job_number = re.sub('[^0-9]', '', job_count)
        print(f"Total number of jobs is {job_number}, "
              f"and there are about {math.ceil(int(job_number) / 15)} pages based on the total number\n")
        return job_number
    except NoSuchElementException:
        # raise ValueError("Can't find any result for the job title!")
        return -1


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
                # deal with the popup window if there's one
                try:
                    popup_window_close = driver.find_element(By.XPATH,
                                                             '//*[@id="mosaic-modal-mosaic-provider-desktopserp-'
                                                             'jobalert-popup"]/div/div/div[1]/div/button')
                    popup_window_close.click()
                    time.sleep(1)
                except NoSuchElementException as e:
                    pass

                return


def is_qualified(title):
    """ Return true if the title fits certain conditions """
    if len(os.environ.get('RULES_INCLUDED').split(" ")) != 0:
        including_certain_words = os.environ.get('RULES_INCLUDED').split(" ")
        rule_string = ""
        counter = 1
        for rule in including_certain_words:
            if counter > 1:
                rule_string += "|"
            rule_string += rule
            counter += 1

        if re.search(rf"({rule_string})", title, re.I) is None:
            print(f"no keywords included - {title}")
            return False

    if len(os.environ.get('RULES_EXCLUDED').split(" ")) != 0:
        excluding_certain_words = os.environ.get('RULES_EXCLUDED').split(" ")
        rule_string = ""
        counter = 1
        for rule in excluding_certain_words:
            if counter > 1:
                rule_string += "|"
            rule_string += rule
            counter += 1

        if re.search(rf"({rule_string})", title, re.I):
            print(f"included exclude keywords - {title}")
            return False
    return True


def scraping_a_page():
    """ Scraping data from a page """
    # For measuring performance
    start_time = time.time()
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
            # Get one job information!
            global collected_jobs
            collected_jobs += 1

            company_name_block = job_result_block.find_element(By.CLASS_NAME, 'companyName')
            company_location_block = job_result_block.find_element(By.CLASS_NAME, 'companyLocation')
            job_title_block.click()
            time.sleep(2)
            # right column - content
            right_panel = main_block.find_element(By.CLASS_NAME, 'jobsearch-RightPane')

            # grep the apply link
            apply_button_block = right_panel.find_element(By.ID, 'jobsearch-ViewJobButtons-container')
            # there are two kinds of button/link for applying a job
            link = ""
            try:
                # 1) is an anchor link for applying on company site
                apply_button_area = apply_button_block.find_element(By.ID, 'applyButtonLinkContainer')
                link = apply_button_area.find_elements(By.CSS_SELECTOR, 'a').__getitem__(0).get_attribute('href')
            except NoSuchElementException:
                # 2) is a button - Apply now; copy the page url
                apply_button_area = apply_button_block.find_element(By.CLASS_NAME, 'ia-IndeedApplyButton')
                link = apply_button_area.find_element(By.CSS_SELECTOR, 'span') \
                    .get_attribute('data-indeed-apply-joburl')

            job_content_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-JobComponent-description')
            job_description = job_content_block.find_element(By.ID, 'jobDescriptionText')

            print(f"Found the job as {job_title_block.text} - {link}")
            # print(f"Position: {job_title_block.text}")
            # print(f"Company: {company_name_block.text}")
            # print(f"Location: {company_location_block.text}")
            # print("Job Description:")
            # print(job_description.text)
            # print()

            global job_titles, company_names, company_locations, apply_links, job_descriptions
            job_titles.append(job_title_block.text)
            company_names.append(company_name_block.text)
            company_locations.append(company_location_block.text)
            apply_links.append(link)
            job_descriptions.append(job_description.text)
        # scroll down for each job element
        driver.execute_script("arguments[0].scrollIntoView();", job)

    # For measuring time
    end_time = time.time()
    spent_time_one_this_page = int(end_time - start_time)
    print(f"Spent {spent_time_one_this_page}s on this page\n")


total_jobs = int(get_total_number_of_jobs())
if total_jobs == -1:
    print(f"Can't find any job for the position of {what} in {where} with assigned patterns\n")
    sys.exit(0)

if total_jobs > 1500:
    user_input = input(f"There are {total_jobs} jobs on Indeed. It might take hours for scraping data.\n"
                       f"Do you want to continue? yes/no ")
    if re.match(r'(no|n)', user_input, re.I):
        print("Try to change the position(what), location(where) or date posted(WITHIN_DAYS) "
              "to narrow down the result\n")
        sys.exit(0)
    else:
        print("Alright, let's go!\n")

tag = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
# Start to scrap data
s_time = time.time()
keep_going = True

print(f"# Collect page 1")
while keep_going:
    scraping_a_page()
    next_page = next_page_number()
    current_page = next_page - 1
    if next_page != -1:
        print(f"\n# Collect page {next_page}")
        go_to_next_page(next_page)
    else:
        keep_going = False

# create csv file , encoding='utf8'
df = pd.DataFrame(list(zip(job_titles, company_names, apply_links, company_locations, job_descriptions)),
                  columns=["job_title", "company_name", "apply_link", "company_location", "job_description"])
df.to_csv(f"logs/job-{tag}.csv", index=False)

e_time = time.time()
t_time = (e_time - s_time) / 60
print(f"{collected_jobs} jobs collected!")
print("Spent {:.2f} minutes".format(t_time))
print("Done!")
