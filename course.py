from preqparser import PreqParser
from bs4 import BeautifulSoup
import requests
import re

class Course:
    def __init__(self, subj: str, crse: str, term:str ='202520') -> None:
        self.subj = subj
        self.crse = crse
        self.term = term

        response = requests.post(url='https://banner9.rowan.edu/ords/ssb/bwckctlg.p_disp_course_detail',
                  data= {'cat_term_in': term,
                         'subj_code_in': subj,
                         'crse_numb_in': crse})

        assert (response.status_code == 200), f"error: {response.status_code}, unable to find course"

        self.soup = BeautifulSoup(response.text, features="html.parser")
        
        self.preqs = self._extract_preqs()
        self.title = self._extract_title()
        self.desc = self._extract_desc()
        self.credits = self._extract_credits()

    def _extract_preqs(self) -> PreqParser:
        """
            extracts prerequisites from Rowan's detailed course information website
            
            Args:
                soup: BeautifulSoup of Rowan course information HTML
            Returns:
                preqs: Preq parser
        """
        preq_head = self.soup.find('span', 'fieldlabeltext', string=re.compile('Prerequisites', re.IGNORECASE))
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

        return PreqParser(''.join(res))

    def _extract_desc(self) -> str:
        _found = self.soup.find('td', 'ntdefault')
        if not _found:
            return None
        _found = _found.findNext(string=True)
        if not _found or _found == '\n':
            return None
        return _found
    def _extract_title(self) -> str:
        _found = self.soup.find('td', 'nttitle')
        if not _found:
            return None
        return _found.string

    def _extract_credits(soup) -> str:
        # ensures it is credits
        _match = re.search(r'(\d{1}\.\d{,4}) (Credit)', soup.text)
        if _match:
            return _match.group(1)
        return None
