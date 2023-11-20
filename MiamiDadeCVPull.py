# This File was written in 4/2023 By Carick Brandt

# Import the needed modules
import os
import re
import sys
import time
import datetime
import SetDates
import json
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import threading

# Set the Download Directory to the current directory  + \Downloads
DownloadDirectory = os.getcwd() + "/Downloads"


# Initialize the Chrome Driver
def InitDriver():
    # Create a Chrome Options object to set the download directory
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DownloadDirectory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # Create a Chrome Driver object
    driver = uc.Chrome(options=chrome_options)
    return driver


# This function will handle checking if an element is present on the page, and if there is not then it will attempt to reload the page up to 3 times
def CheckElement(driver, ElementID):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, ElementID)))
    except:
        for i in range(3):
            driver.refresh()
            time.sleep(15)
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, ElementID)))
                break
            except:
                if i == 3:
                    print("Page did not load correctly")
                    return False
    return True


# This Function will write in whatever string a character at a time into a given input box
def WriteSlowly(driver, InputBoxID, InputString):
    InputBox = driver.find_element(By.ID, InputBoxID)
    InputBox.send_keys(Keys.CONTROL + "a")
    InputBox.send_keys(Keys.BACKSPACE)
    InputBox.send_keys(Keys.HOME)
    for i in range(len(InputString)):
        InputBox.send_keys(InputString[i])
        time.sleep(0.24)
    InputBox.send_keys(Keys.TAB)
    return 0


# This Function wil go to the website https://www8.miamidade.gov/Apps/RER/RegulationSupportWebViewer/Home/Reports
# the case type is supposed to be set to "All Case Types" and we just need a start Date to complete a search
# Downloads the Excel file and returns the path to the file
def Search(driver, StartDate, EndDate):
    Violations = ["Unsafe Structures", "All Other Code Violations"]
    dfList = []
    for Violation in Violations:
        driver.get("https://www8.miamidade.gov/Apps/RER/RegulationSupportWebViewer/Home/Reports")
        time.sleep(5)
        if CheckElement(driver, "txtCaseType") is False:
            return False
        CaseTypeDropDown = driver.find_element(By.ID, "txtCaseType")
        CaseTypeDropDown.click()
        time.sleep(.5)
        WriteSlowly(driver, "txtCaseType", str(Violation))
        CaseTypeRadio = driver.find_element(By.ID, "radios-1")
        CaseTypeRadio.click()
        StartDateInput = driver.find_element(By.ID, "startDate")
        StartDateInput.click()
        time.sleep(.4)
        StartDateInput.send_keys(Keys.CONTROL + "a")
        StartDateInput.send_keys(Keys.BACKSPACE)
        StartDateInput.send_keys(StartDate.split("/")[2])
        time.sleep(.4)
        StartDateInput.send_keys(Keys.TAB)
        StartDateInput.send_keys(StartDate.split("/")[0])
        time.sleep(.4)
        StartDateInput.send_keys(StartDate.split("/")[1])
        EndDateInput = driver.find_element(By.ID, "endDate")
        EndDateInput.click()
        time.sleep(.4)
        EndDateInput.send_keys(Keys.CONTROL + "a")
        EndDateInput.send_keys(Keys.BACKSPACE)
        EndDateInput.send_keys(EndDate.split("/")[2])
        time.sleep(.4)
        EndDateInput.send_keys(Keys.TAB)
        EndDateInput.send_keys(EndDate.split("/")[0])
        time.sleep(.4)
        EndDateInput.send_keys(EndDate.split("/")[1])
        SubmitButton = driver.find_element(By.CLASS_NAME, "btn.btn-primary")
        SubmitButton.click()
        time.sleep(5)
        tempdf = pd.read_html(driver.page_source)[0]
        tempdf = tempdf[tempdf["FOLIO NUMBER"] != "---"]
        tempdf = tempdf[tempdf["FOLIO NUMBER"] != "EXEMPT FROM PUBLIC RECORDS, Florida Statues 119.071"]
        dfList.append(tempdf)
    df = pd.concat(dfList, ignore_index=True)
    df["DATE OPENED"] = pd.to_datetime(df["DATE OPENED"])
    df = df[df["DATE OPENED"] >= pd.to_datetime(StartDate) - pd.DateOffset(years=2)]
    df = df.drop(columns=["COUNT", "LAST INSPECTION ACTIVITY", "ACTIVITY DATE",
                                      "DISTRICT NUMBER", "INSPECTOR", "OWNER NAME and ADDRESS",
                                      "VIOLATION", "PERMIT NUMBER"])
    df.reset_index(drop=True, inplace=True)
    driver.close()
    return df


# This Function will take in the driver, and dataframe.
# It will navigate to the website: https://www.miamidade.gov/Apps/PA/propertysearch/#/ Where using the folio number it
# will pull the property information and return a dataframe with the new information
def GetPropertyInfo(driver, df: pd.DataFrame):
    # Add a Property Address, Property City, Property Zip, Mailing Address, Mailing City, Mailing Zip, Zoning, Land Use, Beds, Bath, SqFt
    df["Name"] = ""
    df["Property Address"] = ""
    df["Property City"] = ""
    df["Property State"] = "FL"
    df["Property Zip"] = ""
    df["Mailing Address"] = ""
    df["Mailing City"] = ""
    df["Mailing State"] = ""
    df["Mailing Zip"] = ""
    df["Zoning"] = ""
    df["Land Use"] = ""
    df["Beds"] = ""
    df["Bath"] = ""
    df["SqFt"] = ""
    df["Year Built"] = ""
    for index, row in df.iterrows():
        print('*'*50)
        print("\033")
        print(json.dumps(list(row)))
        print("Row: " + str(index) + " of " + str(len(df.index)) + " Folio: " + str(row["FOLIO NUMBER"]))
        driver.get("https://www.miamidade.gov/Apps/PA/propertysearch/#/")
        if driver.get_window_size()["width"] != 1920:
            driver.set_window_size(1920, 1080)
        time.sleep(3)
        if CheckElement(driver, "t-folio") is False:
            return False
        FolioButton = driver.find_element(By.ID, "t-folio")
        FolioButton.click()
        time.sleep(1)
        SearchBox = driver.find_element(By.CSS_SELECTOR, "#folio #search_box")
        SearchBox.click()
        SearchBox.send_keys(Keys.CONTROL + "a")
        SearchBox.send_keys(Keys.BACKSPACE)
        SearchBox.send_keys(row["FOLIO NUMBER"])
        SearchBox.send_keys(Keys.ENTER)
        time.sleep(.5)
        try:
            driver.find_element(By.CLASS_NAME, "close").click()
            df.at[index, "Property Address"] = "Not Found"
        except:
            try:
                if driver.find_element(By.LINK_TEXT, "Comparable Sales"):
                    driver.find_element(By.CLASS_NAME, "layers-list").click()
                    time.sleep(.25)
                    driver.find_element(By.CSS_SELECTOR, ".ng-scope:nth-child(4) > .ng-pristine").click()
                    time.sleep(.25)
                    driver.find_element(By.CSS_SELECTOR, ".ng-scope:nth-child(5) > .ng-pristine").click()
                    time.sleep(1.8)
                    City = driver.find_element(By.ID, "layer-muni").text.split("MUNICIPALITY: ")[1]
                    Zip = driver.find_element(By.ID, "layer-zip").text.split("ZIP: ")[1]
                    df2 = pd.read_html(driver.page_source)[0]
                    Name = df2.iloc[3, 1].split("Owner  ")[1]
                    Property = df2.iloc[2, 1].split("Address  ")[1]  # row 2 is Property Address:
                    DupeTest = Property.split(" ")[0]
                    for substring in Property.split(" ")[1:]:
                        if substring == DupeTest:
                            Property = DupeTest + Property.split(substring)[1]
                            break
                    StreetTypes = ["ALY", "AVE", "BND", "BLVD", "CSWY", "CIR", "CT", "CV", "DRIVE", "EXT", "HWY",
                                   "HOLW", "ISLE", "LN",
                                   "LNDG", "MNR", "MILE", "PASS", "PATH", "PL", "PT", "ROAD", "ROW", "SQ", "ST", "TER",
                                   "TWP", "TRCE",
                                   "TRL", "VIEW", "WALK", "WAY", "RD", "PARK", "COURT", "DR"]
                    MailingAddress = df2.iloc[4, 1].split("Address  ")[1]
                    if MailingAddress.split("  ")[-1] == "USA":
                        MailingZip = MailingAddress.split("  ")[-2]
                        MailingState = MailingAddress.split("  ")[-3]
                        for streetType in StreetTypes:
                            if streetType in MailingAddress:
                                if MailingAddress.split(streetType)[1].split(",")[0][1].isdigit():
                                    streetType = streetType + " " + MailingAddress.split(streetType)[1].split(" ")[1]
                                MailingCity = MailingAddress.split(streetType)[1].split(",")[0]
                                break
                            else:
                                MailingCity = MailingAddress.split(",")[0].split(" ")[-2]
                        MailingAddress = MailingAddress.split(MailingCity)[0]
                    else:
                        MailingZip = MailingAddress.split("  ")[-1]
                        MailingState = MailingAddress.split("  ")[-2]
                        for streetType in StreetTypes:
                            if streetType in MailingAddress:
                                if MailingAddress.split(streetType)[1].split(",")[0][1].isdigit():
                                    streetType = streetType + " " + MailingAddress.split(streetType)[1].split(" ")[1]
                                MailingCity = MailingAddress.split(streetType)[1].split(",")[0]
                                break
                            else:
                                MailingCity = MailingAddress.split(",")[0].split(" ")[-2]
                        MailingAddress = MailingAddress.split(MailingCity)[0]
                    df.loc[index, "Name"] = Name
                    df.loc[index, "Property Address"] = Property
                    df.loc[index, "Property City"] = City
                    df.loc[index, "Property Zip"] = Zip
                    df.loc[index, "Mailing Address"] = MailingAddress
                    df.loc[index, "Mailing City"] = MailingCity
                    df.loc[index, "Mailing State"] = MailingState
                    df.loc[index, "Mailing Zip"] = MailingZip
                    df.loc[index, "Zoning"] = df2.iloc[5, 1].split("Zone")[1]
                    df.loc[index, "Land Use"] = df2.iloc[6, 1].split("Use")[1]
                    df.loc[index, "Beds"] = df2.iloc[7, 1].split("/")[0]
                    df.loc[index, "Bath"] = df2.iloc[7, 1].split("/")[1].split("/")[0]
                    df.loc[index, "SqFt"] = df2.iloc[11, 1].split("Sq.Ft")[0]
                    df.loc[index, "Year Built"] = df2.iloc[14, 1]
                    print(df.loc[index])
            except:
                print("Multiple Results for Search")
                df.loc[index, "Name"] = np.nan
                df.loc[index, "Property Address"] = "Not Found"
                df.loc[index, "Property City"] = np.nan
                df.loc[index, "Property Zip"] = np.nan
                df.loc[index, "Mailing Address"] = np.nan
                df.loc[index, "Mailing City"] = np.nan
                df.loc[index, "Mailing State"] = np.nan
                df.loc[index, "Mailing Zip"] = np.nan
                df.loc[index, "Zoning"] = np.nan
                df.loc[index, "Land Use"] = np.nan
                df.loc[index, "Beds"] = np.nan
                df.loc[index, "Bath"] = np.nan
                df.loc[index, "SqFt"] = np.nan
                df.loc[index, "Year Built"] = np.nan
    df = df[df["Property Address"] != "Not Found"]
    for index, row in df.iterrows():
        if "UNINCORPORATED" in row["Mailing City"]:
            df.loc[index, "Mailing City"] = "Miami-Dade"
        if "UNINCORPORATED" in row["Property City"]:
            df.loc[index, "Property City"] = "Miami-Dade"
    driver.close()
    return df
