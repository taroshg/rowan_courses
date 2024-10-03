from course import Course
from datetime import datetime
import re

class CourseClass(Course):
    """creates a class for a certain course
    Args:
        subj: subject ex. (ACC, CS, ...)
        crse: course number ex. (03110, 02110, ...)
        prof: name of the professor
        sched: weekly class schedule
               ex. TR      1100 1215 BUSN 101 (Class)
        term: year and term value (202440, 202530, ...)
    """
    def __init__(self, subj: str, 
                       crse: str, 
                       prof: str | dict,
                       sched: str,
                       avail: int,
                       max: int,
                       term: str = '202520') -> None:

        super().__init__(subj, crse, term)
        
        self.sched = self._decode_class_meeting(sched)
        self.prof = prof
        self.avail = avail
        self.max = max
        self.term = term

    def _dtoi(self, d):
        """converts day to int
        """
        return 'MTWRFS'.index(d)
    
    def _itod(self, i):
        return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i]

    def _ln_decode_class_meeting(self, string: str):
        days_match = re.search(r"[A-Z]{,6}", string)
        time_match = re.search(r'(\b\d{4}) (\d{4}\b)', string)
        place_match = re.search(r"([A-Z]{3,6}) (\d{,4}\b)", string)

        _time = lambda x : datetime.strptime(x, "%H%M") 

        days = [self._dtoi(d) for d in days_match.group()] if days_match else None
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
