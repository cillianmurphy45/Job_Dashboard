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
get_job_info("#")