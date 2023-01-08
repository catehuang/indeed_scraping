import json
import sys
import os
import re
import time
import datetime
import pandas
from scrap_data import DataCollection, Job

file_name = ""


def prepare_data():
    jobs = []
    # setup all conditions and make sure there is data meets requirement and the amount of data is not out of the scope
    data_collection = DataCollection()
    search_for = data_collection.read_configuration()
    data_collection.start_window()
    total_jobs = int(data_collection.get_total_number_of_jobs())

    if total_jobs == -1:
        print(
            f"Can't find any job for the position of {search_for.what} in {search_for.where} with assigned patterns\n")
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
    global file_name
    file_name = f"logs/job-{tag}.csv"
    s_time = time.time()
    keep_going = True

    while keep_going:
        # get jobs info from a page
        jobs.extend(data_collection.scraping_a_page())

        # click the next page if there is a next page
        next_page = data_collection.next_page_number()
        if next_page != -1:
            data_collection.go_to_next_page(next_page)
        else:
            keep_going = False

    # save search results to a file as json format
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    # deal with data
    titles = []
    company_names = []
    locations = []
    links = []
    descriptions = []
    for job in jobs:
        titles.append(job.title)
        company_names.append(job.company_name)
        locations.append(job.location)
        links.append(job.link)
        descriptions.append(job.description)
    df = pandas.DataFrame(list(zip(titles, company_names, links, locations, descriptions)),
                          columns=["title", "company_name", "link", "location", "description"])
    df.to_csv(f"logs/job-{tag}.csv", index=False)

    e_time = time.time()
    t_time = (e_time - s_time) / 60
    print(f"\n{len(jobs)} jobs collected!")
    print("Spent {:.2f} minutes for scraping data\n".format(t_time))


# get data
prepare_data()
# render data
os.system(f"python show_pages.py {file_name}")
