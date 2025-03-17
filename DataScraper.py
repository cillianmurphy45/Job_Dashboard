
# handler class for pipeline
class DataScraper:
    def __init__(self, next: 'DataScraper' = None):  
        ''' initialise the next handler reference'''
        self.next = next
        
    def process(self, data):
        ''' call process_task on the concrete class
        then calls the next handler'''
        self.process_task(data)
        if self.next is not None:
            self.next.process(data)
    
    def process_task(self, data):
        ''' abstract method'''
        pass
    
    def add_datascraper(self, datacleaner):
        '''Adds a new handler to the end of the chain '''
        if self.next != None:
            self.next.add_datascraper(datacleaner)
        else:
            self.next = datacleaner



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import csv
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from itertools import zip_longest
import pandas as pd
import mysql.connector


def get_job_info(data):
    # setting up driver
    driver = webdriver.Chrome(service=ChromeService(r"C:\Users\Cillian\chromedriver.exe"))

    # setting up waits
    wait = WebDriverWait(driver,10)
    # Data storing variables
    job_title = []
    company_name = []
    location = []
    date = []
    salary_exp = []
    skills = []

    # Getting url
    driver.get(data)

    wait = WebDriverWait(driver,20)

    # Finding job search button
    job_search = driver.find_element(By.ID,"heroSectionDesktop-skillsAutoComplete--input")
    # Entering job title
    job_search.send_keys("data analyst")
    # Search
    job_search.send_keys(Keys.RETURN)

    try:
        # While loop for continous loop until all data is found
        while True:
            # Waiting until the job titles are on th page then looping through them and adding to the job title list
            job = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"jobTitle")))
            for titles in job:
                job_title.append(titles.text)
            

            company_title = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"companyName")))
            for company in company_title:
                company_name.append(company.text)
            

            company_location = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,".details.location")))
            for loc in company_location:
                location.append(loc.text)
            

            dates = driver.find_elements(By.CLASS_NAME,"jobAddedTime")
            for da in dates:
                date.append(da.text)

            job_sal_exp = driver.find_elements(By.CLASS_NAME,"experienceSalary")
            for sal in job_sal_exp:
                salary_exp.append(sal.text)
                
            # Looping through all of the clickable boxes and finding the data
            for j in job:
                j.click()

                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"pillsContainer")))

                skill = driver.find_elements(By.CLASS_NAME,"pillsContainer")

                for sk in skill:
                    skills.append(sk.text)
                
                
                # Showing selenium where to click after above data is found
                job = driver.find_elements(By.CLASS_NAME,"jobTitle")
            

            try:
                # Finding next page
                next_page = driver.find_element(By.CSS_SELECTOR,".arrow.arrow-right")
                # Once it reaches the final page the arrow right button is disabled so once that is in the class atribute break the loop
                if "disabled" in next_page.get_attribute("class"):
                    break
                # Clicking next page if avaialble
                next_page.click()
                # Refresging the page each time so no stale elements
                driver.refresh()
            
            except Exception as e:
                print(f"error:{e}")
            
    

            
    finally:
        driver.quit()
    # Looping through all of the data obtained and writing to a csv file 
    with open('test.csv', 'w', newline='',encoding="utf-8") as csv_file:
                headers = ["job_title","company_name","location","salary","skills","date_posted"]
                writer = csv.DictWriter(csv_file,fieldnames=headers)
                writer.writeheader()
                # using zip_longest so it fills any null values if the other data is longer than another
                for jo,co_name,lo,posted,salar,skil in zip_longest(job_title,company_name,location,date,salary_exp,skills,fillvalue="N/A"):
                    writer.writerow({"job_title":jo,"company_name":co_name,"location":lo,"salary":salar,"skills":skil,"date_posted":posted})
get_job_info("https://www.foundit.sg/")

class CleanData(DataScraper):
    def process_task(self, data):

            data["salary"] = data["salary"].str.replace("s\n"," ")

            # Salary and experience were joined by the circle so had to replace this with a comma
            data["salary"] = data["salary"].str.replace("•",", ")

            # Creating the experience column by taking where it had the experience in the salary column and assigning that to experience
            data["experience"] = data["salary"].str.extract(r'((?:\d+\s*-\s*\d+\s*Years)|(?:Fresher))')

            # Finding where it had the salary per month part and assigning that to salary column
            data['salary'] = data['salary'].str.extract(r'((?:USD|SGD)\s[\d,]+\s*-\s*[\d,]+\s*per\s*month)')

            # Assigning each experience level to a key value then looping through the experience column to assign the value to each type of experience category
            exp_data = {"Fresher":1,"3 - 5 Years":4,"5 - 7 Years":6,"2 - 4 Years":3,"1 - 3 Years":2,"2 - 5 Years":3,"5 - 8 Years":6,"4 - 6 Years":5,"3 - 8 Years":6,"10 - 12 Years":11,"8 - 10 Years":9,"1 - 5 Years":3,"5 - 10 Years":7,"0 - 2 Years":1}
            for exp in exp_data:
                data.loc[data["experience"].str.contains(exp,na = False), "experience"] = exp_data[exp]

            # Extracting what currency the job is listed in and assigning it to a new column currency
            data["currency"] = data["salary"].str.extract(r'((?:USD|SGD))')

            # Getting rid of any white space in the salary column
            data["salary"] = data["salary"].str.strip()

            # Gettiong rid of the hyphon between the salaries
            data["salary"] = data["salary"].str.replace("-"," ")

            # Getting rid of the USD/SGD currency in the salary column as we have a new column with that info
            data['salary'] = data['salary'].str.replace(r'(SGD|USD|\s*per month)', '', regex=True)

            # Splitting the salary column to max and min salaries to compute the median
            data[["min_salary","max_salary"]] = data["salary"].str.split(expand=True)

            # Getting rid of commas so that I can convert the salaries to floats
            data['min_salary'] = data['min_salary'].str.replace(',', '').astype(float)
            data['max_salary'] = data['max_salary'].str.replace(',', '').astype(float)

            # Computing the median salary then writing that to a new column called median salary
            data['median_salary'] = data[['min_salary', 'max_salary']].median(axis=1)

            # Drop salary column as have all info neccesary within min, max and median salary
            data.drop(columns=["salary"],inplace = True)

            # Finding rows where job title was null as the webscraper didnt obtain that data and dropping these rows
            indexdata = data[(data['job_title'].isna() ==  True)].index
            data.drop(indexdata,inplace=True)


            data.to_csv("new_jobs_28_2_25.csv")

            super().process(data)  
            


class CleanSkills(DataScraper):
    def process_task(self, data):

            skills = pd.DataFrame(data["skills"])

            # Getting rid of the /n in between each skill
            skills["skills"] = skills["skills"].str.replace("\n",", ")

            # Creating a job_id column to relate it to the job
            skills = skills.rename(columns={"Unnamed: 0":"job_id"})

            # Splitting the skills every time there is a comma while still being assigned to the job_id
            skills = skills.assign(skills=skills['skills'].str.split(',')).explode('skills')
            skills['skills'] = skills['skills'].str.strip()

            data.drop(columns=["skills"],inplace=True)

            skills.to_csv("new_skills_28_2_25.csv")
            
            super().process(data)

class SkillsDatabase(DataScraper):
    def process_task(self, data):
            # Creating connection to the database
            mydb = mysql.connector.connect(user='root', password='', host='localhost')

            # Creating cursor to interact with my database
            cur = mydb.cursor()

            # Connecting to my database
            cur.execute("USE Jobs_Data")

            # Creating pandas dataframe for csv files
            skills_db = pd.read_csv("new_skills_28_2_25.csv")

            cur.execute("""
            CREATE TABLE IF NOT EXISTS skills_28_2_25 (
                job_id INT,
                skill_name VARCHAR(255),
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            )
            """)

            for i, row in skills_db.iterrows():
                sql = "INSERT INTO skills (job_id, skill_name) VALUES (%s, %s)"
                cur.execute(sql, (row['job_id'], row['skills']))
                mydb.commit()
            
            mydb.close()

class JobsDatabase(DataScraper):
     def process_task(self, data):
            # Creating connection to the database
            mydb = mysql.connector.connect(user='root', password='', host='localhost')

            # Creating cursor to interact with my database
            cur = mydb.cursor()

            # Creating the Database to connect to
            cur.execute("CREATE DATABASE IF NOT EXISTS Jobs_Data")
            
            # Connecting to my database
            cur.execute("USE Jobs_Data")

            data.reset_index(drop=True, inplace=True)  # Ensure clean index

            cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs_28_2_25 (
                job_id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255),
                location VARCHAR(255),
                salary FLOAT,
                company_name VARCHAR(255),
                date_posted VARCHAR(255),
                experience FLOAT
            )
            """)

            # Writing the csv files to my database by itering through the rows and inserting them nto the correct column by saving them to row

            for i, row in data.iterrows():
                sql = "INSERT INTO jobs (title, company, location, salary, experience, date_posted) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (row['title'], row['company'], row['location'], row['salary'] if pd.notna(row['salary']) else None, row['experience'] if pd.notna(row['experience']) else None, row['date_posted']))
                mydb.commit()

            mydb.close()    

x = ("current_jobs.csv")
chain = CleanSkills(CleanData(JobsDatabase(SkillsDatabase)))
chain.process(x)