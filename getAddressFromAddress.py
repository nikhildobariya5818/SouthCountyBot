import pandas as pd
import json
from MiamidadeSearch import getFolioNumberByAddress,PropertyInformation,getZoning 
import numpy as np
import os
from FolioConverter import FolioForMiami

# for filename in ["Open Unsafe Structure Cases.xlsm - District 1.csv",'Open Unsafe Structure Cases.xlsm - Open Unsafe Structure Cases.csv']:
def getAddressFromAddress(filename): 
    print('Fetching address from file',filename)

    fname = 'Input\\' + filename
    print(fname)
    df = pd.read_csv(fname, converters={'Folio': str})

    print(filename)
     

    if 'Organization Name' in df.columns:
        df = df.drop('Organization Name',axis=1)
    df.insert(loc=1, column='Organization Name', value='')
    if 'Legal description' in df.columns:
        df = df.drop('Legal description',axis=1)
    df.insert(loc=1, column='Legal description', value='')
    if 'of units' in df.columns:
        df = df.drop('of units',axis=1)
    df.insert(loc=1, column='Number of units', value='')
    if 'Year' in df.columns:
        df = df.drop('Year',axis=1)
    df.insert(loc=1, column='Year', value='')
    if 'Sqft' in df.columns:
        df = df.drop('Sqft',axis=1)
    df.insert(loc=1, column='Sqft', value='')
    if 'Bathrooms' in df.columns:
        df = df.drop('Bathrooms',axis=1)
    df.insert(loc=1, column='Bathrooms', value='')
    if 'Bedrooms' in df.columns:
        df = df.drop('Bedrooms',axis=1)
    df.insert(loc=1, column='Bedrooms', value='')
    if 'Land Use' in df.columns:
        df = df.drop('Land Use',axis=1)
    df.insert(loc=1, column='Land Use', value='')
    if 'Land zoning' in df.columns:
        df = df.drop('Land zoning',axis=1)
    df.insert(loc=1, column='Land zoning', value='')
    if 'Mailing Zip' in df.columns:
        df = df.drop('Mailing Zip',axis=1)
    df.insert(loc=1, column='Mailing Zip', value='')
    if 'Mailing State' in df.columns:
        df = df.drop('Mailing State',axis=1)
    df.insert(loc=1, column='Mailing State', value='')
    if 'Mailing City' in df.columns:
        df = df.drop('Mailing City',axis=1)
    df.insert(loc=1, column='Mailing City', value='')
    if 'Mailing Address' in df.columns:
        df = df.drop('Mailing Address',axis=1)
    df.insert(loc=1, column='Mailing Address', value='')
    if 'Property Zip' in df.columns:
        df = df.drop('Property Zip',axis=1)
    df.insert(loc=1, column='Property Zip', value='')
    if 'Property State' in df.columns:
        df = df.drop('Property State',axis=1)
    df.insert(loc=1, column='Property State', value='')
    if 'Property City' in df.columns:
        df = df.drop('Property City',axis=1)
    df.insert(loc=1, column='Property City', value='')
    if 'Property Address' in df.columns:
        df = df.drop('Property Address',axis=1)
    df.insert(loc=1, column='Property Address', value='')
    if 'Middle Name' in df.columns:
        df = df.drop('Middle Name',axis=1)
    df.insert(loc=1, column='Middle Name', value='')
    if 'Last Name' in df.columns:
        df = df.drop('Last Name',axis=1)
    df.insert(loc=1, column='Last Name', value='')
    if 'First Name' in df.columns:
        df = df.drop('First Name',axis=1)
    df.insert(loc=1, column='First Name', value='')
    df.insert(loc=1, column='APN', value='')

    df["Property State"] = "FL"


    for index, row in df.iterrows():
        print('*'*50)
        # print(index,str(row["Folio"]))

        name = row["Address"]
        print('Fetching address for name',name)
        # return
        try:

            Folio = getFolioNumberByAddress(name)
                
            if int(Folio) <1:
                raise ValueError() 
            data = PropertyInformation(Folio).get_parsed_info()[0]
            try:

                df.loc[index, "APN"] = FolioForMiami(str(Folio))
            except:
                print('Error while conveting Folio')
                df.loc[index, "APN"] = Folio
                
            df.loc[index, "First Name"] = data["first_name"]
            df.loc[index, "Last Name"] = data["last_name"]
            df.loc[index, "Middle Name"] = data["middle_name"]

            df.loc[index, "Property City"] = data["property_address_city"]
            df.loc[index, "Property Zip"] = data["property_address_zip"]

            print(data["property_address"])
            if data["property_address"] == "":
                data["property_address"] = Folio
                df.loc[index, "Property City"] = data["city"]
                df.loc[index, "Property Zip"] = data["zip_code"]
            else:
                df.loc[index, "Property Address"] = data["property_address"]
            
            df.loc[index, "Mailing Address"] = data["mailing_address"]
            df.loc[index, "Mailing City"] = data["city"]
            df.loc[index, "Mailing State"] = data["state"]
            df.loc[index, "Mailing Zip"] = data["zip_code"]
            df.loc[index, "Land Use"] = data["primary_land_use"]
            df.loc[index, "Bedrooms"] = data["bedroom_count"]
            df.loc[index, "Bathrooms"] = data["bathroom_count"]
            df.loc[index, "Sqft"] = data["building_actual_area"]
            df.loc[index, "Year"] = data["year_built"]
            df.loc[index, "Number of units"] = data["living_units"]
            df.loc[index, "Legal description"] = data["legal_description"]
            df.loc[index,"Organization Name"] = data["owner_name"]

            if data["parent_folio"] != '':
                Folio = data["parent_folio"]
            try:
                zone = getZoning(Folio)
                df.loc[index, "Land zoning"] = zone 
            except Exception as e:
                df.loc[index, "Land Use"] = np.nan
                print(e)
                print('Error in Zoning')
        except:
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

    for index, row in df.iterrows():
        try:
            if "UNINCORPORATED".lower() in row["Property City"].lower():
                df.loc[index, "Property City"] = "Miami"
        except:
            df.loc[index, "Property City"] = "Miami"
            
    File = os.getcwd() +"\\output\\" +filename
    df.to_csv(File, index=False)