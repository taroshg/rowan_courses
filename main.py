import requests
import pandas as pd
response = requests.post(url='https://banner9.rowan.edu/ords/ssb/bwckctlg.p_disp_course_detail',
                  data= {'cat_term_in': '202520',
                         'subj_code_in': 'ACC',
                         'crse_numb_in': '03210'})
print("The status code is:", response.status_code)
assert (response.status_code == 200), f"error: {response.status_code}"
if (response.status_code == 200):
    print("The content is:", response.text)