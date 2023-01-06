## indeed_scraping

### Purpose 
- Even you carefully selected your keywords and typed them into the search field on the Indeed, you get tons of results that you don't want. You spend your valuable time to read all titles and click the next page repeatedly until you get bored or luckily reach the end of the result.

- This application uses Python and Selenium to filter search results from Indeed, and generates a file job.csv with a time tag under logs folder which saves all qualified jobs with their job information.

### How to use this application
- You will need to download the Chrome Drive corresponding to your Chrome version, and create a file named .env to write down your preferences. 

- The .env should contain the following information
<pre>
# the path of chrome drive
CHROME_DRIVER_PATH=
# what position are you looking for
WHAT=
# where the location of the job
WHERE=
# the range of the posted date between 1/3/7/14 days
WITHIN_DAYS=
# are you looking for remote jobs? 0 or 1
IS_REMOTE=
# what are the keywords you want to see them on the title? keywords should be separated by a space 
RULES_INCLUDED=
# what are the keywords you don't want them show on the title of the position? keywords should be separated by a space 
RULES_EXCLUDED=
</pre>

- Run main.py to scrap data from Indeed. If the number of jobs on Indeed for the specified position, location, and date posted is more than 1500, it will prompt for a confirmation to continue since it may take hours to finish the task.

- After the scraping task completed, type "flask --app show_pages run" in the Terminal, then open browser for localhost:5000. You will see all filtered results on web pages.

- Note: These processes will be improved later.

<img src="https://user-images.githubusercontent.com/35821309/211101442-1dfe7ecb-84fa-4194-907d-7f1e420841af.png" width="80%" />


### How to choose the included/excluded keywords? / How do I make sure I selected the right words for searching?
- When the application starts to scrap the from Indeed, it also shows messages including the job titles, the reason why the jobs doesn't be collected if they are not qualify for the requirement you assigned, and the links for applying a job.
- You can ues these messages from console to check the keywords you assigned and determine if the keywords are right or wrong.
