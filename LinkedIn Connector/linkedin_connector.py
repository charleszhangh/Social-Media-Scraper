"""
Created June 20th, 2017
Program: Logs in to LinkedIn and connects with people based on a CSV list of LinkedIn URLs
@author: Charles Zhang
"""

from selenium import webdriver
import pandas as pd
import os
import time
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException

# Sources
inputDirectory = 'Input//'
input_data = inputDirectory + '' #FILE NAME WITH LINKEDIN URLS
# Transforms csv files to data frames
people_to_connect = pd.read_csv(input_data, encoding="ISO-8859-1",low_memory = False)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chromedriver = webdriver.Chrome(executable_path='') #PATH of Chromedriver

#Logs in to LinkedIn using account information
def login_linkedin(myemail,mypassword,chromedriver):
    url = 'https://www.linkedin.com/uas/login?goback=&trk=hb_signin'
    chromedriver.get(url)
    email = chromedriver.find_element_by_xpath('//*[@id="session_key-login"]')
    email.send_keys(myemail)
    password = chromedriver.find_element_by_xpath('//*[@id="session_password-login"]')
    password.send_keys(mypassword)
    sign_in = chromedriver.find_element_by_xpath('//*[@id="btn-primary"]')
    sign_in.click()
    time.sleep(2)

#Connects with user using a LinkedIn URL
def requestuser(linkedin_url):
    try:
        chromedriver.get(linkedin_url)
        distance = chromedriver.find_element_by_class_name('dist-value')
        dist_value = distance.text
        if (dist_value != "1st"):
            try:
                connects = chromedriver.find_elements_by_class_name('default-text')
                connected = 0
                for c in connects:
                    try:
                        if c.text == "Connect":
                            c.click()
                            send_now = chromedriver.find_element_by_css_selector('button.button-primary-large.ml3')
                            send_now.click()
                            connected += 1
                    except(StaleElementReferenceException):
                        pass
                if connected == 0:
                    buttons5 = chromedriver.find_elements_by_tag_name('button')
                    # more_button.click()
                    for b2 in buttons5:
                        if b2.text == "More Actions":
                            b2.click()
                    connects5 = chromedriver.find_elements_by_class_name('default-text')
                    for c2 in connects5:
                        try:
                            if c2.text == "Connect":
                                c2.click()
                                send_now = chromedriver.find_element_by_css_selector('button.button-primary-large.ml3')
                                send_now.click()
                        except(StaleElementReferenceException):
                            pass
            except (NoSuchElementException) as e:
                pass
                print("skip")
    except(NoSuchElementException) as e:
        pass
        print("no account")

USERNAME = ""
PASSWORD = ""

login_linkedin(USERNAME,PASSWORD,chromedriver)
count = 0
for x in people_to_connect.linkedin_url:
    try:
        requestuser(x)
    except:
        pass
    time.sleep(10)
    count += 1
    print(count)
