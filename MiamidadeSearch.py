import re
import json
import requests
from clean_name import CleanName
from sunbiz_search import SunbizSearch
from keywords import COMPANY_KEYWORDS
from shapely.geometry import Polygon
from thefuzz import fuzz

OWNER_NAME_URL = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetOwners&clientAppName=PropertySearch&enPoint=&from=1&ownerName={}&to=200'
OWNER_NAME_BY_ADD_URL = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetAddress&clientAppName=PropertySearch&from=1&myAddress={}&myUnit=&to=200'
POLYGON_URL = 'https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/6/query?f=json&spatialRel=esriSpatialRelIntersects&where=FOLIO%3D%27{}%27'
ZONE_URL1 = 'https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/4/query'
ZONE_URL2 = 'https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/5/query'
ZONE_URL3 = 'https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/5/query'

# https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/6/query?f=json&spatialRel=esriSpatialRelIntersects&where=FOLIO%3D%273040050160530%27
# https://gisfs.miamidade.gov/mdarcgis/rest/services/MD_PA_PropertySearch/MapServer/6/query?f=json&spatialRel=esriSpatialRelIntersects&where=FOLIO%3D%273040050160001%27
def getZoning(folio):
    search_url = POLYGON_URL.format(folio)
    # print(search_url)
    while True:
            try:
                response  = requests.get(search_url)
                # print(json.dumps(response.json()))
                polygon = Polygon(response.json()['features'][0]['geometry']['rings'][0])
                center = polygon.centroid
            except json.decoder.JSONDecodeError:
                continue
            break
    while True:
    
        params = {
            'f': 'json',
            'geometry': '{"x":'+str(center.x)+',"y":'+str(center.y)+'}',
            'outFields': '*',
            'spatialRel': 'esriSpatialRelIntersects',
            'where': '1=1',
            'geometryType': 'esriGeometryPoint',
            'inSR': '102658',
            'outSR': '102658',
        }

        

        try:
            response = requests.get(
                ZONE_URL1,
                params=params,
            )

            print(response)

            if len(response.json()['features']) != 0:

                zone = response.json()['features'][0]['attributes']

                zone = zone['ZONE'] + '-'+ zone['ZONE_DESC'] 


            else:
                response = requests.get(
                ZONE_URL2,
                params=params,
            )

                print(response)

                zone = response.json()['features'][0]['attributes']
                zone = zone['ZONE'] + '-'+ zone['ZONEDESC'] 

            return zone
        except json.decoder.JSONDecodeError:
            continue
        break
    

def getFolioNumber(name,index=0):
    response = ""
    search_url = OWNER_NAME_URL.format(name)
    while True:
            try:
                response  = requests.get(search_url)
                if 'The remote server returned an error:' in str(response.content):
                    return 0
                response = response.json()
                if response["MinimumPropertyInfos"] is not None:
                    if len(response["MinimumPropertyInfos"]) == 1:
                        return  response["MinimumPropertyInfos"][0]["Strap"].replace('-','')
                    else:
                        return -1
                else:
                    return 0
            except json.decoder.JSONDecodeError:
                continue
            break
    
def getFolioNumberByAddress(name):
    search_url = OWNER_NAME_BY_ADD_URL.format(name)
    while True:
            try:
                response  = requests.get(search_url)
                if 'The remote server returned an error:' in str(response.content):
                    return 0
                
                response = response.json()
                if response["MinimumPropertyInfos"] is not None:
                    if len(response["MinimumPropertyInfos"]) == 1:
                        return  response["MinimumPropertyInfos"][0]["Strap"].replace('-','')
                       
                    else:
                        # print('xy')        
                        return -1
                else:            
                    return 0
            except json.decoder.JSONDecodeError:
                continue
            break

class PropertyInformation:

    KEYWORDS = COMPANY_KEYWORDS
    PROPERTY_SEARCH_URL = "https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetPropertySearchByFolio&clientAppName=PropertySearch&folioNumber={}"

    def __init__(self, folio):
        if len(folio) != 13:
            folio = '0' + folio
        self.folio = folio
        self.response = None
        self.property_data = {}
        self.property_address = {}
        self.mailing_address = {}
        self.sales_info = {}
        self.last_assessed_value = {}
        self.owners_list = []
        self.__parsed_result = []
        self.legal_description = ''
        self.organization = ''

    

    def _search_property(self):
        search_url = self.PROPERTY_SEARCH_URL.format(self.folio)
        while True:
            try:
                response  = requests.get(search_url)
                self.response = response.json()
            except json.decoder.JSONDecodeError:
                continue
            break

    def _parse_property_data(self):
        self._search_property()
        property_info = self.response.get("PropertyInfo")
        self.property_data["pa_primary_zone"] = f"{property_info.get('PrimaryZone', '')} {property_info.get('PrimaryZoneDescription', '')}"
        self.property_data["primary_land_use"] = f"{property_info.get('DORCode', '')} {property_info.get('DORDescription', '')}"
        self.property_data["living_area"] = property_info.get("BuildingHeatedArea", "")
        self.property_data["living_units"] = property_info.get("UnitCount", "")
        self.property_data["actual_area"] = property_info.get("BuildingActualArea", "")
        self.property_data["adjusted_area"] = property_info.get("BuildingEffectiveArea", "")
        self.property_data["lot_size"] = property_info.get("LotSize", "")
        self.property_data["year_built"] = property_info.get("YearBuilt", "")
        self.property_data["bedroom_count"] = property_info.get("BedroomCount", "")
        self.property_data["bathroom_count"] = property_info.get("BathroomCount", "")
        self.property_data["building_actual_area"] = property_info.get("BuildingActualArea", "")
        self.property_data["parent_folio"] = property_info.get("ParentFolio", "")

        legal_description = self.response.get("LegalDescription")
        self.legal_description = legal_description.get("Description", "")



    def _parse_property_address(self):
        site_address = self.response.get("SiteAddress")
        address = ""
        property_address = ""
        zip = ''
        city = ''
        if site_address:
            address = site_address[0].get("Address")
            zip = site_address[0].get("Zip")
            city = site_address[0].get("City")
        if "," in address:
            property_address = address.split(",")[0]
        self.property_address["property_address"] = property_address
        self.property_address["property_address_zip"] = zip
        self.property_address["property_address_city"] = city

    def _parse_mailing_and_zip_codes(self):
        mailing_address= self.response.get("MailingAddress")
        address_1 = mailing_address.get("Address1", "")
        address_2 = mailing_address.get("Address2", "")
        self.mailing_address["mailing_address"] = f"{address_1} {address_2}"
        self.mailing_address["address_1"] = address_1
        self.mailing_address["address_2"] = address_2
        self.mailing_address["city"] = mailing_address.get("City", "")
        self.mailing_address["country"] = mailing_address.get("Country", "")
        self.mailing_address["state"] = mailing_address.get("State", "")
        zip_code = mailing_address.get("ZipCode")
        zip4 = None
        if zip_code and "-" in zip_code:
            zip_, zip4 = zip_code.split("-", 1)
        else:
            zip_ = zip_code
        self.mailing_address["zip_code"] = zip_
        self.mailing_address["zip4"] = zip4

    def _parse_sales_info(self):
        sales_info = self.response.get("SalesInfos")
        sales_information = ""
        sales_information_date = ""
        for sales in sales_info:
            if sales.get("SalePrice") > 101:
                sales_information = sales.get("SalePrice")
                sales_information_date = sales.get("DateOfSale")
                break
        self.sales_info["sales_information"] = sales_information
        self.sales_info["sales_information_date"] = sales_information_date

    def _parse_last_assessed_value(self):
        assessment_value = self.response.get("Assessment", {}).get("AssessmentInfos", [])
        last_assessed_value = ""
        if assessment_value:
            last_assessed_value = assessment_value[0].get("AssessedValue", "")
        self.last_assessed_value["last_assessed_value"] = last_assessed_value

    @staticmethod
    def __get_clean_name(owner_name):
        clean_name = CleanName(owner_name)
        cleaner_names = clean_name.get_cleaned_name()
        return cleaner_names

    def clean_company_owners_name(self, owners, owner_name):
        owners_list = []
        owners = {frozenset(item.items()): item for item in owners}.values()
        for owner in owners:
            if not any(map(lambda keyword, owner=owner: keyword in owner.get("name").upper(), PropertyInformation.KEYWORDS)):
                cleaner_names = self.__get_clean_name(owner.get("name"))
                owner.pop("name")
                [obj.update({"owner_name": owner_name}) for obj in cleaner_names]
                for obj in cleaner_names:
                    obj.update(owner)
                    owners_list.append(obj)
        return owners_list

    def _parse_owner_info(self):
        owners = self.response.get("OwnerInfos")
        # Owner Name, Full Name, First Name, Middle Name, Last Name, Suffix Name
        # if owner info contains organization name, then search into sunbiz for owner info
        self.owners_list = []
        for owner in owners:
            owner_name = owner.get("Name")
            if any(map(lambda keyword, owner_name = owner_name: keyword in owner_name, self.KEYWORDS)):
                # remove special character
                owner_name = re.sub("[^a-zA-Z.\d\s]", "", owner_name)
                sunbiz = SunbizSearch(owner_name)
                owners = sunbiz.get_owners_info()
                # print(owner)
                for data in owners:
                    data['sunbiz'] = True
                    
                # add extra field 'sunbiz' = True
                if owners:
                    self.owners_list = self.clean_company_owners_name(owners, owner_name)
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
                    }
                    self.owners_list.append(obj)
                    self.organization = owner_name
            else:
                cleaner_names = self.__get_clean_name(owner_name)
                for obj in cleaner_names:
                    obj["title"] = None
                    obj["category_title"] = None
                    obj["full_address"] = None
                    self.owners_list.append(obj)

    def _parse_info_in_order(self):
        self._parse_property_data()
        self._parse_property_address()
        self._parse_mailing_and_zip_codes()
        self._parse_sales_info()
        self._parse_last_assessed_value()
        self._parse_owner_info()

    def _construct_parsed_information(self):
        self._parse_info_in_order()
        owners = self.owners_list
        self.__parsed_result = []
        for owner in owners:
            temp = {"folio": self.folio}
            temp.update(owner)
            temp.update(self.mailing_address)
            temp.update(self.property_address)
            temp.update(self.property_data)
            temp.update(self.last_assessed_value)
            temp.update(self.sales_info)
            temp['legal_description'] = (self.legal_description)
            temp['organization'] = (self.organization)
            self.__parsed_result.append(temp)


    def get_parsed_info(self):
        self._construct_parsed_information()
        return self.__parsed_result

if __name__ == "__main__":
    # folio = getFolioNumberByAddress('1 MIAD BLDG #812')
    # print(folio)
    # folio = getFolioNumber("Derrald B Akins")
    # print(folio)




    folio = '01-0104-090-1110'.replace('-','')
    # print(folio)
    # zone =  (getZoning(folio))
    # print(zone)
    
    p = PropertyInformation(folio)
    # p._parse_owner_info()
    # p = PropertyInformation("3079310010096")
    x = (json.dumps(p.get_parsed_info()))
    print(x)
