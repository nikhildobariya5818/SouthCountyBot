# This file was written by: Carick Brandt on 4/2023
# This file will pull records from the Miami-Dade County Clerks website and run them against the property appraiser's website

import math
import os
import time
import datetime
import SetDates
import numpy as np
from keywords import COMPANY_KEYWORDS
import pandas as pd
import json
import traceback
import sys
import re
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from MiamidadeSearch import getFolioNumber,PropertyInformation,getZoning 
from search_owner import search_owners_from_sunbiz
from FolioConverter import FolioForMiami
from bs4 import BeautifulSoup
from clean_name import CleanName
DocTypes = {
    "PAD": "Probate & Administration (PAD)",
    "DCE": "Death Certificate (DCE)",
    "LIS": "Lis Pendens (Lis)"
}

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

def CheckElementByClass(driver, ElementID):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, ElementID)))
    except:
        for i in range(3):
            driver.refresh()
            time.sleep(15)
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, ElementID)))
                break
            except:
                if i == 3:
                    print("Page did not load correctly")
                    return False
    return True

# Inits Driver and passes options into it
def InitDriver():
    testUA = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'user-agent={testUA}')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = uc.Chrome(executable="C:\\Users\\Global\\Downloads\\chromedriver-win64\\chromedriver.exe",options=options)
    return driver


# This Function will split the Parties from "First Party (Code)  Second Party (Code)"
def SplitParties(df):

    df["First Name"] = ''
    df["Middle Name"] = ''
    df["Organization Name"] = ""
    for index, row in df.iterrows():

        # ------------------------------------------ owner name start --------------------------------------
    #     ownerList = []
    #     tmpowner_first = search_owners_from_sunbiz(row["First Party"])
    #     ownerList.extend(tmpowner_first)
    #     tmpowner_second = search_owners_from_sunbiz(row["Second Party"])
    #     ownerList.extend(tmpowner_second)

    #     df.loc[index, "Organization Name"] = row['First Party (Code)  Second Party (Code)']
    #     for count, owner_data in enumerate(ownerList, start=1):
    #         ownerNum = '' if count == 1 else f' {count}'
    #         colnameF = f'Owner{ownerNum} First Name'
    #         colnameM = f'Owner{ownerNum} Middle Name'
    #         colnameL = f'Owner{ownerNum} Last Name'

    #         # Check if the columns exist, and if not, add them to the DataFrame
    #         if colnameF not in df.columns:
    #             df[colnameF] = ''
    #         if colnameM not in df.columns:
    #             df[colnameM] = ''
    #         if colnameL not in df.columns:
    #             df[colnameL] = ''

    #         # Populate the DataFrame with owner data
    #         if 'first_name' in owner_data:
    #             df.loc[index, colnameF] = owner_data['first_name']
    #         if 'middle_name' in owner_data:
    #             df.loc[index, colnameM] = owner_data['middle_name']
    #         if 'last_name' in owner_data:
    #             df.loc[index, colnameL] = owner_data['last_name']


        # ------------------------------------------ owner name end --------------------------------------


        Party = row["First Party (Code)  Second Party (Code)"].split(")  ")[0]
        if row["Misc Ref"] == "WILL":
            df.at[index, "First Party (Code)  Second Party (Code)"] = np.nan
            continue
        Party = Party.split(" (")[0]
        Spaces = Party.count(" ")
        if int(Spaces) <= 2:
            df.at[index, "First Party (Code)  Second Party (Code)"] = Party
            if int(Spaces) == 2:
                Party = Party.split(" ")
                df.at[index, "First Name"] = Party[1]
                df.at[index, "Middle Name"] = Party[2]
                df.at[index, "First Party (Code)  Second Party (Code)"] = Party[0]
            if int(Spaces) == 1:
                Party = Party.split(" ")
                df.at[index, "First Name"] = Party[1]
                df.at[index, "First Party (Code)  Second Party (Code)"] = Party[0]
            if int(Spaces) == 0:
                df.at[index, "First Party (Code)  Second Party (Code)"] = np.nan
        else:
            df.at[index, "First Party (Code)  Second Party (Code)"] = np.nan
    df.dropna(subset=["First Party (Code)  Second Party (Code)"], inplace=True)
    df.rename(columns={"First Party (Code)  Second Party (Code)": "Last Name"}, inplace=True)
    df = df[~df["Last Name"].str.contains("INC", na=False)]
    df = df[~df["Last Name"].str.contains("BANK", na=False)]
    df = df[~df["Last Name"].str.contains("TRUST", na=False)]
    df = df[~df["Last Name"].str.contains("LLC", na=False)]

    df.drop_duplicates(subset=["Clerk's File No"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# This Function will grab a dataframe from the tables on the Miami-Dade County Clerk's website
def GetTable(driver):
    time.sleep(2)
    Results = driver.find_element(By.ID, "lblResults").text
    Pages = math.ceil(int(Results) / 50)
    # print(Pages)
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')
    listing = []
    links = table.find('tbody').find_all('tr')
    import re
    for tr in links:
        onclick_value = tr['onclick']
        url_start = onclick_value.find("'") + 1
        url_end = onclick_value.find("'", url_start)
        url = onclick_value[url_start:url_end]
        combination = tr.find_all('td')[-1].text.strip().replace('\n', '')
        combination = re.sub(r'\s +', ' ', combination)
        combination = combination.replace(') ', ')  ')
        first_name = combination.split('  ')[0]
        first_name = first_name.split('(')[0]
        if '()' in first_name:
            first_name = ""
        second_name = combination.split('  ')[-1]
        second_name = second_name.split('(')[0]
        if '()' in second_name:
            second_name = ""

        # print("first name : ",first_name)
        # print("second name : ",second_name)
        date = tr.find_all('td')[3].text.strip()
        listing.append({"url": "https://onlineservices.miamidadeclerk.gov/officialrecords/" + url,
                         "First Party (Code)  Second Party (Code)": combination,
                         "Rec Book/Page": date,
                         'First Party':first_name,
                         'Second Party':second_name})
    
    df = pd.DataFrame(pd.read_html(driver.page_source)[0])
    time.sleep(3)
    dfList = [df]
    
    if Pages > 1:
        for i in range(1, Pages):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.find_element(By.LINK_TEXT, str(i+1)).click()
            time.sleep(10)
            tDf = pd.DataFrame(pd.read_html(driver.page_source)[0])
            dfList.append(tDf)
    
    Complete = pd.concat(dfList, ignore_index=True)
    
    Complete.insert(loc=1, column='URL', value='')
    Complete.insert(loc=1, column='First Party', value='')
    Complete.insert(loc=1, column='Second Party', value='')
    
    for index, row in Complete.iterrows():
        for l in listing:
            if l['Rec Book/Page'] + l['First Party (Code)  Second Party (Code)']== row["Rec Book/Page"] + row["First Party (Code)  Second Party (Code)"]:
                Complete.loc[index, 'URL'] = l["url"]
                Complete.loc[index, 'First Party'] = l["First Party"]
                Complete.loc[index, 'Second Party'] = l["Second Party"]
                # print('--------',Complete.loc[index,'URL'],l["url"])
    # print(Complete)
    # SaveNonMatch = os.getcwd() + "\\output" + "\\Complete.csv"
    # Complete.to_csv(SaveNonMatch, index=True)
    
    return Complete


# This function will Login to the Clerks site
def Login(driver):
    driver.get("https://www2.miamidadeclerk.gov/PremierServices/login.aspx")
    time.sleep(5)
    UsernameField = driver.find_element(By.ID, "ctl00_cphPage_txtUserName")
    for char in "Cjbrandt10":
        UsernameField.send_keys(char)
        time.sleep(.15)
    PasswordField = driver.find_element(By.ID, "ctl00_cphPage_txtPassword")
    for char in "Livelife1!":
        PasswordField.send_keys(char)
        time.sleep(.15)
    PasswordField.send_keys(Keys.ENTER)
    time.sleep(5)
    driver.get("https://onlineservices.miamidadeclerk.gov/officialrecords/StandardSearch.aspx")
    time.sleep(5)
    return 0

def Search(driver, DocType, StartDate: str, EndDate: str):
    StartDateField = driver.find_element(By.ID, "prec_date_from")
    StartDateField.click()
    StartDateField.clear()
    for char in StartDate:
        StartDateField.send_keys(char)
        time.sleep(.15)

    EndDateField = driver.find_element(By.ID, "prec_date_to")
    EndDateField.click()
    EndDateField.clear()
    for char in EndDate:
        EndDateField.send_keys(char)
        time.sleep(.15)

    DocTypeDropdown = driver.find_element(By.ID, "pdoc_type")
    DocTypeDropdown.click()
    DocTypeDropdown.send_keys(DocType)
    time.sleep(2)

    SearchButton = driver.find_element(By.ID, "btnNameSearch")
    SearchButton.click()
    time.sleep(5)
    return 0


# Grabs the Records from the Clerk Site
def GetRecords(driver, DocType, StartDate: str = None, EndDate: str = None):
    Login(driver)
    if StartDate is None:
        StartDate, EndDate = SetDates.NoDates()
    Search(driver, DocType, StartDate, EndDate)
    df = GetTable(driver)
    df = SplitParties(df)
    df = GetPropertyAddress(driver,df)
    df.drop(columns=["Rec Book/Page", "Plat Book/Page", "Blk", "Legal", "Doc Type","Second Party","First Party"], inplace=True)
    df.drop(columns="Misc Ref", inplace=True)
    df.rename(columns={"Clerk's File No": "Case #"}, inplace=True)
    # df = df[["Rec Date", "Case #",'URL', "First Name", "Middle Name", "Last Name"]]
    df2 = df[df["Property Address"] == "Not Found"]
    df = df[df["Property Address"] != "Not Found"]
    Date1 = StartDate.replace("/", "-")
    Date2 = EndDate.replace("/", "-")
    SaveTo = os.getcwd() + "\\output" + "\\MiamiDadeRecordsTest-" + DocType + "-" + Date1 + "to" + Date2 + ".csv"
    SaveNonMatch = os.getcwd() + "\\output" + "\\MiamiDadeRecordsTest-" + DocType + "-" + Date1 + "to" + Date2 + "-NotMatched.csv"
    df2.to_csv(SaveNonMatch, index=False)
    df.to_csv(SaveTo, index=False)
    sunbiz_data =  os.getcwd() + "\\output" + "\\MiamiDadeRecordsTest-" + DocType + "-" + Date1 + "to" + Date2 + "-sunbiz.csv"
    if 'sunbiz' in df.columns:
        df3 = df[df['sunbiz'] == True]
        df3.to_csv(sunbiz_data,Index=False)

        # Rest of your code that uses df3
    else:
        print("'sunbiz' column not found in DataFrame.")
    driver.quit()
    return SaveTo, SaveNonMatch ,sunbiz_data

# This function will grab the Property Address from the miami-dade county property appraiser's website
def GetPropertyAddress(driver,df):
    df["APN"] = ""
    df["Property Address"] = ""
    df["Property City"] = ""
    df["Property State"] = "FL"
    df["Property Zip"] = ""
    df["Mailing Address"] = ""
    df["Mailing City"] = ""
    df["Mailing State"] = ""
    df["Mailing Zip"] = ""
    df["Land zoning"] = ""
    df["Land Use"] = ""
    df["Bedrooms"] = ""
    df["Bathrooms"] = ""
    df["Sqft"] = ""
    df["Year"] = ""
    df["Number of units"] = ""
    df["Legal description"] = ""
    df["Organization Name"] = ''

    # print(df.columns)
    for index, row in df.iterrows():
        print('*'*50)
        try:    
            name = row["First Name"]
            name += ", "

            if row["Middle Name"] != "":
                name += row["Middle Name"] + " "

            name += row["Last Name"]  

            Folio = getFolioNumber(name)
            if int(Folio) <1:
                raise ValueError() 
            data = PropertyInformation(Folio).get_parsed_info()
            print(data)
            
            # df.loc[index, "Mailing Address"] = data["mailing_address"]
            # df.loc[index, "Mailing City"] = data["city"]
            # df.loc[index, "Mailing State"] = data["state"]
            # df.loc[index, "Mailing Zip"] = data["zip_code"]
            df.loc[index, "Property Address"] = data[0]["property_address"]
            df.loc[index, "Property City"] = data[0]["property_address_city"]
            df.loc[index, "Property Zip"] = data[0]["property_address_zip"]
            df.loc[index, "Land Use"] = data[0]["primary_land_use"]
            df.loc[index, "Bedrooms"] = data[0]["bedroom_count"]
            df.loc[index, "Bathrooms"] = data[0]["bathroom_count"]
            df.loc[index, "Sqft"] = data[0]["building_actual_area"]
            df.loc[index, "Year"] = data[0]["year_built"]
            df.loc[index, "Number of units"] = data[0]["living_units"]
            df.loc[index, "Legal description"] = data[0]["legal_description"]
            df.loc[index,"Organization Name"] = data[0]["owner_name"]

            if data[0]["property_address"] == "":
                df.loc[index, "Property Address"] = FolioForMiami(str(Folio))
                df.loc[index, "Property City"] = data[0]["city"]
                df.loc[index, "Property Zip"] = data[0]["zip_code"]

        
            for count, owner_data in enumerate(data, start=1):
                ownerNum = '' if count == 1 else f' {count}'
                colnameF = f'Owner {ownerNum} First Name'
                colnameM = f'Owner{ownerNum} Middle Name'
                colnameL = f'Owner{ownerNum} Last Name'
                Mailing_Address = f'Owner {ownerNum} Mailing Address'
                Mailing_City = f'Owner{ownerNum} Mailing City'
                Mailing_State = f'Owner{ownerNum} Mailing State'
                Mailing_Zip = f'Owner{ownerNum} Mailing Zip'
                sunbiz = f'{ownerNum} sunbiz'

                # Check if the columns exist, and if not, add them to the DataFrame
                if colnameF not in df.columns:
                    df[colnameF] = ''
                if colnameM not in df.columns:
                    df[colnameM] = ''
                if colnameL not in df.columns:
                    df[colnameL] = ''
                if Mailing_Address not in df.columns:
                    df[Mailing_Address] = ''
                if Mailing_City not in df.columns:
                    df[Mailing_City] = ''
                if Mailing_State not in df.columns:
                    df[Mailing_State] = ''
                if Mailing_Zip not in df.columns:
                    df[Mailing_Zip] = ''
                if sunbiz not in df.columns:
                    df[sunbiz] = ''

                # Populate the DataFrame with owner data
                if 'first_name' in owner_data:
                    df.loc[index, colnameF] = owner_data['first_name']
                if 'middle_name' in owner_data:
                    df.loc[index, colnameM] = owner_data['middle_name']
                if 'last_name' in owner_data:
                    df.loc[index, colnameL] = owner_data['last_name']
                if 'mailing_address' in owner_data:
                    df.loc[index,Mailing_Address] = owner_data['mailing_address']
                if 'city' in owner_data:
                    df.loc[index,Mailing_City] = owner_data['city']
                if 'state' in owner_data:
                    df.loc[index,Mailing_State] = owner_data['state']
                if 'zip_code' in owner_data:
                    df.loc[index,Mailing_Zip] = owner_data['zip_code']
                if 'sunbiz' in owner_data:
                    if owner_data['sunbiz'] == True:
                        df.loc[index, sunbiz] = True
                    else:
                        df.loc[index, sunbiz] = ''
                
            try:

                df.loc[index, "APN"] = FolioForMiami(str(Folio))
            except:
                print('Error while conveting Folio')
                df.loc[index, "APN"] = Folio

            if data[0]["parent_folio"] != '':
                Folio = data[0]["parent_folio"]
            try:
                zone = getZoning(Folio)
                df.loc[index, "Land zoning"] = zone 
            except Exception as e:
                df.loc[index, "Land Use"] = np.nan
                print(e)
                print('Error in Zoning')

            SaveNonMatch = os.getcwd() + "\\output" + "\\Complete.csv"
            df.to_csv(SaveNonMatch, index=True)

        except Exception as e:
            print(e.__class__,traceback.format_exc(),sys.exc_info())
            print("Multiple Results for Search")
            df.loc[index, "APN"] = np.nan
            df.loc[index, "Property Address"] = "Not Found"
            df.loc[index, "Property City"] = np.nan
            df.loc[index, "Property Zip"] = np.nan
            df.loc[index, "Mailing Address"] = np.nan
            df.loc[index, "Mailing City"] = np.nan
            df.loc[index, "Mailing State"] = np.nan
            df.loc[index, "Mailing Zip"] = np.nan
            df.loc[index, "Land zoning"] = np.nan
            df.loc[index, "Land Use"] = np.nan
            df.loc[index, "Bedrooms"] = np.nan
            df.loc[index, "Bathrooms"] = np.nan
            df.loc[index, "Sqft"] = np.nan
            df.loc[index, "Year"] = np.nan
            df.loc[index, "Number of units"] = np.nan
            df.loc[index, "Legal description"] = np.nan

            time.sleep(1.5)
    
    
    for index, row in df.iterrows():
        try:
            if "UNINCORPORATED" in row["Mailing City"]:
                df.loc[index, "Mailing City"] = "Miami"
        except:
            df.loc[index, "Mailing City"] = "Miami"
            
    # dats = os.getcwd() + "\\output" + "\\all_dta.csv"
    # df.to_csv(dats, index=True)
    return df
# B64
# RnJvbSBvbmUgcHJvZ3JhbW1lciB0byBhbm90aGVyIHRoZSBndXkgeW91IGFyZSB3b3JraW5nIHdpdGggaXMgYSBmdWNraW5nIGlkaW90IGFuZCB3aWxsIGNoYW5nZSBoaXMgZXhwZWN0YXRpb25zIG9uIGENCldoaW0sIEFsc28gaGlzIG5lcGhldyBpcyBhIGNvbXAgc2NpIGdyYWR1YXRlIGFuZCBhcHBhcmVudGx5IHRoYXQgbWVhbnMgdGhlIGRlZ3JlZSB0cmF2ZWxzIGJhY2t3YXJkcyB0aHJvdWdob3V0IHRoZSBmYW1pbHkgb2J2aW91c2x5Lg0KTXkgQ29kZSB3YXMgY2xlYW5lciBiZWZvcmUgdGhlIDV0aCByZXZpc2lvbiB0byB3aGF0IGlzICJyZXF1aXJlZCIgZnJvbSBtZQ==

def test():
        
        filename  = "Output\\MiamiDadeForeclosure_RPMF__HOMESTEAD_07-17-2023_07-17-2023_NotMatched.csv"

        df = pd.read_csv(filename, converters={'Folio': str,'Middle Name': str})

        Date1 = '123'.replace("/", "-")
        Date2 = '456'.replace("/", "-")
        os.makedirs('output', exist_ok=True)
        filename = 'test'
        File = os.getcwd() +"\\output" + "\\MiamiDadeForeclosure_" +filename+"_" + Date1 + "_" + Date2 + ".csv"
        File2 = os.getcwd() +"\\output" + "\\MiamiDadeForeclosure_" +filename+"_" + Date1 + "_" + Date2 + "_NotMatched.csv"
        File3 = os.getcwd() +"\\output" + "\\MiamiDadeForeclosure_" +filename+"_" + Date1 + "_" + Date2 + "sunbiz.csv"

        df = GetPropertyAddress('driver', df)
        df2 = df[df["Property Address"] == "Not Found"]
        df3 = df[df["sunbiz"] == "True"]
        df = df[df["Property Address"] != "Not Found"]
        
        df.to_csv(File, index=False) 
        df2.to_csv(File2, index=False)
        df3.to_csv(File3, index=False)


def ForeclosureSearch(driver, StartDate=None, EndDate=None):
    # ForeclosureTypes = {1: "RPMF -HOMESTEAD", 2: "RPMF -NON-HOMESTEAD",3:"RPMF -COMMERCIAL",4:"RPMF -OTHER ACTION"}
    ForeclosureTypes = {1: "RPMF -HOMESTEAD"}
    Login(driver)
    for Code in ForeclosureTypes:
        Plaintiffs = []
        Defendants = []
        Notes = []
        tests = []
        driver.get("https://www2.miamidadeclerk.gov/ocs/Search.aspx?type=premier")
        driver.maximize_window()
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.75);")
        if StartDate is None and EndDate is None:
            StartDate = datetime.datetime.today() - datetime.timedelta(days=1)
            EndDate = datetime.datetime.today()
            StartDate = StartDate.strftime("%m/%d/%Y")
            EndDate = EndDate.strftime("%m/%d/%Y")
        else:
            StartDate = StartDate
            EndDate = EndDate
        CheckElement(driver,"ctl00_ContentPlaceHolder1_pP1_Atty_Bar_Num_generalContent")
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_pFiling_Date_From_generalContent").send_keys(StartDate)
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_pFiling_Date_To_generalContent").send_keys(EndDate)
        # driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_pP1_Atty_Bar_Num_generalContent").click()
        time.sleep(.15)
        CheckElement(driver,"ctl00_ContentPlaceHolder1_ddlCaseType_PRM_generalContent")
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCaseType_PRM_generalContent").click()
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCaseType_PRM_generalContent").send_keys(ForeclosureTypes[Code])
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCaseType_PRM_generalContent").send_keys(Keys.ENTER)
        time.sleep(.15)
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnGeneralSearch").click()
        time.sleep(4)
        try:
            Total = int(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblResults").text.split(" ")[-1])
            print(Total)
        except:
            Total = 0
        for Num in range(0, Total):
            rID = "ctl00_ContentPlaceHolder1_reResults_ctl{:02d}_trItem".format(Num)
            row = driver.find_element(By.ID, rID)
            row.find_element(By.CLASS_NAME, "btn.coc-button--blue.pointer").click()

            time.sleep(2)

            CheckElementByClass(driver,"card.m-md-2.shadow-lg")

            LoadParties = driver.find_elements(By.CLASS_NAME, "card.m-md-2.shadow-lg")[2]
            LoadParties.click()
            time.sleep(.15)
            Result = LoadParties.text
            print(Result)
            Result = Result.split("Attorney(S)\n")[1]
            Plaintiff = Result.split("Plaintiff")[1].split("\n")[0]
            Defendant = Result.split("Defendant")[1].split("\n")[0]
            print(Defendants)
            tests.append(Result)
            
            Plaintiffs.append(Plaintiff)
            Defendants.append(Defendant)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.75);")
            CheckElementByClass(driver,"card.m-md-2.shadow-lg")
            LoadComplaint = driver.find_elements(By.CLASS_NAME, "card.m-md-2.shadow-lg")[4]
            LoadComplaint.click()
            time.sleep(.15)
            Dockets = LoadComplaint.find_element(By.ID, "bodySearchCriteria2")
            for tr in Dockets.find_elements(By.TAG_NAME, "tr"):
                for td in tr.find_elements(By.TAG_NAME, "td"):
                    if "Complaint" in td.text:
                        try:
                            CheckElementByClass(driver,"btn.btn-lg")
                            Link = tr.find_element(By.CLASS_NAME, "btn.btn-lg")
                            Html = Link.get_attribute("outerHTML")
                            Html = Html.split("window.open('")[1].split("',")[0]
                            Link = "https://www2.miamidadeclerk.gov/ocs/{}".format(Html)
                        except:
                            Link = ""
                        print(Link)
                        Notes.append(Link)
            driver.back()
            time.sleep(2)
        df = pd.DataFrame(list(zip(Plaintiffs, Defendants, Notes,tests)), columns=["Plaintiff", "Defendant", "Notes","tests"])
        df['Owner Name'] = ''
        for Index, Row in df.iterrows():
            if "," not in Row["Defendant"]:
                df.drop(Index, inplace=True)
            else:
                try:
                    owner = CleanName(Row["Defendant"]).get_cleaned_name()[0]
                    df.loc[Index, "Last Name"] = owner['last_name']
                    df.loc[Index, "First Name"] = owner['first_name']
                    df.loc[Index, "Middle Name"] = owner['middle_name']
                    
                except:
                    df.drop(Index, inplace=True)
        for Index, Row in df.iterrows():
            df.loc[Index, "Last Name"] = Row["Last Name"].replace("AKA", "").replace("(ESTATE OF)", "").strip()
        df.reset_index(drop=True, inplace=True)
        driver.get("https://www2.miamidadeclerk.gov/ocs/Search.aspx?type=premier")
        df.drop("Defendant", axis=1, inplace=True)
        Date1 = StartDate.replace("/", "-")
        Date2 = EndDate.replace("/", "-")
        os.makedirs('output', exist_ok=True)
        filename = ForeclosureTypes[Code].replace(" ","_").replace("-","_")
        File = os.getcwd() +"\\output" + "\\MiamiDadeForeclosure_" +filename+"_" + Date1 + "_" + Date2 + ".csv"
        File2 = os.getcwd() +"\\output" + "\\MiamiDadeForeclosure_" +filename+"_" + Date1 + "_" + Date2 + "_NotMatched.csv"

        df = GetPropertyAddress(driver, df)
        df.drop("tests", axis=1, inplace=True)
        df2 = df[df["Property Address"] == "Not Found"]
        df = df[df["Property Address"] != "Not Found"]
        
        df.to_csv(File, index=False) 
        df2.to_csv(File2, index=False)
    return 0


def Run(DocType, StartDate, EndDate):
    driver = InitDriver()
    SaveTo, SaveNotMatched = GetRecords(driver, DocTypes[DocType], StartDate, EndDate)
    return 0

if __name__ == "__main__":
    # ForeclosureSearch(InitDriver(), "08/11/2023", "08/11/2023")
    GetRecords(InitDriver(),"PROBATE & ADMINISTRATION - PAD ", "08/03/2023", "08/11/2023")
    # test()
    # df = pd.read_csv(r'C:\Users\Global\SouthCountyBot\output\FOLIO.csv')
    # GetPropertyAddress(df)