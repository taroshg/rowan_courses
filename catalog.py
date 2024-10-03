import pandas as pd
from tqdm.autonotebook import tqdm

from course import Course
from courseclass import CourseClass
from sectiontally import SectionTally
from ratemyprof import RateMyProfScraper


class Catalog():
    """course catelog from Rowan section tally for any given semester
    Args:
        term: the term that was selected should be a str code
    Returns:
        a dict where the key is subject and the value is a list of all crse numbers
    """
    def __init__(self, csv='tally.csv', term:str ='Spring 2024'):
        self.term = term
        self.csv = csv
        
        self.st = SectionTally(term=term, 
                               csv=csv)
        self.df = self.st.df
        # 822 is code of Rowan University
        self.profs = RateMyProfScraper(822)

        self.subjs = self.df['Subj'].unique()
        self.courses = {}
        for subj in self.subjs:
            self.courses[subj] = self.df[self.df['Subj'] == subj]['Crse'].unique()

        self.catalog = {}
        for subj in tqdm(self.courses):
            for crse in self.courses[subj]:

                course = Course(subj, crse, term)
                classes = self.get_classes(subj, crse)

                if course.credits == None:
                    # slower method for extracting course credits
                    course.credits = self._extract_creds()

                self.catalog[f'{subj} {crse}'] = {"info": course, 
                                                  "classes": classes}

    def get_classes(self, subj, crse) -> list[CourseClass]:
        classes = self.df[(self.df['Subj'] == subj) & (self.df['Crse'] == crse)]
        out: list[CourseClass] = []
        for i in range(len(classes)):
            cls = classes.iloc[i]
            prof = self.profs.find_prof(cls['Prof'])

            # if proffesor info is found else just put in string
            prof = prof if prof else cls['Prof']
            cls = CourseClass(subj, 
                              crse, 
                              prof, 
                              cls['Day  Beg   End   Bldg Room  (Type)'], 
                              cls['Avail'], 
                              cls['Max'])
            out.append(cls)
        return 

    def _extract_creds(self):
        """ backup to extracts credits from the secition_tally if not found in description
        """
        _found = self.df[(self.df['Subj'] == self.subj) & (self.df['Crse'] == self.crse)]['Hrs']
        creds = None
        # if creds are found and the credits of all classes are the same
        if len(_found) > 0 and _found.all():
            creds = _found.iloc[0]
        return creds
        