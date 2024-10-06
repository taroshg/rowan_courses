from datetime import datetime
from tqdm.auto import tqdm
from lxml import etree
import pandas as pd
import requests
import csv
import os

TERM_VALUE = ['40', '30', '20', '10']
TERM_NAME = ['fall', 'summer', 'spring', 'winter']

class SectionTally():
    def __init__(self, term:str, csv:str='tally.csv', force_download=False) -> None:
        self.term = self._get_term_code(term)

        if not force_download:
            if os.path.exists(csv):
                self.df = pd.read_csv(csv)
            else:
                self.df = self.download()
        else:
            self.df = self.download()

    def _get_term_code(self, term: str):
        """gets rowan term code, {year}{TERM_VALUE}
        Args:
            term: year and one of the following {fall, summer, spring, winter}
            ex. 2024 spring, 2025 summer ...
        """
        _split = term.split()
        assert len(_split) == 2, f"invalid term: got {_split}"
        term, year = _split
        assert len(year) == 4 and year.isalnum(), f"invalid term year: got {_split}"

        return f"{year}{TERM_VALUE[TERM_NAME.index(term.lower())]}"

    def download(self):
        response = requests.post(url='https://banner.rowan.edu/reports/reports.pl?task=Section_Tally',
                data= {"term": self.term,
                        "task": "Section_Tally",
                        "coll": "ALL",
                        "dept": "ALL",
                        "subj": "ALL",
                        "ptrm": "ALL",
                        "sess": "ALL",
                        "prof": "ALL",
                        "attr": "ALL",
                        "camp": "ALL",
                        "bldg": "ALL",
                        "Search": "Search",
                        "format": "excel"})
        assert(response.status_code == 200), response.status_code
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(response.content, parser=parser)

        # Open a CSV file for writing
        with open('tally.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Iterate through the XML tree and extract data
            for worksheet in root.findall('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):                
                for table in worksheet.findall('{urn:schemas-microsoft-com:office:spreadsheet}Table'):
                    for row in tqdm(table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row')):
                        row_data = [cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data').text for cell in row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell')]
                        csvwriter.writerow(row_data)

        return pd.read_csv('tally.csv')

