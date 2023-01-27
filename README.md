## indeed_scraping</h2>

### Purpose
  - Get those job information you are looking for by filtering in required keywords and/or out unrelated ones
  - Save your valuable time (up to 95%) from scanning all job titles and descriptions from Indeed
  - Easy to use and flexible. Only need to fill in your preferences, run the program, open your browser, and then apply jobs
  - It utilizes Python, Selenium and Pandas to scrape useful data from the website, and uses Flask, JavaScript and Ajax to provide a user-friendly website for users to read matched job information


### How to use this application
1. You will need to download the Chrome Drive corresponding to your Chrome version, install python packages, and create a file named .env to write down your preferences.
   - If your browser needs to be updated, you might have some unexpected errors occurred when you run the program

2. Create a .env file which should contain the following information
   - Values are case insensitive
   - Don't forget to use escape characters "\\" if the value contains special characters, such as ".", "+"

```
  # the path of chrome drive
  CHROME_DRIVER_PATH=
  
  # what position are you looking for
  # this value will feed to the search keyword on Indeed
  WHAT=
  
  # where the location of the job
  # this value will feed to the search keyword on Indeed
  WHERE=
  
  # the range of the posted date between 1/3/7/14 days
  # this value will feed to the search keyword on Indeed
  WITHIN_DAYS=
  
  # are you looking for remote jobs? 0 or 1
  # this value will feed to the search keyword on Indeed
  IS_REMOTE=
  
  # what are the keywords you want to see them on the title? keywords should be separated by a space
  # example: A B C => collect this job information if the job title contains A or B or C, otherwise ignore it
  # if you are looking for intern or co-op, you can try "intern co-op student"
  RULES_INCLUDED=
  
  # what are the keywords you don't want them show on the title of the position? keywords should be separated by a space
  # example: A B C => ignore this job information if the job title contains A or B or C, otherwise collect it
  # if you are looking for entry level job, you definitely don't want to see "manager lead senior sr\. intermediate staff" on the job title
  RULES_EXCLUDED=
  
  # filter out the job if the content contains the keyword (be general)
  # example: A B C => ignore this job information if the job description contains A or B or C
  FILTER_OUT_JOB_DESC=
  
  # filter out the job if it mentions/requires n+ years' of experience; n is the value you set in the below
  FILTER_OUT_BY_MIN_REQ_YEARS=
```
    
3. Execute main.py to start the program. And what do you expect for after you start running the program?
   <img src="https://user-images.githubusercontent.com/35821309/215185516-1122ef62-28cc-42ad-8cf1-20b376718783.png" width="70%" />     
   - If the program found the number of jobs on Indeed was zero or greater 1500, it will exit or prompt a message from the console to ask you if you want to continue scraping more than 1500 jobs
   - You might need to add more time for scraping if your computer's performance or network speed is not good enough
     - Symptoms: you can see messages in the terminal telling you the program skipped cases due to exceptions and complaining about no such elements
     - Solution: searching the function time.sleep() in scrap_data.py, and add more minutes
   - Check the messages and make sure the filtering patterns fit your need

5. After the scraping is done, you will see the message from the terminal
   <img src="https://user-images.githubusercontent.com/35821309/215188457-0d150842-6f76-4050-a829-921c6e31bb6b.png" width="70%" />
   
6. Open the browser and enter "localhost:5000". You will see all the collected jobs on the web page
   <img src="https://user-images.githubusercontent.com/35821309/211101442-1dfe7ecb-84fa-4194-907d-7f1e420841af.png" width="90%" />
