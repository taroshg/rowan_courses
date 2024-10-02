import pandas as pd
from course import Course
from tqdm.autonotebook import tqdm

class Catalog():
    """course catelog from Rowan section tally for any given semester
    Args:
        section_tally: select a term from
        https://banner.rowan.edu/reports/reports.pl?task=Section_Tally
        and search for ALL, then download as execel and load it into pandas
        term: the term that was selected should be a str code
    Returns:
        a dict where the key is subject and the value is a list of all crse numbers
    """
    def __init__(self, section_tally: pd.DataFrame, term:str ='202520'):
        self.st = section_tally
        self.subjs = section_tally['Subj'].unique()
        self.courses = {}
        for subj in self.subjs:
            self.courses[subj] = section_tally[section_tally['Subj'] == subj]['Crse'].unique()

        self.catalog = {}
        for subj in tqdm(self.courses):
            for crse in self.courses[subj]:
                course = Course(subj, crse, term)

                if course.credits == None:
                    # slower method for extracting course credits
                    course.credits = self._extract_creds()

                self.catalog[f'{subj} {crse}'] = course

    def _extract_creds(self):
        """ extracts credits from the secition_tally
        """
        _found = self.st[(self.st['Subj'] == self.subj) & (self.st['Crse'] == self.crse)]['Hrs']
        creds = None
        # if creds are found and the credits of all classes are the same
        if len(_found) > 0 and _found.all():
            creds = _found.iloc[0]
        return creds
        