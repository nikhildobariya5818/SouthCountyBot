# This file was written by Carick Brandt on 4/2023
# This module will be used to scrape the https://officialrecords.broward.org/AcclaimWeb/search/SearchTypeDocType
# website for the relevant DocType and returns a list of FirstNames, and LastNames from the First Indirect Name column
# from the search results.

# Import the necessary modules
import os
import re
import sys
import time
import datetime
import numpy as np
import pandas as pd
import SetDates
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from FolioConverter import FolioForBroward
# dictionary of the DocTypes we want to search for
DocTypes = {
    "LP": "Lis Pendens (LP)",
    "DC": "Death Certificate (DC)",
    "PRO": "Probate (PRO)",
    "PALIE": "Property Tax Lien (PALIE)",
    "EV": "Evictions"
}

# This function will Initialize the Chrome Driver and return it
def InitDriver():
    # Create an Undetectable Chrome Driver
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    driver = uc.Chrome(options=options)
    driver.get("https://google.com")
    time.sleep(2)
    driver.get("https://officialrecords.broward.org/AcclaimWeb/search/SearchTypeDocType")
    time.sleep(5)
    driver.find_element(By.ID, "btnButton").click()
    time.sleep(5)
    return driver

# This function will Search for the Evictions
def EvictionsSearch(driver, StartDate=None, EndDate=None):
    # Load the right website
    driver.get("https://www.browardclerk.org//Web2/Account/LogIn")
    time.sleep(5)
    driver.find_element(By.ID, "Username").send_keys("livelifeproperties")
    driver.find_element(By.ID, "Password").send_keys("Livelife1!")
    driver.find_element(By.ID, "terms").click()
    driver.find_element(By.ID, "Password").send_keys(Keys.ENTER)
    time.sleep(3)
    driver.get("https://www.browardclerk.org//Web2/CaseSearchECA/Index/?AccessLevel=SUBSCRIBER")
    time.sleep(3)
    driver.find_element(By.LINK_TEXT, "Civil Cases Filed").click()
    time.sleep(2)
    driver.find_element(By.ID, "filingDateOnOrAfter").send_keys(StartDate)
    driver.find_element(By.ID, "filingDateOnOrAfter").send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element(By.ID, "ddl").click()
    driver.find_element(By.ID, "ddl").send_keys("Case Type")
    driver.find_element(By.ID, "FilterText").send_keys("Removal of Tenant")
    driver.find_element(By.ID, "FilterText").send_keys(Keys.ENTER)
    time.sleep(3)
    NumRows = driver.find_element(By.CSS_SELECTOR, ".k-pager-info").text.split("of ")[1].split(" items")[0]
    NumPages = int(np.ceil(int(NumRows)/10))
    df = pd.DataFrame(columns=["Case Number", "Name", "Case Type", "Filing Date"])
    for i in range(NumPages):
        table = driver.find_element(By.ID, "SearchResultsGrid")
        table_rows = table.find_elements(By.TAG_NAME, "tr")
        for row in table_rows[1:]:
            row_data = [data.text for data in row.find_elements(By.TAG_NAME, "td")[:4]]
            row_data[1] = row_data[1].split("vs. ")[1].split(" Defendant")[0]
            if ", " in row_data[1]:
                row_data[1] = row_data[1].split(", ")[0]
            row_data[2] = row_data[2].split("Removal of Tenant")[1]
            current_row = pd.DataFrame([row_data], columns=["Case Number", "Name", "Case Type", "Filing Date"])
            df = pd.concat([df, current_row], axis=0, ignore_index=True)
        driver.find_element(By.LINK_TEXT, "Go to the next page").click()
        pd.set_option('display.max_columns', None)

    df.rename(columns={"Name": "FirstName"}, inplace=True)
    df.insert(2, "MiddleName", "")
    df.insert(3, "LastName", "")
    for index, row in df.iterrows():
        if "LLC" in row["FirstName"]:
            df.drop(index, inplace=True)
        if "Corp" in row["FirstName"]:
            df.drop(index, inplace=True)
        if row["FirstName"].count(" ") > 1:
            df.loc[index, "FirstName"] = row["FirstName"].split(" ")[0]
            df.loc[index, "MiddleName"] = " ".join(row["FirstName"].split(" ")[1:-1])
            df.loc[index, "LastName"] = row["FirstName"].split(" ")[-1]
        else:
            df.loc[index, "FirstName"] = row["FirstName"].split(" ")[0]
            df.loc[index, "LastName"] = row["FirstName"].split(" ")[-1]
    print(df)
    return df


def Search(driver, DocType, StartDate=None, EndDate=None):
    dropdown = driver.find_element(By.ID, "DocTypesDisplay-input")
    time.sleep(2)
    dropdown.send_keys(Keys.CONTROL + "a")
    time.sleep(1)
    dropdown.send_keys(Keys.DELETE)
    time.sleep(1)
    for char in DocType:
        dropdown.send_keys(char)
        time.sleep(1)
    time.sleep(4)
    if StartDate is None or EndDate is None:
        StartDate, EndDate = SetDates.NoDates()
    EndDateField = driver.find_element(By.ID, "RecordDateTo")
    time.sleep(2)
    EndDateField.click()
    time.sleep(2)
    EndDateField.send_keys(Keys.CONTROL + "a")
    time.sleep(2)
    EndDateField.send_keys(Keys.DELETE)
    time.sleep(2)
    for char in EndDate:
        EndDateField.send_keys(char)
        time.sleep(1)
    time.sleep(4)
    StartDateField = driver.find_element(By.ID, "RecordDateFrom")
    time.sleep(2)
    StartDateField.click()
    time.sleep(2)
    StartDateField.send_keys(Keys.CONTROL + "a")
    time.sleep(2)
    StartDateField.send_keys(Keys.DELETE)
    time.sleep(2)
    for char in StartDate:
        StartDateField.send_keys(char)
        time.sleep(1)
    time.sleep(2)
    StartDateField.send_keys(Keys.ENTER)
    time.sleep(2)

    return 0

# This Function will Scrape the Search Results and return a dataframe
def Scrape(driver, DocType):
    try:
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "SearchGridContainer")))
    except:
        print("No Results Found")
        return None
    time.sleep(10)
    NumRows = driver.find_element(By.CLASS_NAME, "t-status-text").text.split(" ")[-1]
    print("Number of Rows: " + NumRows)
    NumPages = int(np.ceil(int(NumRows) / 100))
    print("Number of Pages: " + str(NumPages))
    CaseNumber = []
    FirstIndirectName = []
    iframes = []
    for i in range(max(1, NumPages-1)):
        time.sleep(2)
        print("Page: " + str(i+1))
        table = driver.find_element(By.ID, "SearchGridContainer")
        rows = table.find_elements(By.TAG_NAME, "tr")
        FirstIndirectNameIndex: int
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if row.text.__contains__("Cart\nConsideration\nFirst Direct Name\nFirst Indirect Name"):
                FirstIndirectNameIndex = row.text.count("\n", 0, row.text.index("First Indirect Name"))
                continue
            else:
                FirstIndirectNameIndex = 3
            if DocType == DocTypes["LP"] or DocType == DocTypes["PALIE"]:
                FirstIndirectName.append(columns[FirstIndirectNameIndex].text)
            else:
                try:
                    FirstIndirectName.append(columns[FirstIndirectNameIndex-1].text)
                except:
                    FirstIndirectName.append(np.nan)
            if DocType is DocTypes["DC"] or DocType is DocTypes["PALIE"]:
                CaseNumber.append(np.nan)
            else:
                time.sleep(2)
                row.click()
                driver.switch_to.window(driver.window_handles[1])
                NotLoaded = True
                attempts = 0
                while NotLoaded:
                    try:
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "docBlock")))
                        NotLoaded = False
                    except:
                        print("Page Did not load Cannot grab Case Number. Attempting to reopen page")
                        attempts += 1
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        row.click()
                        driver.switch_to.window(driver.window_handles[1])
                    if attempts > 5:
                        print("Page Did not load Cannot grab Case Number. Skipping")
                        CaseNumber.append(np.nan)
                        break
                time.sleep(2)
                iframe = driver.find_element(By.CLASS_NAME, "docFrame")
                iframes.append(iframe.get_attribute("src"))
                DocBlock = driver.find_element(By.CLASS_NAME, "docBlock")
                Details = DocBlock.find_elements(By.CLASS_NAME, "detailLabel")
                ListDocDetails = DocBlock.find_elements(By.CLASS_NAME, "listDocDetails")
                for Detail in Details:
                    if Detail.text.__contains__("Case Number:"):
                        print("Case Number: " + ListDocDetails[Details.index(Detail)].text)
                        CaseNumber.append(ListDocDetails[Details.index(Detail)].text)
                if len(CaseNumber) < len(FirstIndirectName):
                    print("No Case Number Found")
                    CaseNumber.append(np.nan)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(6)
        if i < NumPages:
            print("Clicking Next Button")
            driver.find_element(By.CLASS_NAME, "t-icon.t-arrow-next").click()
            time.sleep(6)
    df = pd.DataFrame(list(zip(CaseNumber, FirstIndirectName, iframes)), columns=["CaseNumber", "FirstIndirectName",'URL'])
    df["DocType"] = DocType
    df = df[["DocType",'URL', "CaseNumber", "FirstIndirectName"]]
    return df


# This Function will take a dataframe and separate the First Indirect name column into First Name and Last Name columns
# and return the new dataframe
def SeparateNames(df):
    FirstName = []
    LastName = []
    for index, row in df.iterrows():
        if "," in row["FirstIndirectName"]:
            FirstName.append(row["FirstIndirectName"].split(",")[1].split(" ")[0])
            LastName.append(row["FirstIndirectName"].split(",")[0])
            df.at[index, "FirstIndirectName"] = np.nan
        else:
            FirstName.append(np.nan)
            LastName.append(np.nan)
    df["FirstName"] = FirstName
    df["LastName"] = LastName
    df = df.rename(columns={"FirstIndirectName": "CompanyName"})
    return df

# Sets row to NAN if needed.
def SetNAN(index, df):
    df.at[index, "APN"] = np.nan
    df.at[index, "Address"] = np.nan
    df.at[index, "City"] = np.nan
    df.at[index, "State"] = np.nan
    df.at[index, "Zip"] = np.nan
    df.at[index, "MailingAddress"] = np.nan
    df.at[index, "MailingCity"] = np.nan
    df.at[index, "MailingState"] = np.nan
    df.at[index, "MailingZip"] = np.nan
    df.at[index, "JustMarketValue"] = np.nan
    df.at[index, "Taxes"] = np.nan
    df.at[index, "Bed"] = np.nan
    df.at[index, "Bath"] = np.nan
    df.at[index, "SqFt"] = np.nan
    return df


# This Function will Split a Mailing Address into house number, street direction, street name, street type, unit number (if applicable), City, State, Zip
def SplitMailingAddress(mailAddress):
    StreetTypes = ["ALY", "AVE", "BND", "BLVD", "CSWY", "CIR", "CT", "CV", "DRIVE", "EXT", "HWY", "HOLW", "ISLE",
                   "LNDG", "MNR", "MILE", "PASS", "PATH", "PL", "ROAD", "ROW", "SQ", "TER", "TWP","TRCE",
                   "TRL", "VIEW", "WALK", "WAY", "PARK", "COURT", "DR", "PT", "ST", "RD", "LN"]
    MailingAddr = ""
    Remaining = ""
    for streetType in StreetTypes:
        if mailAddress.__contains__(streetType):
            MailingAddr = mailAddress.split(streetType)[0] + streetType
            Remaining = mailAddress.split(streetType)[1]
            break
    if re.search(r"UNIT \d{1,4}", Remaining):
        UnitNumber = re.search(r"UNIT \d{1,4}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"UNIT \d{0,4}[A-Z]", Remaining):
        UnitNumber = re.search(r"UNIT \d{0,4}[A-Z]", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"# \d{0,4}[A-Z]\d{1}", Remaining):
        UnitNumber = re.search(r"# \d{0,4}[A-Z]\d{1}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"#\d{1,5}", Remaining):
        UnitNumber = re.search(r"\d{1,5}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"# \d{1,4}", Remaining):
        UnitNumber = re.search(r"# \d{1,4}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"#[A-Z]-\d{1,4}", Remaining):
        UnitNumber = re.search(r"#[A-Z]-\d{1,4}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"APT \d{1,4}", Remaining):
        UnitNumber = re.search(r"APT \d{1,4}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    elif re.search(r"APT #\d{1,4}", Remaining):
        UnitNumber = re.search(r"APT #\d{1,4}", Remaining).group(0)
        MailingAddr = MailingAddr + " " + UnitNumber
        Remaining = Remaining.split(UnitNumber)[1]
    else:
        Remaining = Remaining
    try:
        State = Remaining.split(" ")[-2]
        Zip = Remaining.split(" ")[-1]
        Zip = Zip[0:5]
        City = Remaining.split(State)[0]
    except:
        City = ""
        State = ""
        Zip = ""
    return MailingAddr, City, State, Zip


# This Function will take a dataframe and grab the address' from the Broward County Property Appraiser Website
def GetAddress(driver, df):
    df["APN"] = ""
    df["Address"] = ""
    df["City"] = ""
    df["State"] = ""
    df["Zip"] = ""
    df["MailingAddress"] = ""
    df["MailingCity"] = ""
    df["MailingState"] = ""
    df["MailingZip"] = ""
    df["JustMarketValue"] = ""
    df["Taxes"] = ""
    df["Bed"] = ""
    df["Bath"] = ""
    df["SqFt"] = ""

    print("Starting GetAddress Function")
    print(df)
    time.sleep(5)
    for index, row in df.iterrows():
        driver.get("https://bcpa.net/RecName.asp")
        try:
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "Name")))
        except:
            print("Website did not load")
            continue
        time.sleep(2)
        try:
            Name = df.at[index, "LastName"] + ", " + df.at[index, "FirstName"]
            NameField = driver.find_element(By.ID, "Name")
            NameField.send_keys(Name)
            NameField.send_keys(Keys.ENTER)
            time.sleep(3)
        except:
            print("Error: " + str(sys.exc_info()[0]))
            df = SetNAN(index, df)
            df.at[index, "CompanyName"] = np.nan
            continue
        if driver.current_url.__contains__("RecSearch.asp"):
            print("Multiple Results Found/No Results Found")
            df.at[index, "Address"] = "Manual Search required"
            continue
        else:
            try:
                WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.CLASS_NAME, "BodyCopyBold9")))
            except:
                print("Website did not load")
                df = SetNAN(index, df)
                continue
            time.sleep(2)
        try:
            Folio = driver.current_url.split("URL_Folio=")[1]
            Address = driver.find_element(By.CLASS_NAME, "BodyCopyBold9").find_element(By.TAG_NAME, "a").text
            City = Address.split(",")[1].split("FL")[0]
            State = Address.split(" ")[-2].split(" ")[0]
            Zip = Address.split(",")[1].split("FL")[1].split(" ")[1]
            City = City.strip()
            State = State.strip()
            Zip = Zip.strip()[0:5]

            
            try:
                

                df.loc[index, "APN"] = FolioForBroward(str(Folio))
            except:
                print('Error while conveting Folio')
                df.loc[index, "APN"] = Folio


            df.at[index, "Address"] = Address.split(",")[0]
            df.at[index, "City"] = City
            df.at[index, "State"] = State
            df.at[index, "Zip"] = Zip
        except:
            df = SetNAN(index, df)
            print("Error: " + str(sys.exc_info()[0]))
            continue
        MailingAddress = driver.find_elements(By.CLASS_NAME, "BodyCopyBold9")[2].text
        MailingAddressStruct = SplitMailingAddress(MailingAddress)
        df.at[index, "MailingAddress"] = MailingAddressStruct[0]
        df.at[index, "MailingCity"] = MailingAddressStruct[1]
        df.at[index, "MailingState"] = MailingAddressStruct[2]
        df.at[index, "MailingZip"] = MailingAddressStruct[3]
        JustMarketValue = driver.find_elements(By.TAG_NAME, "td")[49].text
        print("Just Market Value: " + JustMarketValue)
        df.at[index, "JustMarketValue"] = JustMarketValue
        try:
            Taxes = driver.find_elements(By.TAG_NAME, "td")[57].text
            if Taxes.__contains__(" "):
                Taxes = driver.find_elements(By.TAG_NAME, "td")[57].text
        except:
            Taxes = driver.find_elements(By.TAG_NAME, "td")[58].text
        df.at[index, "Taxes"] = Taxes
        BedBath = driver.find_elements(By.TAG_NAME, "td")[162].text
        if BedBath.__contains__("its"):
            BedBath = driver.find_elements(By.TAG_NAME, "td")[163].text
        if BedBath.__contains__("/"):
            Bed = BedBath[2:].split("/")[0]
            Bath = BedBath[2:].split("/")[1]
            df.at[index, "Bed"] = Bed
            df.at[index, "Bath"] = Bath
        else:
            df.at[index, "Bed"] = np.nan
            df.at[index, "Bath"] = np.nan
        SqFt = driver.find_elements(By.TAG_NAME, "td")[160].text
        if SqFt.__contains__("Adj. Bldg. S.F."):
            SqFt = driver.find_elements(By.TAG_NAME, "td")[161].text
        df.at[index, "SqFt"] = SqFt
        if Taxes.__contains__(str(datetime.datetime.now().year - 1)):
            df.at[index, "Taxes"] = np.nan
            df.at[index, "Bed"] = np.nan
            df.at[index, "Bath"] = np.nan
            df.at[index, "SqFt"] = np.nan
            df.at[index, "JustMarketValue"] = np.nan
    return df

# Testing the functions
def Run(CurrentDocType, Drive, StartDate=None, EndDate=None):
    driver = InitDriver()
    if CurrentDocType == "EV":
        df = EvictionsSearch(driver, StartDate, EndDate)
    else:
        Search(driver, DocTypes[CurrentDocType], StartDate, EndDate)
        df = Scrape(driver, DocTypes[CurrentDocType])
        df = SeparateNames(df)
    df = GetAddress(driver, df)
    df = df.dropna(subset=["Address"])
    if CurrentDocType != "EV":
        if df["CompanyName"].isnull().all():
            df = df.drop(columns=["CompanyName"])
        if df["CaseNumber"].isnull().all():
            df = df.drop(columns=["CaseNumber"])
    if StartDate is None or EndDate is None:
        print("No StartDate or EndDate given")
        Yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        Yesterday = str(Yesterday).split(" ")[0].replace("/", "-")
        SaveTo = str(DocTypes[CurrentDocType]) + str(Yesterday) + ".csv"
        print(SaveTo)
    else:
        print("Saving as yesterday")
        EndDate = str(EndDate).split(" ")[0].replace("/", "-")
        SaveTo = str(DocTypes[CurrentDocType]) + "-" + str(EndDate) + ".csv"
        Manuaul = str(DocTypes[CurrentDocType]) + "-" + str(EndDate) + "-ManualSearch.csv"
        print(SaveTo)
    ManualSearch = df[df["Address"] == "Manual Search required"]
    df = df[df["Address"] != "Manual Search required"]
    os.makedirs('output', exist_ok=True)
    SaveTo = os.getcwd() + "\\output\\"  + SaveTo
    Manuaul = os.getcwd() + "\\output\\"  + Manuaul
    df.to_csv(SaveTo, index=False)
    ManualSearch.to_csv(Manuaul, index=False)
    driver.quit()
    print("Finished Scraping " + str(DocTypes[CurrentDocType]))
    return 0
if __name__ == "__main__":

    Run("LP", "B-LP", '08/14/2023', '08/14/2023')
