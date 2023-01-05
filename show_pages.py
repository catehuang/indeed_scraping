import pandas as pd
import os
from flask import Flask, render_template, url_for, request, redirect, abort, flash
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

# setup flask
app = Flask("__name__")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap(app)
PORT = 5000

# deal with data, using dictionary is better than the class since there are lots of efforts needed to do
# between html and js
jobs = []
file_path = "logs/job-2023-01-03-221026.csv"
df = pd.read_csv(file_path, encoding='utf8')
# technically the max index of the row is df.shape[0], but the first row in header which is not what we want
for row_index in range(0, df.shape[0]):
    job = {
        'title': df.iloc[row_index][0],
        'company_name': df.iloc[row_index][1],
        'link': df.iloc[row_index][2],
        'location': df.iloc[row_index][3],
        'description': df.iloc[row_index][4]
    }
    jobs.append(job)


@app.route("/")
def home():
    # includes both start and stop item
    current_job_list = jobs[:14]
    return render_template("page.html", total_number_of_jobs=df.shape[0], page_id=0, jobs=current_job_list)


@app.route("/page/<int:page_id>")
def show_page(page_id):
    current_job_list = jobs[page_id * 15: (page_id + 1) * 15 - 1]
    return render_template("page.html", total_number_of_jobs=df.shape[0], page_id=page_id, jobs=current_job_list)


if __name__ == "__show_pages__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
