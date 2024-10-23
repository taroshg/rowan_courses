from datetime import datetime
from tqdm.auto import tqdm
from lxml import etree
import pandas as pd
import requests
import csv
import os
import re

TERM_VALUE = ['40', '30', '20', '10']
TERM_NAME = ['fall', 'summer', 'spring', 'winter']

class SectionTally():
    def __init__(self, 
                 term:str='ALL', 
                 subj:str='ALL',
                 dept:str='ALL',
                 attr:str='ALL') -> None:
        self.term = term
        self.subj = subj
        self.dept = dept
        self.attr = attr

        self.df = self.download(self.term, self.subj, self.dept, self.attr)

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

    def download(self, term='ALL', subj='ALL', dept='ALL', attr='ALL'):
        response = requests.post(url='https://banner.rowan.edu/reports/reports.pl?task=Section_Tally',
                data= {"term": term,
                        "task": "Section_Tally",
                        "coll": "ALL",
                        "dept": dept,
                        "subj": subj,
                        "ptrm": "ALL",
                        "sess": "ALL",
                        "prof": "ALL",
                        "attr": attr,
                        "camp": "ALL",
                        "bldg": "ALL",
                        "Search": "Search",
                        "format": "excel"})
        assert(response.status_code == 200), response.status_code
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(response.content, parser=parser)

        # Open a CSV file for writing
        data = []
        # Iterate through the XML tree and extract data
        for worksheet in root.findall('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):                
            for table in worksheet.findall('{urn:schemas-microsoft-com:office:spreadsheet}Table'):
                for row in tqdm(table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row')):
                    row_data = [cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data').text for cell in row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell')]
                    data.append(row_data)
        
        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])  # Assuming the first row contains column names

        # Rename the 'Day  Beg   End   Bld  g Room  (Type)' column to a more readable name
        df = df.rename(columns={'Day  Beg   End   Bldg Room  (Type)': 'Schedule'})

        # Apply the _decode_class_meeting_to_str function to the 'schedule' column
        df['Schedule'] = df['Schedule'].apply(lambda x: self._decode_class_meeting_to_str(x))

        return df

    def _ln_decode_class_meeting(self, string: str):
        days_match = re.search(r"[A-Z]{,6}", string)
        time_match = re.search(r'(\b\d{4}) (\d{4}\b)', string)
        place_match = re.search(r"([A-Z]{3,6}) (\d{,4}\b)", string)

        _time = lambda x : datetime.strptime(x, "%H%M") 

        def _dtoi(d):
            """converts day to int
            """
            
            return 'MTWRFS'.index(d)

        def _itod(i):
            return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i]

        days = [_itod(_dtoi(d)) for d in days_match.group()] if days_match else None
        time = (_time(time_match.group(1)), _time(time_match.group(2))) if time_match else None
        place = (place_match.group(1), place_match.group(2)) if place_match else None

        return days, time, place

    def _decode_class_meeting(self, string: str):
        """Decodes the class meeting time from a typical Rowan format
            Args:
                str: Rowan's string for class meetings
                example - "TR      1830 1945 SCIENC 149 (Class)\n
                        TR      2000 2115 SCIENC 149 (Class)"
                        - "MW      0930 1045 SCIENC 232 (Class)\n
                        T       1230 1345 SCIENC 232 (Class)\n
                        T       1400 1515 SCIENC 232 (Class)"
                        - "TR      1700 1815 DISCOV 409 (Class)"
                        - "MW      1530 1645   (Class)"
            Returns:
                times_dict: <days: int> : list[(start time, end time), ...]
                rooms_dict: <days:int> : (bldg, room)
                        
        """

        if not string:
            return None, None

        _ln_split: list[str] = string.split('\n')

        # <days: int> : list[(start time, end time), ...]
        times_dict = {}

        # <days:int> : (bldg, room)
        rooms_dict = {}

        for mtg in _ln_split:
            days, time, place = self._ln_decode_class_meeting(mtg)
            for d in days:
                if d in times_dict:
                    times_dict[d].append(time)
                else:
                    times_dict[d] = [time]

                rooms_dict[d] = place

        return times_dict, rooms_dict
    
    def _decode_class_meeting_to_str(self, string: str):    
        try:
            times, rooms = self._decode_class_meeting(string)
            out_str = ""
            for day in times:
                out_str += day + ": "
                if len(times[day]) == 0:
                    continue
                for start_time, end_time in times[day]:
                    start_str = start_time.strftime("%I:%M %p").lstrip("0").lower()
                    end_str = end_time.strftime("%I:%M %p").lstrip("0").lower()
                    time_range = f"{start_str} - {end_str}"
                    out_str += time_range + ", "

                if rooms[day] is not None:
                    out_str += "in " + rooms[day][0] + " " + rooms[day][1]
                    out_str += "\n"

            return out_str
        except:
            return None