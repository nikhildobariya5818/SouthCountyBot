import requests
import json
from bs4 import BeautifulSoup
from CREATE_COOKIES import CREATE_COOKIES 

class CREATEDATE:
    def __init__(self) :

        cookies_data = CREATE_COOKIES()
        self.cookies = cookies_data.cookie()
        days_to_process = [9208, 8045]
        for day in days_to_process:
            cookies_data.process_day(day,self.cookies)

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
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }

    def get_date(self):
        date = input("Enter The Month (YYYY-MM-DD) : ")
        print(date)
        params = {
            'ZACTION': 'USER',
            'ZMETHOD': 'CALENDAR',
        'selCalDate':"{ts '"+str(date)+" 00:00:00'}"
        }
        response = requests.get('https://www.miamidade.realforeclose.com/index.cfm', params=params, cookies=self.cookies, headers=self.headers)
        data_id =[]
        soup = BeautifulSoup(response.content, 'lxml')
        calboxes = soup.find_all('div', {'class':'CALBOX'})
        for calbox in calboxes:
            dayid = calbox.get('dayid')
            if dayid:
                data_id.append(dayid)
                
        return data_id
    
    def get_id(self):
        ids = []
        datas = self.get_date()
        for da in datas:

            print('Getting Listings for date :- ',da)

            response = requests.get(
                'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE='+str(da),
                cookies=self.cookies,
                headers=self.headers,
            )
            params = {
                'zaction': 'AUCTION',
                'Zmethod': 'UPDATE',
                'FNC': 'LOAD',
                'AREA': '',
                'PageDir': '0',
                'doR': '0',
                'dir':'1',
                'bypassPage': '0',
                'test': '1',
            }
            
            area = ['R','C','W']
            area = ['C']
            for r in area:
                params['AREA'] = r
                response = requests.get('https://www.miamidade.realforeclose.com/index.cfm', params=params, cookies=self.cookies, headers=self.headers)
                data = json.loads(response.content)
                rlist = data.get('rlist', '')
                rlist_ids = rlist.split(',')
                ids.extend(rlist_ids)
                previous_len = None
                while True:
                    current_len = len(set(ids))
                    # print(current_len)
                    if current_len == previous_len:
                        break 
                    previous_len = current_len
                    params['PageDir'] ='1'
                    response = requests.get('https://www.miamidade.realforeclose.com/index.cfm', params=params, cookies=self.cookies, headers=self.headers)
                    data = json.loads(response.content)
                    rlist = data.get('rlist', '')
                    rlist_ids = rlist.split(',')
                    # print(rlist_ids)
                    ids.extend(rlist_ids)
         
        return list(set(ids))

if __name__ == "__main__":
    obj = CREATEDATE()
    print(obj.get_id())