# Libraries
import re
import time
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
from selenium import webdriver
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
what = 'software engineer'
# job location
where = 'Calgary, AB'
# create url
position_keywords = what.replace(' ', '+')
location = where.replace(' ', '+').replace(',', '%2C')
url = 'https://ca.indeed.com/jobs?q=' + position_keywords + '&l=' + location

# Enter the url
driver.get(url)
time.sleep(2)


def find_total_number_of_jobs():
    # Locate target block
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    total_jobs_block = job_list_block.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')
    total_jobs = total_jobs_block.find_element(By.CSS_SELECTOR, 'span')
    max_value = re.sub(r'\D', "", total_jobs.text)
    max_page_index = int(max_value) / 15
    if int(max_value) % 15 == 0:
        return int(max_page_index)
    else:
        return int(max_page_index) + 1


def go_to_page(next_page):
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    page_block = job_list_block.find_element(By.CSS_SELECTOR, 'nav')
    # current page is button, otherwise anchors
    other_pages = page_block.find_elements(By.CSS_SELECTOR, 'a')
    for page in other_pages:
        if page.text == next_page:
            page.click()
            time.sleep(5)


def scraping_a_page():
    # Locate target block
    main_block = driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')

    # left column - job list and total number of jobs
    job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
    job_lists = job_list_block.find_elements(By.CLASS_NAME, 'job_seen_beacon')

    # click qualified jobs and grep the content
    for job in job_lists:
        job_result_block = job.find_element(By.CSS_SELECTOR, 'td') and job.find_element(By.CLASS_NAME, 'resultContent')
        job_title_block = job_result_block.find_element(By.CSS_SELECTOR, 'h2')
        company_name_block = job_result_block.find_element(By.CLASS_NAME, 'companyName')
        company_location_block = job_result_block.find_element(By.CLASS_NAME, 'companyLocation')
        job_title_block.click()
        time.sleep(2)
        # right column - content
        job_content_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-JobComponent-description')
        job_description = job_content_block.find_element(By.ID, 'jobDescriptionText')
        print(f"Position: {job_title_block.text}")
        print(f"Company: {company_name_block.text}")
        print(f"Location: {company_location_block.text}")
        print("Job Description:")
        print(job_description.text)
        print()

        f.write(f"Position: {job_title_block.text}\n")
        f.write(f"Company: {company_name_block.text}\n")
        f.write(f"Location: {company_location_block.text}\n")
        f.write("Job Description:\n")
        f.write(job_description.text)
        f.write('\n\n')
        # scroll down for each job element
        driver.execute_script("arguments[0].scrollIntoView();", job)


with open('job.txt', 'w', encoding="UTF-8") as f:
    max_page_index = find_total_number_of_jobs()
    for page_number in range(1, max_page_index + 1):
        f.write(f"### page {page_number}\n")
        if page_number > 1:
            go_to_page(page_number)
        scraping_a_page()
f.close()



