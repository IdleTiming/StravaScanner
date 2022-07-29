# -*- coding: utf-8 -*-

"""
Created on Wed Apr  6 19:35:30 2022

@author: Chris Idle

Data scraping tool for Strava 
"""

# Import libraries
import time
from selenium import webdriver
import warnings
import csv
import os
import os.path
import PySimpleGUI as sg

# disable deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

strava_url =  "https://www.strava.com/segments/" 

# Function to scrape data and write to CSV
def get_data():
    # get number of rows
    rows = len(driver.find_elements_by_xpath('//*[@id="results"]/table/tbody/tr'))
    # get data 
    for r in range(1, rows+1):
        #for p in cols_required:
        strava_name = driver.find_element_by_xpath('//*[@id="results"]/table/tbody/tr['+str(r)+']/td[2]').text
        strava_speed = driver.find_element_by_xpath('//*[@id="results"]/table/tbody/tr['+str(r)+']/td[4]').text
        speed = strava_speed[:-4]
        # write data to csv file
        with open('scraped.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow((str(strava_name), str(speed), str(i)))
        print(strava_name, ",", speed)

# Create GUI for inputs
sg.theme('DarkRed1')   # Add a touch of color
print = sg.Print #write all print commands to GUI output box
# All the stuff inside your window.
layout = [  [sg.Text('STRAVA SCRAPER')],
            [sg.Text('This tool requires a definition file.  Please see the segments.txt file in the program folder for an example')],
            [sg.Text('Strava premium membership is also required to access the leaderboard filters')],
            [sg.Text('Please enter the details required and select your definition file:')],
            [sg.Text('Strava Username: '), sg.InputText()],
            [sg.Text('Strava Password'), sg.InputText(password_char="*")],
            [sg.Text('Club Name: '), sg.InputText()],
            [sg.Text('Date Range: ')],
            [sg.Listbox(values=["All Time", "Today", "This Week", "This Month", "This year"], select_mode="extended", size=(30,5))],
            [sg.Text('Please select your definition file'), sg.Input(), sg.FilesBrowse('Select')],
            [sg.Button('SUBMIT'), sg.Button('QUIT')]
            ]

# Create the Window
window = sg.Window('STRAVA SCRAPER', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'QUIT': # if user closes window or clicks cancel
        window.close()
        break
    print (values[3])
    u_name = values[0]
    p_word = values[1]
    f_club = values[2]
    f_date = str(values[3])
    def_file = values[4]
    print (u_name, p_word, f_club, f_date, def_file)
    
    # check for existing csv and delete 
    if os.path.exists("scraped.csv"):
        os.remove("scraped.csv")
        
    # Grabs segment numbers from the test file segments.txt and assigns values to segment_ID list
    segment_ID = []
    with open(def_file) as segmentfile: #def_file is defined in the GUI code above
        for line in segmentfile:
            if int(line) > 0:
                segment_ID.append(int(line))

    # load webdriver and define site
    driver = webdriver.Chrome()
    # driver.minimize_window()
    driver.get('https://www.strava.com/')

    # Navigate Strava and apply login credentials
    login_page = '//*[@id="view"]/header/div/nav/a'
    u_name_input = '//*[@id="email"]'
    p_word_input = '//*[@id="password"]' 
    login_submit = '//*[@id="login-button"]'
    driver.find_element_by_xpath(login_page).click() 
    driver.find_element_by_xpath(u_name_input).send_keys(u_name)
    driver.find_element_by_xpath(p_word_input).send_keys(p_word)
    driver.find_element_by_xpath(login_submit).click()

    # Check login was succesful
    expectedURL = "https://www.strava.com/dashboard"
    actualURL = driver.current_url
    if actualURL == expectedURL:
        print('\n', "Login Successful!",'\n')
    else:
        driver.close()
        print('\n', "Login failed!  Please check your username and password and try again.",'\n')
        window.close()
        break
   
    # Display summary of process
    print("\n")
    print("DATA SCRAPER COMMENCING","\n")
    print("Segments included: " + str(segment_ID),"\n")
    print("Club: " + f_club,"\n")
    print("Dates: " + f_date,"\n")

    # Loop for each page and call get_data function
    for i in segment_ID:
        # Navigate to segment page
        segment_url = strava_url+str(i) 
        driver.get(segment_url)
        # get segment name
        segment_name = driver.find_element_by_class_name("name").text
        print ("  ")
        print ('-------')
        print (segment_url)
        print (segment_name)
        print ("  ")
        # apply filters
        filter_dropdown = '//*[@id="segment-results"]/div[2]/table/tbody/tr/td[3]/div/button'
        filter_date = '//*[@id="this-year"]/a' 
        driver.find_element_by_link_text(f_club).click() 
        time.sleep(3)
        driver.find_element_by_xpath(filter_dropdown).click()
        time.sleep(2)
        driver.find_element_by_xpath(filter_date).click()
        time.sleep(2)
        # call function to get data
        get_data()
        # check for NEXT pages else back to start of loop
        while driver.find_elements_by_xpath('//*[@id="results"]/nav/ul/li[4]/a'):
            driver.find_element_by_xpath('//*[@id="results"]/nav/ul/li[4]/a').click()
            time.sleep(3)
            get_data()
        else:
            print ()  
 
 

    # print summary of results
    print ('------------------------------------------------------------')
    print ('\n')
    print ('END OF SCRAPING')
    print('\n')
    # print('Total number of records extracted: ', i)
    print('\n')
    print ("APPLICATION IS CLOSING, SEE SCRAPED.CSV FILE IN THE INSTALLATION DIRECTORY")
    time.sleep(5)
    

# window.close()


