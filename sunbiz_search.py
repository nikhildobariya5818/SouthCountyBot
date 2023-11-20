# Series of task to be done for searching on sunbiz

# 1. If name contains word related to organization, search on sunbiz
# 2. Go to url of sunbiz for search
# 3. Choose correct search result url and go there
# 3. Get Registered Name, Authorized or Director Name on search result
# 4. If name contains word related to organization, Start from 1
# 5. Else scrap fullname, mailing address, property address, address 1, address 2, City, Country, State, Zip

import re
import json
import requests
from time import sleep
from random import randint
from bs4 import BeautifulSoup
from keywords import COMPANY_KEYWORDS

class SunbizSearch:

    SUNBIZ_BASE_SEARCH_URL = "http://search.sunbiz.org"
    SUNBIZ_ENTITY_SEARCH_URL = SUNBIZ_BASE_SEARCH_URL+"/Inquiry/CorporationSearch/SearchResults/EntityName/{0}/Page1?searchNameOrder={0}"
    PARSER = "html.parser"
    KEYWORDS = COMPANY_KEYWORDS

    def __init__(self, company_name):
        self.company_name = company_name
        self.previous_company_name = None
        self.owners_list = []
        self.company_detail_link = None
        self.company_found = False

    @staticmethod
    def _make_clean_address(address):
        address_clean_and_split = {
                "full_address": "",
                "mailing_address": "",
                "address_1": "",
                "address_2": "",
                "city": "",
                "country": "",
                "state": "",
                "zip_code": "",
                "zip4":"",
            }
        clean_address = address.strip().replace("\r\n","")
        if "\n" in address:
            addresses = address.split("\n")
            addresses = list(filter(lambda addr: addr, map(lambda address: address.replace("\r", "").replace("\n", "").strip(), addresses)))
        else:
            addresses = address.split("  ")
            addresses = list(filter(lambda address: address, addresses))
        for index, address in enumerate(addresses, 1):
            address_clean_and_split["full_address"] = " ".join(clean_address.split())
            if len(addresses) == index:
                try:
                    if "," in address:
                        city, state_and_zipcode = address.split(",")
                        state, zipcode = state_and_zipcode.strip().split(" ", 1)
                        address_clean_and_split["city"] = city
                        address_clean_and_split["state"] = state
                        address_clean_and_split["zip_code"] = zipcode
                    else:
                        city, zip_code, state = address.split(" ")
                        address_clean_and_split["city"] = city
                        address_clean_and_split["state"] = state
                        address_clean_and_split["zip_code"] = zip_code
                except Exception:
                    pass
            else:
                address_clean_and_split[f"address_{index}"] = address
                address_clean_and_split["mailing_address"] += address
        return address_clean_and_split
        # return " ".join(address.split())


    @staticmethod
    def _confirm_response(search_url):
        """
            It will attempt to make requests for 5 times.
            If response is ok within 5 times then will return response.
        """
        count = 1
        while count <= 5:
            try:
                response = requests.get(search_url)
            except requests.exceptions.ConnectionError:
                print(f"Connection error with sunbiz...\n Trying again...")
                sleep(5)
            else:
                if response.status_code == 200:
                    return response
                else:
                    sleep(randint(1, 5))
                    count += 1

    def _get_category_content(self, category):
        categories = category.find_all("span")
        if categories[1].text != "NONE":
            return category.find_all("span")

    def _make_entity_search_url(self):
        return self.SUNBIZ_ENTITY_SEARCH_URL.format(self.company_name)

    def _make_entity_detail_search_url(self):
        return self.SUNBIZ_BASE_SEARCH_URL+self.company_detail_link

    def _extract_category_one_data(self, category_one):
        if self._get_category_content(category_one):
            category_one_text = category_one.find_all("span")
            category_one_title, category_one_name, category_one_address = "", "", ""
            try:
                category_one_title = category_one_text[0].text
                category_one_name = category_one_text[1].text
                category_one_address = category_one_text[2].text
            except IndexError:
                pass
            temp = {"title":None}
            category_one_address = self._make_clean_address(category_one_address)
            temp["category_title"] = category_one_title.strip()
            temp["name"] = category_one_name.strip()
            temp.update(category_one_address)
            self.owners_list.append(temp)

    def _extract_category_two_data(self, category_two):
        if self._get_category_content(category_two):
            category_two = map(lambda detail: re.sub(r"<br\s?\/>", "", str(detail)), category_two)
            category_two = map(lambda detail: re.sub(r"<b>", "", detail), category_two)
            category_two = list(filter(str,map(lambda detail: re.sub(r"\r?\n", "", detail), category_two)))

            category_two_title = BeautifulSoup(category_two.pop(0), self.PARSER)
            category_two = category_two[1:]
            count = 1
            temp = {"category_title": category_two_title.text}
            for category in category_two:
                cat = BeautifulSoup(category, self.PARSER)
                if count == 1:
                    temp["title"] = cat.text.strip().replace(u"Title\xa0", u"")
                    count += 1
                    continue
                if count == 2:
                    temp["name"] = cat.text.strip()
                    count += 1
                    continue
                if count == 3:
                    temp.update(self._make_clean_address(cat.text))
                    count = 1
                self.owners_list.append(temp)
                temp = {"category_title": category_two_title.text}


    def _parse_entity_search_result(self):
        entity_search_url = self._make_entity_search_url()
        response = self._confirm_response(entity_search_url)
        if response:
            bs = BeautifulSoup(response.text, self.PARSER)
            search_result = bs.find("div", attrs={"id": "search-results"})
            table_data = search_result.find("table")
            trs = table_data.find_all("tr")
            data_tr = trs[1:]
            text = ""
            for index, tr in enumerate(data_tr):
                REMOVE_KEYWORDS = ("THE ", )
                td = tr.find("td", attrs={"class": "large-width"})
                anchor = td.find("a", href=True)
                link = anchor["href"]
                text = anchor.text
                text = text.lower().replace(",", "").replace(".", "").strip()
                for keyword in REMOVE_KEYWORDS:
                    text = text.replace(keyword.lower(), "")
                text = re.sub("[^a-zA-Z.\d\s]", " ", text)
                splitted_text = text.split(" ")
                splitted_company_name = self.company_name.replace(",", " ").replace(".", " ").strip().split(" ")
                company_name_found = f"{splitted_text[0]} {splitted_text[-1]}"
                original_company_name = f"{splitted_company_name[0]} {splitted_company_name[-1]}"
                if original_company_name.lower().strip() in company_name_found.lower().strip():
                    self.company_found = True
                    return link

    def _parse_entity_detail_result(self):
        self.company_detail_link = self._parse_entity_search_result()
        if self.company_found:
            entity_detail_search_url = self._make_entity_detail_search_url()
            response = self._confirm_response(entity_detail_search_url)
            if response:
                search_result = BeautifulSoup(response.text, self.PARSER)
                detail_sections = search_result.find_all("div", attrs={"class": "detailSection"})
                try:
                    detail_sections = detail_sections[4:-2]

                    category_one, category_two= detail_sections[0], detail_sections[1]
                    self._extract_category_one_data(category_one)
                    self._extract_category_two_data(category_two)
                    return True
                except IndexError:
                    return False

    def _finalize_owners_list(self):
        owners_list = self.owners_list.copy()
        final_owners_list = []
        for index, owner in enumerate(owners_list):
            if any(map(lambda keyword, owner=owner: keyword in owner.get("name").upper(), SunbizSearch.KEYWORDS)):
                print(f"Found 1 more company. Searching again...")
                sunbiz_search = SunbizSearch(owner.get("name"))
                sunbiz_search.previous_company_name = self.company_name
                if self.previous_company_name:
                    new_owner_name = owner.get("name").replace(",", "").replace(".", "").strip()
                    previous_owner_name = self.previous_company_name.replace(",", "").replace(".", "").strip()
                    if new_owner_name == previous_owner_name:
                        owners_list.remove(owner)
                        continue
                final_owners_list.extend(sunbiz_search.get_owners_info())
            else:
                final_owners_list.extend(owners_list)
        return final_owners_list

    def get_owners_info(self):
        if self._parse_entity_detail_result():
            owners_list = self._finalize_owners_list()
            return owners_list
        else:
            return []

if __name__ == "__main__":
    # COMPANY_NAME = "KALLER ONE RETAIL LLC".lower()
    # COMPANY_NAME = "FAVA RESIDENTIAL, LLC".replace(",", "").lower()
    # COMPANY_NAME = "SCULLY QUIET WATERS LLC".replace(",", "").lower()
    # COMPANY_NAME = "CROWN DIVERSIFIED IND CORP".replace(",", "").lower()
    # COMPANY_NAME = "KNICKERBOCKER PROPERTIES INC".lower()
    # COMPANY_NAME = "HAIG & HAIG CONTR INC".lower()
    # COMPANY_NAME = "L7F CORP".lower()
    COMPANY_NAME = "GNA 1 LLC".lower()

    s = SunbizSearch(COMPANY_NAME)
    s.get_owners_info()
    # print(json.dumps())