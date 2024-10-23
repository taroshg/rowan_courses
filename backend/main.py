from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sectiontally import SectionTally
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEPTS = json.load(open('./data/dept.json'))
SUBJS = json.load(open('./data/subj.json'))
ATTRS = json.load(open('./data/attr.json'))
CATALOG = json.load(open('./data/catalog.json'))
PROFS = json.load(open('./data/profs.json'))

@app.get("/")
async def root():
    return {"message": "SectionTally API"}

@app.get("/depts")
async def get_depts():
    return {"depts": DEPTS}

@app.get("/subjs") 
async def get_subjs():
    return {"subjs": SUBJS}

@app.get("/attrs")
async def get_attrs():
    return {"attrs": ATTRS}

@app.get("/profs")
async def get_profs():
    return {"profs": PROFS}

@app.get("/tally/{term}")
async def get_tally(term: str, subj: str = None, dept: str = None, attr: str = None):
    if subj is None:
        subj = 'ALL'
    elif subj not in SUBJS:
        return {"error": "Subject not found"}
    
    if dept is None:
        dept = 'ALL'
    elif dept not in DEPTS:
        return {"error": "Department not found"}
    
    if attr is None:
        attr = 'ALL'
    elif attr not in ATTRS:
        return {"error": "Attribute not found"}
    
    tally = SectionTally(term=term, subj=subj, dept=dept, attr=attr)

    out = dict()
    out = tally.df.to_dict(orient='records')
    return out

@app.get("/catalog")
async def get_catalog(course: str=None):
    """
    Get the catalog for a given course
    Args:
        course: the course code, example 'CS20123', 'MATH101', 'ENGL101'
    Returns:
        the catalog for the given course
    """
    out = dict()
    if not course:
        out = CATALOG
        return out
    
    def format_course_code(course_code: str) -> str:
        """
        Formats the course code to match the format in the catalog
        """
        split_index = next((i for i, char in enumerate(course_code) if char.isdigit()), len(course_code))
        return f"{course_code[:split_index]} {course_code[split_index:]}"

    out = CATALOG[format_course_code(course)]
    return out
