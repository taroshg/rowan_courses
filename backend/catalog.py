from backend.sectiontally import SectionTally
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import requests
import json
import re
import os


class Catalog():
    """Downloads the rowan catalog by scraping every course info
    Args:
        section_tally: downloaded section_tally with selected term
    """
    def __init__(self, tally: SectionTally, catalog_json='catalog.json', force_download=False):
        self.term = tally.term
        self.tally = tally
        self.catalog_json = catalog_json
    
        self.courses = self.get_all_courses()

        if not force_download:
            if os.path.exists(self.catalog_json):
                self.data = json.load(open(self.catalog_json))
            else:
                self.data = self.download()
        else:
            self.data = self.download()

    def get_all_courses(self):
        subjs = self.tally.df['Subj'].unique()
        courses = {}
        for subj in subjs:
            courses[subj] = self.tally.df[self.tally.df['Subj'] == subj]['Crse'].unique()
        return courses

    def download(self):
        catalog = {}
        for subj in tqdm(self.courses):
            for crse in self.courses[subj]:
                response = requests.post(url='https://banner9.rowan.edu/ords/ssb/bwckctlg.p_disp_course_detail',
                    data= {'cat_term_in': self.term,
                            'subj_code_in': subj,
                            'crse_numb_in': crse})

                assert (response.status_code == 200), f"error: {response.status_code}, unable to find course"

                soup = BeautifulSoup(response.content, features="lxml")

                catalog[f'{subj} {crse}'] = {
                    "subj": subj,
                    "crse": crse,
                    "title": self.extract_title(soup),
                    "desc": self.extract_desc(soup),
                    "preqs": self.extract_preqs(soup),
                    "creds": self.extract_credits(soup),
                }
        

        with open(self.catalog_json, 'w') as f:
            json.dump(catalog, f)

        return catalog

    def extract_preqs(self, soup) -> str:
            """
                extracts prerequisites from Rowan's detailed course information website
                
                Args:
                    soup: BeautifulSoup of Rowan course information HTML
                Returns:
                    preqs: string
            """
            preq_head = soup.find('span', 'fieldlabeltext', string=re.compile('Prerequisites', re.IGNORECASE))
            if preq_head == None:
                return None

            assert (preq_head.next_siblings != None), "nothing found after 'Prerequisites: '"
                
            res = []
            prev_tag = ''
            for sibling in preq_head.next_siblings:
                if sibling == '\n':
                    continue

                if (sibling.name == 'br') and (prev_tag == 'br'):
                    break

                prev_tag = sibling.name

                s = sibling.string
                if s != None:
                    res.append(s)

            return ''.join(res)

    def extract_desc(self, soup) -> str:
        _found = soup.find('td', 'ntdefault')
        if not _found:
            return None
        _found = _found.findNext(string=True)
        if not _found or _found == '\n':
            return None
        return _found
    def extract_title(self, soup) -> str:
        _found = soup.find('td', 'nttitle')
        if not _found:
            return None
        return _found.string

    def extract_credits(self, soup) -> str:
        # ensures it is credits
        _match = re.search(r'(\d{1}\.\d{,4}) (Credit)', soup.text)
        if _match:
            return _match.group(1)
        return None