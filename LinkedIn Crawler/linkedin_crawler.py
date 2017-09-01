"""
Created July 6th, 2017
Program: Logs in to LinkedIn, enters a query in the LinkedIn search bar, and scrapes relevant information on queried people.
@author: Charles Zhang
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options

#Sources
inputDirectory = 'Input//'
outputDirectory = 'Output//'
input_data = inputDirectory + 'canvas.csv'

#Transforms csv files to data frames
canvas = pd.read_csv(input_data, encoding="ISO-8859-1",low_memory = False)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chromedriver = webdriver.Chrome(executable_path='') #PATH of Chromedriver

#Logs into LinkedIn using email and password
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

#Enters specified query into LinkedIn search bar with various filters
def createquery(query,company,region,position, industry):
    search_bar = chromedriver.find_element_by_class_name('ember-text-field')
    search_bar.send_keys(query)
    search_button = chromedriver.find_element_by_class_name('nav-search-button')
    search_button.click()
    time.sleep(7)
    time.sleep(3)

    buttons1 = chromedriver.find_elements_by_tag_name('button')
    for a in buttons1:
        try:
            if "Industries" in a.text:
                a.click()
                time.sleep(5)
                industry_buttons = chromedriver.find_elements_by_tag_name('label')
                for e in industry_buttons:
                    try:
                        if (industry in e.get_attribute('title')) or ("Software" in e.get_attribute('title')):
                            e.click()
                    except:
                        pass
                a.click()
        except (StaleElementReferenceException):
            pass
    time.sleep(5)

    buttons2 = chromedriver.find_elements_by_tag_name('button')
    for b in buttons2:
        try:
            if "Locations" in b.text:
                b.click()
                time.sleep(1)
                add_location = chromedriver.find_element_by_xpath('//*[@id="sf-facetGeoRegion-add"]')
                time.sleep(1)
                add_location.send_keys(region)
                labels = chromedriver.find_elements_by_tag_name('label')
                count_city = 0
                for d in labels:

                    #Make sure to change location during query
                    if region in d.get_attribute('title') and count_city == 0:
                        d.click()
                        count_city += 1
                time.sleep(7)
                #b.click()
        except (StaleElementReferenceException):
            pass
    search_bars = chromedriver.find_elements_by_tag_name('input')
    try:
        for tag in search_bars:
            if ("Search" in tag.get_attribute('placeholder')):
                tag.clear()
    except:
        pass

    time.sleep(3)
    q_search_button = chromedriver.find_element_by_css_selector('button.submit-button.button-primary-large')
    q_search_button.click()
    time.sleep(3)

    buttons1 = chromedriver.find_elements_by_tag_name('button')
    for a in buttons1:
        try:
            if "Keywords" in a.text:
                a.click()
                time.sleep(1)
                title = chromedriver.find_element_by_xpath('//*[@id="advanced-search-title"]')
                title.send_keys(position)
                company_search = chromedriver.find_element_by_xpath('//*[@id="advanced-search-company"]')
                company_search.send_keys(company)
                a.click()
        except (StaleElementReferenceException):
            pass
    time.sleep(1)

    q_search_button2 = chromedriver.find_element_by_css_selector('button.submit-button.button-primary-large')
    q_search_button2.click()

    time.sleep(5)
    connections_buttons = chromedriver.find_elements_by_tag_name('label')
    for c in connections_buttons:
        try:
            if ("1st" in c.get_attribute('title') or "2nd" in c.get_attribute('title') or "3rd+" in c.get_attribute('title')):
                c.click()
        except:
            pass
#/Users/charleszhang/Google Drive/LinkedIn Crawler
def collectinfo():
    total_pages = 20
    page = 1
    people = 0
    while (page < total_pages):
        chromedriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        buttons = chromedriver.find_elements_by_css_selector('div.search-result__wrapper')
        for b in buttons:
            try:
                text = b.text
                positionandcompany = findpositionandcompany(text)
                linkedin_url = ""
                all_children = b.find_elements_by_css_selector("*")
                for z in all_children:
                    try:
                        if ('search-result__result-link ember-view' in z.get_attribute('class')):
                            linkedin_url = z.get_attribute('href')
                        if ('p.subline-level-1.Sans-15px-black-85%.search-result__truncate' in z.get_attribute('class')):
                    except:
                        pass
                canvas.loc[people,'name'] = positionandcompany.get('name').encode('utf-8')
                canvas.loc[people,'position'] = positionandcompany.get('position').encode('utf-8')
                canvas.loc[people,'company'] = positionandcompany.get('company').encode('utf-8')
                canvas.loc[people,'description'] = positionandcompany.get('description').encode('utf-8')
                canvas.loc[people,'linkedin_url'] = linkedin_url[2:-1].encode('utf-8')
                people += 1
            except (StaleElementReferenceException):
                pass
        page += 1
        pages = chromedriver.find_elements_by_tag_name('button')
        for x in pages:
            try:
                if str(page) in x.text:
                    x.click()
            except:
                pass
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def findpositionandcompany(text):
    position = ""
    company = ""
    description = ""
    name = ""
    number_line = 0
    description_line = 0
    count = 1
    for line in text.splitlines():
        if "Current: " in line:
            position = find_between(line,"Current: ", " at")
            company = line[line.find("at ") + len("at "):]
        if line == "1st" or line == "2nd" or line == "3rd":
            number_line = count
            description_line = count + 1
        if count == description_line:
            description = line
        if count == 1:
            name = line
        count += 1
    return {'name':name,'position':position,'company':company,'description':description}

USERNAME = ""
PASSWORD = ""
login_linkedin(USERNAME,PASSWORD,chromedriver) #logs into LinkedIn

createquery("columbus technology","","columbus","cto", "information technology") #Enters specified query
collectinfo() #Collects user information and puts information into a pandas dataframe
canvas.to_csv(outputDirectory + '') #Outputs dataframe into a csv file
