from backend.ratemyprof import RateMyProfScraper
from backend.sectiontally import SectionTally
from backend.catalog import Catalog

# scrapes and downloads all the data from RateMyProf and SectionTally, into the frontend
rowan_profs = RateMyProfScraper(profs_json='./frontend/src/profs.json')
tally = SectionTally("Spring 2025", csv='./frontend/src/tally.json')

# scrapes course title, descriptions, credits, prerequisites from Rowan's catalog
catalog = Catalog(tally, catalog_json='./frontend/src/catalog.json')