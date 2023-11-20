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
from FolioConverter import FolioForBroward
import undetected_chromedriver as uc
from BrowardRecordsPull import SetNAN,SplitMailingAddress
from clean_name import CleanName
from BrowardZoning import Zones

def InitDriver():
    # Create an Undetectable Chrome Driver
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    driver = uc.Chrome(options=options)
    return driver

def getAddressFromFOLIOBroward(driver, df):
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

    df["Zoning"] = ""

    print("Starting getAddressFromFOLIOBroward Function")
    # print(df)
    time.sleep(5)
    for index, row in df.iterrows():
        driver.get("https://bcpa.net/RecID.asp")
        try:
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "FOLIO_NUMBER")))
        except:
            print("Website did not load")
            continue
        time.sleep(2)
        try:
            Folio = df.at[index, "Folio"]
            FolioField = driver.find_element(By.ID, "FOLIO_NUMBER")
            FolioField.send_keys(str(Folio))
            FolioField.send_keys(Keys.ENTER)
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

            names = driver.find_elements(By.CLASS_NAME, "BodyCopyBold9")[1].text.splitlines()
            print(names)

            for count in range(0,len(names)):
                ownerNum = ' '+ str(count+1)
                if count+1 ==1:
                    ownerNum = ' '
                colnameF = 'Owner' + ownerNum + ' First Name' 
                colnameM = 'Owner' + ownerNum + ' Middle Name' 
                colnameL = 'Owner' + ownerNum + ' Last Name' 
                if colnameF not in df.columns:
                    df[colnameF] = ''
                    df
                    df.loc[index, colnameF] = '100'
                if colnameM not in df.columns:
                    df[colnameM] = ''
                if colnameL not in df.columns:
                    df[colnameL] = ''
                c = CleanName(names[count])
                out = c.get_cleaned_name()
                df.loc[index, colnameF] = out[0]['first_name']
                df.loc[index, colnameM] = out[0]['middle_name']
                df.loc[index, colnameL] = out[0]['last_name']
                
            try:
                zone = driver.find_elements(By.CLASS_NAME, "BodyCopyBold9")[5].text.strip()
                df.at[index, "Zoning"] = Zones[zone]
                
            except Exception as e:
                print(e)
                df.at[index, "Zoning"] = np.nan
                pass




            
            try:
                

                df.loc[index, "APN"] = FolioForBroward(str(Folio))
            except:
                print('Error while conveting Folio')
                df.loc[index, "APN"] = Folio


            df.at[index, "Address"] = Address.split(",")[0]
            df.at[index, "City"] = City
            df.at[index, "State"] = State
            df.at[index, "Zip"] = Zip
        except Exception as e:
            df = SetNAN(index, df)
            print("Error: "+str(e)  + str(sys.exc_info()[0]))
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


if __name__ == "__main__":
    # ForeclosureSearch(InitDriver(), "08/09/2023", "08/14/2023")
    # fname = 'Input\\FOLIO.csv'
    # df = pd.read_csv(fname)

    df = pd.DataFrame([{"Folio":'504201110630'}])
    df = getAddressFromFOLIOBroward(InitDriver(),df)

    File = os.getcwd() +"\\output\\FOLIO.csv"

    df.to_csv(File, index=False)
    input()
    # test()