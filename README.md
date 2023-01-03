# indeed_scraping
Even you carefully selected your keywords and typed them into the search field on the Indeed, you get tons of results that you don't want. You spend your valuable time to read all titles and click the next page repeatly until you get bored or luckily reach the end of the result.

This application uses Python and Selenium to filter search results from Indeed, and generates a file job.txt which saves all qualified jobs with their job information.

You will need to download the Chrome Drive corresponding to your Chrome version, and create a file named .env to write down your preferences. 

The .env should contain the following information
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
# what are the keywords you want to see them on the title? keywords should be seperated by a space 
RULES_INCLUDED=
# what are the keywords you don't want them show on the title of the position? keywords should be seperated by a space 
RULES_EXCLUDED=
</pre>
