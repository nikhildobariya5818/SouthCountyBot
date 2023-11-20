import os
import csv
import sys
import json
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from sunbiz_search import SunbizSearch
from clean_name import CleanName
from keywords import COMPANY_KEYWORDS as KEYWORDS


def get_input_file() -> str:
    '''Get file to parse from args or file dropped on Python script'''
    input_file_name = None
    try:
        input_file_name = sys.argv[1]
    except IndexError:
        print('No dropped file found, trying to search in arguments..')
        if not input_file_name:
            print('No file found to parse, quit.')
    return input_file_name


def get_clean_name(owner_name):
    clean_name = CleanName(owner_name)
    cleaner_names = clean_name.get_cleaned_name()
    return cleaner_names


def clean_company_owners_name(owners, owner_name):
    owners_list = []
    owners = {frozenset(item.items()): item for item in owners}.values()
    for owner in owners:
        if not any(map(lambda keyword, owner=owner: keyword in owner.get("name").upper(), KEYWORDS)):
            cleaner_names = get_clean_name(owner.get("name"))
            owner.pop("name")
            [obj.update({"owner_name": owner_name}) for obj in cleaner_names]
            for obj in cleaner_names:
                obj.update(owner)
                owners_list.append(obj)
    return owners_list


def search_owners_from_sunbiz(owner_name):
    owners_list = []
    # Assuming KEYWORDS is a list of keywords to filter out certain names
    if not any(keyword.upper() in owner_name.upper() for keyword in KEYWORDS):
        cleaner_names = get_clean_name(owner_name)
        temp = {
            "title": None,
            "category_title": None,
            "full_address": None,
            "mailing_address": None,
            "address_1": None,
            "address_2": None,
            "city": None,
            "country": None,
            "state": None,
            "zip_code": None,
            "zip4": None
        }
        owners_list.extend({**obj, **temp} for obj in cleaner_names)
    else:
        sunbiz_search = SunbizSearch(owner_name)
        owners = sunbiz_search.get_owners_info()
        if owners:
            owners_list = clean_company_owners_name(owners, owner_name)
        else:
            obj = {
                "owner_name": owner_name,
                "full_name": None,
                "first_name": None,
                "middle_name": None,
                "last_name": None,
                "suffix_name": None,
                "title": None,
                "category_title": None,
                "full_address": None,
                "mailing_address": None,
                "address_1": None,
                "address_2": None,
                "city": None,
                "country": None,
                "state": None,
                "zip_code": None,
                "zip4": None
            }
            owners_list.append(obj)
    return owners_list


def customer_folio(df):
    matching_owners = df[df['Owner'].notnull()]
    datas = []
    for owner in matching_owners['Owner']:
        datas.extend(search_owners_from_sunbiz(owner))
    df = pd.DataFrame(datas)
    df.rename(columns={
        # 'owner_name':'Owner Name',
        # 'full_name': 'Full Name',
        'first_name': 'First Name',
        #    'middle_name':'Middle Name',
        'last_name': 'Last Name',
        #    'suffix_name':'Suffix Name',
        #    'title':'Title',
        # 'category_title':'Category Title',
        # 'full_address':'Full Address',
        'mailing_address': 'Mailing address',
        # 'address_1':'address 1',
        # 'address_2':'address_2',
        'city': 'Mailing city',
        'country': 'Mailing county',
        'state': 'Mailing state',
        'zip_code': 'Mailing zip',
                    'zip4': 'Mailing zip4'
    }, inplace=True)
    print(df)
    return df


if __name__ == "__main__":
    # owners_list = search_owners_from_sunbiz('HAROLD, BAMBERG')
    # print(owners_list)
    data = customer_folio()
    # FILE_NAME = get_input_file()
    # ext = os.path.splitext(FILE_NAME)[1]
    # if ext == ".csv":
    #     df_read = pd.read_csv(FILE_NAME)
    # elif ext == ".xlsx" or ext == ".xls":
    #     df_read = pd.read_excel(FILE_NAME, engine="openpyxl")
    # else:
    #     print("Please drop either csv or excel files.")
    #     sys.exit()
    # _time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    # _split = FILE_NAME.split('.')[0]
    # output_file_name = f"{_split}_{_time}.csv"
    # owners_list = []
    # write_header = True
    # mode = "w"
    # COLUMN_NAME = "Owner"
    # owners = df_read.get(COLUMN_NAME).to_list()
    # print(f"Found {len(owners)} owners name.")
    # for index, row in tqdm(df_read.iterrows(), total=df_read.shape[0], desc="Searching..."):
    #     owner_name = row.get(COLUMN_NAME)
    #     if owner_name:
    #         owners_list = search_owners_from_sunbiz(owner_name)
    #         [owner.update(row) for owner in owners_list]
    #         [owner.pop(COLUMN_NAME) for owner in owners_list]
    #         df = pd.DataFrame.from_dict(owners_list)
    #         df.to_csv(output_file_name, index=False, mode=mode, header=write_header)
    #         mode = "a"
    #         write_header = False
