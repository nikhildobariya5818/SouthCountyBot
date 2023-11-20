import os
import pandas as pd
import time
import SetDates
import MiamiDadeTaxDel
import MiamiDadeCVPull
import MiamiDadeRecordsPull
import BrowardRecordsPull
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from getAddressFromFOLIO import getAddressByFolio
from getAddressFromAddress import getAddressFromAddress
from getAddressFromOwner import getAddressFromOwner
from getAddressFromFOLIOBroward import getAddressFromFOLIOBroward
from search_owner import customer_folio
from realfoerce import THEDATA 


def CountyMenu():
    active = True
    while active:
        print("Welcome to the South Florida Records Pull Program")
        print("Please select the county you would like to pull records from")
        print("1. Miami-Dade County")
        print("2. Broward County")
        print("3. general  Run")
        print("4. Pull All (Custom Dates)")
        print("5. Exit the Program")
        UserInput = input("Please enter the number of the county you would like to pull records from: ")
        if UserInput == "1":
            MiamiDadeMenu()
        elif UserInput == "2":
            BrowardMenu()
        elif UserInput == "3":
            filename = input("Enter filename: ")
            print('Fetching address from file',filename)
            fname = 'Input\\' + filename
            df = pd.read_csv(fname)
            df = customer_folio(df)
            File = os.getcwd() +"\\output\\" +filename
            df.to_csv(File, index=False)
            active = False
            exit()
        elif UserInput == "4":
            StartDate, EndDate = SetDates.GetDates()
            BrowardRecordsPullAll(StartDate, EndDate)
            MiamiDadePullAll(StartDate, EndDate)
        elif UserInput == "5":
            active = False
            exit()
        else:
            print("Please enter a valid option")
    return 0


def MiamiDadeMenu():
    active = True
    while active:
        print("Welcome to the Miami-Dade Records Pull Program")
        print("Please select the type of records you would like to pull")
        print("1. Lis Pendens")
        print("2. Death Certificates")
        print("3. Probates")
        print("4. Code Violations")
        print("5. Public unpaid accts")
        print("6. Get Adderess From custom File (Folio)")
        print("7. Get Adderess From custom File (Address)")
        print("8. Get Adderess From custom File (Owner)")
        print("9. realforeclose ")
        print("10. Exit the Program")

        UserInput = input("Please enter the number of the records you would like to pull: ")
        if UserInput == "1":
            StartDate, EndDate = SetDates.GetDates()
            MiamiDadeRecordsPull.ForeclosureSearch(MiamiDadeRecordsPull.InitDriver(), StartDate, EndDate)
        elif UserInput == "2":
            StartDate, EndDate = SetDates.GetDates()
            MiamiDadeRecordsPull.Run("DCE", StartDate, EndDate)
        elif UserInput == "3":
            StartDate, EndDate = SetDates.GetDates()
            MiamiDadeRecordsPull.Run("PAD", StartDate, EndDate)
        elif UserInput == "4":
            TempSave = os.getcwd() + "\\MiamiDadeCVTemp.csv"
            StartDate, EndDate = SetDates.GetDates()
            df = MiamiDadeCVPull.Search(MiamiDadeCVPull.InitDriver(), StartDate, EndDate)
            df = MiamiDadeCVPull.GetPropertyInfo(MiamiDadeCVPull.InitDriver(), df)
            df.to_csv(TempSave, index=False)
            People, Trust = MiamiDadeTaxDel.SplitNames(TempSave, ColumnName="Name")
            os.remove(TempSave)
            PeopleSave = os.getcwd() + "\\MiamiDadeCVPeople-" + StartDate.replace("/", "-") + "-" + EndDate.replace("/", "-") + ".csv"
            TrustSave = os.getcwd() + "\\MiamiDadeCVTrust-" + StartDate.replace("/", "-") + "-" + EndDate.replace("/", "-") + ".csv"
            People.to_csv(PeopleSave, index=False)
            Trust.to_csv(TrustSave, index=False)
        elif UserInput == "5":
            print("Place File in the TaxDelinquent Folder")
            input("Press Enter to Continue")
            TaxDelinquentFolder = os.getcwd() + "\\TaxDelinquent"
            TaxDelinquentFiles = os.listdir(TaxDelinquentFolder)
            TaxDelinquentFiles.sort()
            TaxDelinquentFile = TaxDelinquentFolder + "\\" + TaxDelinquentFiles[-1]
            People, Trust = MiamiDadeTaxDel.SplitNames(TaxDelinquentFile, ColumnName="Owner Name 1")
            print(People)
            print(Trust)
            PeopleSave = os.getcwd() + "\\MiamiDadeTaxDelPeople-" + time.strftime("%m-%d-%Y") + ".csv"
            TrustSave = os.getcwd() + "\\MiamiDadeTaxDelTrust-" + time.strftime("%m-%d-%Y") + ".csv"
            People.to_csv(PeopleSave, index=False)
            Trust.to_csv(TrustSave, index=False)
        elif UserInput == "6":
            filename = input("Enter filename: ")
            print('Fetching address from file',filename)
            fname = 'Input\\' + filename
            df = pd.read_csv(fname)
            print(df)
            df = getAddressByFolio(df)
            File = os.getcwd() +"\\output\\" +filename
            df.to_csv(File, index=False)
            active = False
            exit()
        elif UserInput == "7":
            filename = input("Enter filename: ")
            getAddressFromAddress(filename)
            active = False
            exit()
        elif UserInput == "8":
            filename = input("Enter filename: ")
            getAddressFromOwner(filename)
            active = False
            exit()
        elif UserInput == "9":
            filename = input('Enter filename: ')

            helper = THEDATA(filename)
            helper.get_data()
            helper.runSearch()
            active = False
            exit()
        # elif UserInput == "10":
        #     filename = input("Enter filename: ")
        #     print('Fetching address from file',filename)
        #     fname = 'Input\\' + filename
        #     df = pd.read_csv(fname)
        #     df = customer_folio(df)
        #     File = os.getcwd() +"\\output\\" +filename
        #     df.to_csv(File, index=False)
        #     active = False
        #     exit()
        elif UserInput == "10":
            active = False
        else:
            print("Please enter a valid option")
    return 0


def BrowardMenu():
    Active = True
    while Active:
        print("Welcome to the Broward Records Pull Program")
        print("Please select the type of records you would like to pull")
        print("1. Lis Pendens")
        print("2. Death Certificates")
        print("3. Probates")
        print("4. Property Tax Lien")
        print("5. Get Adderess From custom File (Folio)")
        print("6. Exit the Program")
        UserInput = input("Please enter the number of the records you would like to pull: ")
        if UserInput == "1":
            StartDate, EndDate = SetDates.GetDates()
            BrowardRecordsPull.Run("LP", "B-LP", StartDate, EndDate)
        elif UserInput == "2":
            StartDate, EndDate = SetDates.GetDates()
            BrowardRecordsPull.Run("DC", "B-DC", StartDate, EndDate)
        elif UserInput == "3":
            StartDate, EndDate = SetDates.GetDates()
            BrowardRecordsPull.Run("PRO", "B-PR", StartDate, EndDate)
        elif UserInput == "4":
            StartDate, EndDate = SetDates.GetDates()
            BrowardRecordsPull.Run("PALIE", "B-PT", StartDate, EndDate)
        elif UserInput == "5":
            filename = input("Enter filename: ")
            print('Fetching address from file',filename)
            fname = 'Input\\' + filename
            df = pd.read_csv(fname)
            print(df)
            df = getAddressFromFOLIOBroward(BrowardRecordsPull.InitDriver(),df)
            File = os.getcwd() +"\\output\\" +filename
            df.to_csv(File, index=False)
        elif UserInput == "6":
            Active = False
        else:
            print("Please enter a valid option")
    return 0

def BrowardRecordsPullAll(Start=None, End=None):
    print("Pulling all of the Broward Records")
    if Start is None and End is None:
        StartDate = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")
        EndDate = datetime.datetime.now().strftime("%m/%d/%Y")
    else:
        StartDate = Start
        EndDate = End
    try:
        BrowardRecordsPull.Run("LP", "B-LP", StartDate, EndDate)
    except:
        print("There was an error with the Lis Pendens")
        pass
    try:
        BrowardRecordsPull.Run("DC", "B-DC", StartDate, EndDate)
    except:
        print("There was an error with the Death Certificates")
        pass
    try:
        BrowardRecordsPull.Run("PRO", "B-PR", StartDate, EndDate)
    except:
        print("There was an error with the Probates")
        pass
    return 0

def MiamiDadePullAll(Start=None, End=None):
    print("Pulling all of the Miami Dade Records")
    if Start is None and End is None:
        StartDate = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")
        EndDate = datetime.datetime.now().strftime("%m/%d/%Y")
    else:
        StartDate = Start
        EndDate = End
    try:
        MiamiDadeRecordsPull.Run("DCE", StartDate, EndDate)
        # MiamiDadeRecordsPull.Run("DCE", StartDate, EndDate, "M-DC")
    except:
        print("There was an error with the Death Certificates")
        pass
    try:
        MiamiDadeRecordsPull.Run("PAD", StartDate, EndDate)

        # MiamiDadeRecordsPull.Run("PAD", StartDate, EndDate, "M-PR")
    except:
        print("There was an error with the Probates")
        pass
    try:
        MiamiDadeRecordsPull.ForeclosureSearch(MiamiDadeRecordsPull.InitDriver(), StartDate, EndDate)
    except:
        print("There was an error with the Foreclosures")
        pass
    try:
        TempSave = os.getcwd() + "\\MiamiDadeCVTemp.csv"
        df = MiamiDadeCVPull.Search(MiamiDadeCVPull.InitDriver(), StartDate, EndDate)
        df = MiamiDadeCVPull.GetPropertyInfo(MiamiDadeCVPull.InitDriver(), df)
        df.to_csv(TempSave, index=False)
        Taxdf = MiamiDadeTaxDel.SplitNames(TempSave, ColumnName="Name")
        os.remove(TempSave)
        TaxSave = os.getcwd() + "\\MiamiDadeCV-" + StartDate.replace("/", "-") + "-" + EndDate.replace("/", "-") + ".csv"
        Taxdf.to_csv(TaxSave, index=False)
    except:
        print("There was an error with the Code Violations")
        pass
    return 0


# Create a schedule for the program to run
# This will not run on windows since it implements cron
def APS():
    print("Starting Scheduled runs for the Bot")
    while True:
        sched = BlockingScheduler()
        sched.add_job(BrowardRecordsPullAll, 'cron', hour=2, minute=0)
        sched.add_job(MiamiDadePullAll, 'cron', hour=4, minute=0)
        sched.start()

if __name__ == "__main__":
    CountyMenu()