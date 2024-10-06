from backend.ratemyprof import RateMyProfScraper
from backend.sectiontally import SectionTally
from backend.catalog import Catalog

# downloads and stores all backend database
rowan_profs = RateMyProfScraper(profs_json='./backend/profs.json')
tally = SectionTally("Spring 2025", csv='./backend/tally.csv')
catalog = Catalog(tally, catalog_json='/backend/catalog.json')