import requests,json
from bs4 import BeautifulSoup
from CREATE_COOKIES import CREATE_COOKIES 
from CREATEDATE import CREATEDATE
import pandas as pd
import os
import numpy as np

from getAddressFromFOLIO import getAddressByFolio

datas = CREATEDATE()

class THEDATA:
    

    def loging(self):

        print('Creating new cookies')

        cookies_data = CREATE_COOKIES()
        self.cookies = cookies_data.cookie()
        days_to_process = [9208, 8045]
        for day in days_to_process:
            cookies_data.process_day(day,self.cookies)
    
    def __init__(self,filename) :


        self.cookies ={}

        # self.loging()

        self.filename = filename
        
        self.dataList = []

        self.headers = {
            'authority': 'www.miamidade.realforeclose.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }
    
    def get_data(self):
        ids = datas.get_id()
        count = 1

        self.loging()
        print('Processing Listings')
        for id in ids:
        # for id in ['1360849']:
            while True:
                try:
                    if id == '':
                        break
                        # continue
                    self.params = {
                        'zaction': 'auction',
                        'zmethod': 'details',
                        'AID': str(id),
                        'bypassPage': '1',
                    }
                    response = requests.get('https://www.miamidade.realforeclose.com/index.cfm', params=self.params, cookies=self.cookies, headers=self.headers,timeout=10)

                    print(count,id,response.status_code)

                    data ={}
                    data['id'] = id
                    soup = BeautifulSoup(response.content, "lxml") 
                    table = soup.find('table', {'class': 'bdTab'}).find_all('tr')
                    for row in table:
                        columns = row.find_all(['th', 'td'])
                        if len(columns) == 2:
                            key = columns[0].get_text(strip=True).replace(':', '')
                            value = columns[1].get_text(strip=True)
                            if key in data:
                                data[key].append(value)
                                print(key,value,'------------------------------',id)
                            else:
                                data[key] = value

                    data_table = soup.find('table', {'class': 'mgtt'}).find_all('tr')[1:]
                    for row in data_table:
                        columns = row.find_all('td')
                        if len(columns) == 2:
                            key = columns[0].get_text(strip=True)
                            value = columns[1].get_text(strip=True).strip()
                            if key in data:
                                data[key].append(value)
                            else:
                                data[key] = [value]
                    
                    params = {
                        'zaction': 'AUCTION',
                        'ZMETHOD': 'UPDATE',
                        'FNC': 'UPDATESINGLE',
                        'AID': str(id),
                    } 
                    
                    response = requests.get('https://www.miamidade.realforeclose.com/index.cfm', params=params, cookies=self.cookies, headers=self.headers,timeout=10)
                    response.raise_for_status()  # Check for HTTP error status
                    
                    content_json = json.loads(response.content)
                    adata = content_json.get('ADATA', {})
                    aitem_list = adata.get('AITEM', [])

                    if aitem_list:
                        data['status'] = aitem_list[0].get('B')
                        data['tmp'] = aitem_list

                        if 'sold' in str(response.content).lower():
                            data['status'] = 'Sold at ' + aitem_list[0].get('B')


                    # print(data)
                    del data['']
                    self.dataList.append(data)
                    count +=1
                    break
                except Exception as e:
                    self.loging()
                    print(e,id,response.content)

        
    def runSearch(self):

        df = pd.DataFrame(self.dataList)

        # df = pd.read_csv('Output\\August.csv',delimiter=',')

        df = df.fillna('') 

        df.insert(loc=1, column='Notes', value='')
    
        if 'status' in df.columns:
            df['Notes'] += 'status :- '+df['status'].astype(str) + '\n'
            df = df.drop('status',axis=1)

        if 'Assessed Value' in df.columns:
            df['Notes'] +=  'Assessed Value :- ' + df['Assessed Value'].astype(str) + '\n'
            df = df.drop('Assessed Value',axis=1)

        if 'Case Type' in df.columns:
            df['Notes'] += 'Case Type :- ' + df['Case Type'].astype(str) + '\n'
            df = df.drop('Case Type',axis=1)

        for column in df.columns:
            if column not in ['Parcel ID','Notes']:
                df['Notes'] += column + ' :- ' + df[column].astype(str) + '\n'
                df = df.drop(column,axis=1)


        df1 = getAddressByFolio(df[df["Parcel ID"] != ""][['Parcel ID','Notes']])

        df1.insert(1, 'Notes', df1.pop('Notes'))

        # for index, row in df.iterrows():


        if 'Unnamed: 0' in df.columns:
            df1.drop("Unnamed: 0", axis=1, inplace=True)

        df1.to_csv( 'Output/'+self.filename + '.csv', index=False)

if __name__ == "__main__":
    helper = THEDATA('xx')  
    helper.get_data()

    helper.runSearch()

