import requests
import logging
import sys

sys.path.insert(0,'./configuration')
from config import Config

#config file
config = Config()

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Qradar:
    
    def __init__(self) -> None:
        
        self._header = {
            'SEC': config.sec_token,
            'Version': '16.1',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._url = 'https://{}/api'.format(config.iploc_v4)
    
    def _url_(self, base_category:str = None, subase_category:str = None , detail:str = None) -> str:

        return self._url + base_category + subase_category + detail

    def _ariel_search_(self, query:str) -> dict:

        try:
            url = self._url + '/ariel/searches'
            response_searchid = requests.post(url, params={'query_expression': query}, headers=self._header, verify=False)
        except Exception as e:
            logging.log(logging.ERROR,f'{e}\nError in Qradar.py _ariel_seach_()')
        
        if response_searchid.status_code == 201:
            search_id = response_searchid.json()['search_id']
            url_api = f'{self._url}/ariel/searches/{search_id}'

            while True:
                response_status = requests.get(url_api, headers=self._header, verify=False)
                if response_status.json()['status'] == 'COMPLETED':
                    break

            url_api = f'{self._url}/ariel/searches/{search_id}/results'
            try:
                response_result = requests.get(url_api, headers=self._header, verify=False)
            
                #print(json.dumps(response_result.json(),indent=2))
                return response_result.json()['events']
            except Exception as e:
                logging.log(logging.ERROR,f'{e}\nError in Qradar.py _ariel_seach_()')
    
    def _search_(self, url:str=None, filter_param:str=None) -> dict:

        if filter_param:
            url_api = f'{self._url}{url}?filter='+filter_param
        else:
            url_api = f'{self._url}{url}'
        try:
            response = requests.get(url_api, headers=self._header, verify=False).json()
            return response
        except Exception as e:
                logging.error(f'{e}\nError in Qradar.py _search()')
                
        # with open("test.txt","w",encoding="utf-8") as file:
        #     file.write(json.dumps(offenses,indent=2))
        # file.close()
    
    def _get_offense_detail_(self, offenseid:str) -> list:

        url = f'/siem/offenses/{offenseid}'
        try:
            offense_detail = self._search_(url)
            return offense_detail
        except Exception as e:
            logging.log(logging.ERROR, f'{e}\nError in Qradar.py _get_offense_detail()')

    def _add_note_offense(self, offenseid:str, notetext:str) -> dict:

        url = f'{self._url}/siem/offenses/{offenseid}/notes?note_text={notetext}'
        try:
            response = requests.post(url,headers=self._header, verify=False)
            return response
        except Exception as e:
            logging.log(logging.ERROR, f'{e}\nError in Qradar.py _add_note_offense()')