
# Imports
from flask import Flask, render_template,request,redirect
import csv
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
import numpy as np

app = Flask(__name__)

# Creating home page
@app.route("/home_page")
def home_page():
    # Looping through the csv with all the jobs adding them to a list and creating a stored variable to display on the html 
    jobs = []
    with open("display_jobs.csv","r") as f:
        reader = csv.reader(f)
        # reading the first row of the csv to get the headers and storing them for html
        headers = next(reader)
        for row in reader:
            jobs.append(row)
        no_listings = len(jobs) 

    return render_template("home.html",jobs=jobs,title="Data Analyst Jobs Dashboard",headers=headers,no_listings=no_listings)

@app.route("/current_job_vacancies_data")
def current_data():
    companys_top_10 = []
    with open("jobs_per_company.csv","r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            companys_top_10.append(row)
    
    jobs_per_date = []
    with open("jobs_per_date.csv","r") as f:
        reader = csv.reader(f)
        headers2 = next(reader)
        for row in reader:
            jobs_per_date.append(row)
    # Creating pandas dataframe in order to display the data using indexs of the dataframe to display the minimum salary data
    df = pd.read_csv("salary_data.csv")
    fig = plt.figure()
    plt.plot(df["Minimum Salary"])
    plt.ylabel("Minimum Salary")
    plt.xlabel("JobID")
    # Creating a variable to display this graph on the html
    min_salary = mpld3.fig_to_html(fig)

    fig2 = plt.figure()
    plt.plot(df["Maximum Salary"])
    plt.ylabel("Maximum Salary")
    plt.xlabel("JobID")

    max_salary = mpld3.fig_to_html(fig2)

    fig3 = plt.figure()
    plt.plot(df["Median Salary"])
    plt.ylabel("Median Salary")
    plt.xlabel("JobID")

    med_salary = mpld3.fig_to_html(fig3)

    
    
    return render_template("current_job_vacancies_data.html",title="Current Job Vacancies Data",companys_top_10=companys_top_10,headers=headers,jobs_per_date=jobs_per_date,headers2=headers2,plot=min_salary,plot2=max_salary,plot3=med_salary)

@app.route("/current_vs_past_job_vacancies")
def current_vs_past_job_vacancies():
    current_sal = pd.read_csv("salary_data.csv")
    past_sal = pd.read_csv("old_jobs_salaries.csv")

    min_past_pres = plt.figure()
    plt.plot(current_sal["Minimum Salary"])
    plt.plot(past_sal["Minimum Salary"])
    plt.ylabel("Minimum Salary")
    plt.xlabel("JobID")
    plt.legend(['Current Minimum Salaries', 'Past Minimum Salaries'], loc='upper left')
    c_v_p_min = mpld3.fig_to_html(min_past_pres)

    median_past_pres = plt.figure()
    plt.plot(current_sal["Median Salary"])
    plt.plot(past_sal["Median Salary"])
    plt.ylabel("Median Salary")
    plt.xlabel("Job ID")
    plt.legend(['Current Median Salaries', 'Past Median Salaries'], loc='upper left')
    c_v_p_med = mpld3.fig_to_html(median_past_pres)

    max_past_pres = plt.figure()
    plt.plot(current_sal["Maximum Salary"])
    plt.plot(past_sal["Maximum Salary"])
    plt.ylabel("Maximum Salary")
    plt.xlabel("Job ID")
    plt.legend(['Current Maximum Salaries', 'Past Maximum Salaries'], loc='upper left')
    c_v_p_max = mpld3.fig_to_html(max_past_pres)

    top_10_old_skills = []
    with open("top_10_old_skills.csv","r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            top_10_old_skills.append(row)

    top_10_new_skills = []
    with open("top_10_current_skills.csv","r") as f:
        reader = csv.reader(f)
        headers2 = next(reader)
        for row in reader:
            top_10_new_skills.append(row)

    current_experience_needed = []
    with open("new_experience_needed.csv","r") as f:
        reader = csv.reader(f)
        headers3 = next(reader)
        for row in reader:
            current_experience_needed.append(row)

    old_experience_needed = []
    with open("old_experience_needed.csv","r") as f:
        reader = csv.reader(f)
        headers4 = next(reader)
        for row in reader:
            old_experience_needed.append(row)  


    return render_template("current_vs_past_job_vacancies.html",title="Current vs Past Job Vacancies",c_v_p_min=c_v_p_min,c_v_p_med=c_v_p_med,c_v_p_max=c_v_p_max,top_10_old_skills=top_10_old_skills,headers=headers,headers2=headers2,top_10_new_skills=top_10_new_skills,current_experience_needed=current_experience_needed,headers3=headers3,old_experience_needed=old_experience_needed,headers4=headers4)

@app.route("/data_analyst_experience_data")
def data_analyst_experience_data():
    exp_data = pd.read_csv("experience_data.csv")

    plot_exp_data = plt.figure()
    plt.bar(exp_data["Experience Level"],exp_data["Amount"])
    plt.ylabel("Amount")
    plt.xlabel("Level of experience required")
    exp_plot = mpld3.fig_to_html(plot_exp_data)
    avg_exp_needed = []
    with open("avg_exp.csv","r") as f:
        reader = csv.reader(f)
        headers7 = next(reader)
        for row in reader:
            avg_exp_needed.append(row)

    return render_template("data_analyst_experience_data.html",title="Data Analyst Experience Data",exp_plot=exp_plot,headers7=headers7,avg_exp_needed=avg_exp_needed)

@app.route("/data_analyst_skills_data")
def data_analyst_skills_data():
    top_20_skills = []
    with open("top_20_paying_skills.csv","r") as f:
        reader = csv.reader(f)
        headers5 = next(reader)
        for row in reader:
            top_20_skills.append(row)

    company_skills = []
    with open("company_skills.csv","r") as f:
        reader = csv.reader(f)
        headers6 = next(reader)
        for row in reader:
            company_skills.append(row)
    return render_template("data_analyst_skills_data.html",title="Data Analyst Skills Data",top_20_skills=top_20_skills,headers5=headers5,company_skills=company_skills,headers6=headers6)

if __name__  == "__main__":
    app.run(debug=True,port=5000)