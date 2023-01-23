# Libraries
import math
import re
import time
import os
from dotenv import load_dotenv

# import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class Job:
    def __init__(self, title, company_name, link, location, description):
        self.title = title
        self.company_name = company_name
        self.link = link
        self.location = location
        self.description = description


class DataCollection:
    def __init__(self):
        """ Set up web driver, read configurations from environment variables """
        # Driver path
        load_dotenv()
        path = os.getenv("CHROME_DRIVER_PATH")
        if path is None:
            raise ValueError('Please specify the path of Chrome Drive!')
        service = Service(path)
        self.driver = webdriver.Chrome(service=service)
        self.url = 'https://ca.indeed.com/jobs?'

    def read_configuration(self):
        """ Read configuration from .env file, return the search keywords in dictionary"""
        # Keywords for searching
        # job position
        what = os.getenv('WHAT')
        if what is None:
            raise ValueError('Please specify the job title you are looking for!')

        # job location
        where = os.getenv('WHERE')
        if where is None:
            raise ValueError('Please specify the job location you prefer!')

        # generate url
        if what is not None:
            position_keywords = what.replace(' ', '+')
            self.url += 'q=' + position_keywords
        if where is not None:
            location = where.replace(' ', '+').replace(',', '%2C')
            self.url += '&l=' + location

        # days = 1/3/7/14
        posted_within = os.getenv('WITHIN_DAYS')
        if posted_within is not None:
            self.url += '&fromage=' + str(posted_within)

        # is remote
        is_remote = 0
        if os.getenv('IS_REMOTE'):
            is_remote = 1
            self.url += '&sc=0kf%3Aattr(DSQF7)%3B'

        search_for = {
            "what": what,
            "where": where,
            "posted_within": posted_within,
            "is_remote": is_remote
        }
        return search_for

    def start_window(self):
        """ Set up the windows size for selenium, and get the url """
        # Maximize Window
        self.driver.maximize_window()
        self.driver.minimize_window()
        self.driver.maximize_window()
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.driver.implicitly_wait(10)
        # Enter the url
        self.driver.get(self.url)
        time.sleep(2)

    def get_total_number_of_jobs(self):
        """ Read and return the total number of jobs from indeed """
        try:
            main_block = self.driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
            job_count_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')
            job_count_span = job_count_block.find_elements(By.CSS_SELECTOR, 'span')
            job_count = job_count_span.__getitem__(0).text
            job_number = re.sub('[^0-9]', '', job_count)
            real_job_number = int(int(job_number)/1.5)
            print(f"Total number of jobs on Indeed is {job_number}, "
                  f"and there are about {math.ceil(int(job_number) / 15)} pages based on the total number.\n"
                  f"(However, the real number of jobs could be {real_job_number}, "
                  f"and total pages is {math.ceil(real_job_number / 15)} )\n")
            return real_job_number
        except NoSuchElementException:
            # raise ValueError("Can't find any result for the job title!")
            return -1

    def next_page_number(self):
        """Return the next page number if there is a next page; otherwise return -1"""
        main_block = self.driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
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
            except NoSuchElementException:
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

    def go_to_next_page(self, page_number):
        """ Click the next page number """
        main_block = self.driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')
        job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
        page_block = job_list_block.find_element(By.CSS_SELECTOR, 'nav')
        # current page is button, otherwise anchors
        anchors = page_block.find_elements(By.CSS_SELECTOR, 'a')
        for anchor in anchors:
            # could be < or >
            if re.match(r'\d', anchor.text):
                if int(anchor.text) == page_number:
                    print(f"\n# page {page_number}")
                    anchor.click()
                    time.sleep(3)
                    # deal with the popup window if there's one
                    try:
                        popup_window_close = self.driver.find_element(By.XPATH,
                                                                      '//*[@id="mosaic-modal-mosaic-provider-'
                                                                      'desktopserp-jobalert-popup"]'
                                                                      '/div/div/div[1]/div/button')
                        popup_window_close.click()
                        time.sleep(1)
                    except NoSuchElementException:
                        pass

                    return

    def is_qualified(self, title):
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
                print(f"no keywords included - {title}")
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
                print(f"included exclude keywords - {title}")
                return False
        return True

    def filter_out_by_description(self, job_description):
        if len(os.getenv('FILTER_OUT_JOB_DESC').split(" ")) != 0:
            excluding_certain_words = os.getenv('FILTER_OUT_JOB_DESC').split(" ")
            rule_string = ""
            counter = 1
            for rule in excluding_certain_words:
                if counter > 1:
                    rule_string += "|"
                rule_string += rule
                counter += 1

            if re.search(rf"({rule_string})", job_description, re.I):
                return True
        return False

    def scraping_a_page(self):
        """ Scraping data from a page, and return an array of job dictionaries """
        jobs = []
        # Locate target block
        try:
            main_block = self.driver.find_element(By.CLASS_NAME, 'jobsearch-SerpMainContent')

            # left column - job list and total number of jobs
            job_list_block = main_block.find_element(By.CLASS_NAME, 'jobsearch-LeftPane')
            job_list = job_list_block.find_elements(By.CLASS_NAME, 'job_seen_beacon')

            # click qualified jobs and grep the content
            for job_on_list in job_list:
                job_result_block = job_on_list.find_element(By.CSS_SELECTOR, 'td') \
                                   and job_on_list.find_element(By.CLASS_NAME, 'resultContent')
                job_title_block = job_result_block.find_element(By.CSS_SELECTOR, 'h2')
                # filter jobs by their titles
                if self.is_qualified(job_title_block.text):
                    company_name_block = job_result_block.find_element(By.CLASS_NAME, 'companyName')
                    company_location_block = job_result_block.find_element(By.CLASS_NAME, 'companyLocation')
                    job_title_block.click()
                    time.sleep(2)
                    # right column - content
                    right_panel = main_block.find_element(By.CLASS_NAME, 'jobsearch-RightPane')

                    # grep the apply link
                    apply_button_block = right_panel.find_element(By.ID, 'jobsearch-ViewJobButtons-container')
                    # there are two kinds of button/link for applying a job

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

                    # add another filter for the content of the job description
                    if not self.filter_out_by_description(job_description.text):
                        print(f"Found the job as {job_title_block.text} - {link}")
                        # which data type is better to manipulate data?
                        # use arrays to save different columns, then use pandas to combine them as csv or json
                        # use objects to store jobs, then covert them to json (good to store to db)
                        # use json for each job (generate correct format is not easy)
                        job = Job(job_title_block.text, company_name_block.text, link, company_location_block.text,
                                  job_description.text)
                        jobs.append(job)
                # scroll down for each job element
                self.driver.execute_script("arguments[0].scrollIntoView();", job_on_list)
        except NoSuchElementException as e:
            print("something wrong about recognizing elements\n")
            print(e.msg)
            pass
        return jobs
