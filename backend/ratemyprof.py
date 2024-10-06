from tqdm.auto import tqdm
import requests
import json
import math
import re
import os

# https://github.com/Rodantny/Rate-My-Professor-Scraper-and-Search/tree/master

class RateMyProfScraper:
    def __init__(self, schoolid=822, profs_json: str="profs.json", force_download=False):
        # Rowan University: 822
        self.schoolid = schoolid
        self.profs_json = profs_json

        if not force_download:
            if not os.path.exists('proflist.json'):
                self.professors = self.download()
            else:
                self.professors = json.load(open(profs_json))
                # ensure that saved data is of correct school
                if self.professors[0]['tSid'] != str(schoolid):
                    self.professors = self.download()
        else:
            self.professors = self.download()

    def download(self):
        """creates List object that include basic information on all Professors from the IDed University
        """
        profList = []
        n_profs = self.api(1)['searchResultsTotal'] # count the profs
        n_pages = math.ceil(n_profs / 20)
        for p in tqdm(range(1, n_pages + 1)):
            _res = self.api(p)
            profList.extend(_res['professors'])

        # save as json file to prevent rerunning
        with open(self.profs_json, 'w') as f:
            json.dump(profList, f)

        return profList

    def _compare_names(self, name1: str, name2: str) -> bool:
        pattern = r'\b\w+\b'
        name1 = set(re.findall(pattern, name1.upper()))
        name2 = set(re.findall(pattern, name2.upper()))

        return len(name1.intersection(name2)) > 1

    def find_prof(self, name: str) -> int:
        for i in range(len(self.professors)):
            cur_prof = self.professors[i]
            cur_name = f"{cur_prof['tFname']} {cur_prof['tMiddlename']} {cur_prof['tLname']}"

            if self._compare_names(name, cur_name):
                return self.professors[i]
        return False

    def api(self, page: int):
        res = requests.get(f"https://www.ratemyprofessors.com/filter/professor/?page={str(page)}&queryoption=TEACHER&queryBy=schoolId&sid={str(self.schoolid)}")
        assert (res.status_code == 200), f"error: {res.status_code}"
        return json.loads(res.content)