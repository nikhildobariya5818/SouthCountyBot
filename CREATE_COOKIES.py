import requests
from http.cookies import SimpleCookie


class CREATE_COOKIES:
    def __init__(self):
        self.cookies = {}
        self.base_url = 'https://www.miamidade.realforeclose.com/index.cfm'
        self.headers = {
            'authority': 'www.miamidade.realforeclose.com',
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
    def _post_request(self, data,cookies):
        response = requests.post(self.base_url,cookies=cookies, data=data, headers=self.headers)
        return response
    
    def login(self, username, userpass):
        data = {
            'zaction': 'ajax',
            'zmethod': 'login', 
            'process': 'login',
            'username': username,
            'userpass': userpass
        }
        # response = self._post_request(data)
        response = requests.post(self.base_url,data=data, headers=self.headers)
        return response.cookies
    
    def process_day(self, day,cookies):
        data_ok = {
            "zaction":"AJAX",
            "zmethod":"COM",
            "process":"NOTICE",
            "func":"ACCEPT",
            "showjson":"false",
            "NID": str(day),
        }
        response = self._post_request(data_ok,cookies)
        return response
    
    def cookie(self):
        username = 'arahanad'
        userpass = 'ankur123'
        cookies = self.login(username, userpass)
        simple_cookie = SimpleCookie()
        for name, value in cookies.items():
            simple_cookie[name] = value
        awsalbcors_cookie = simple_cookie.get("AWSALBCORS")
        awsalb_cookie = simple_cookie.get("AWSALB")
        cfid_cookie = simple_cookie.get("cfid")
    
        if awsalbcors_cookie:
            self.cookies["AWSALBCORS"] = awsalbcors_cookie.value

        if awsalb_cookie:
            self.cookies["AWSALB"] = awsalb_cookie.value

        if cfid_cookie:
            self.cookies["cfid"] = cfid_cookie.value
        self.cookies['cftoken'] ='0'
        self.cookies['testcookiesenabled'] = 'enabled'
        
        return self.cookies
    

if __name__ == "__main__":
    scraper = CREATE_COOKIES()
    # get cookies
    login_response = scraper.cookie()
    # Process Days
    # days_to_process = [9208, 8045]
    # for day in days_to_process:
    #     process_response = scraper.process_day(day)

