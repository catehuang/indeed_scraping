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
file_path = "logs/job-2023-01-05-180256.csv"
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

total_number_of_jobs = df.shape[0]
total_pages = int(len(jobs) / 15)
if len(jobs) % 15 > 0:
    total_pages += 1


@app.route("/")
def home():
    return redirect(url_for('show_page', page_id=1))


@app.route("/page/<int:page_id>")
def show_page(page_id):
    if 0 < page_id <= total_pages:
        current_job_list = jobs[(page_id - 1) * 15: page_id * 15 - 1]
        return render_template("page.html", total_number_of_jobs=total_number_of_jobs, page_id=page_id,
                               jobs=current_job_list, total_pages=total_pages)
    else:
        return redirect(url_for('show_page', page_id=1))


@app.errorhandler(Exception)
def handle_exception(e):
    print(f"{e}")
    return redirect('/')


if __name__ == "__show_pages__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
