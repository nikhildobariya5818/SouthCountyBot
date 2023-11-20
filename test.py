import pandas as pd
import json
from MiamidadeSearch import getFolioNumber,PropertyInformation,getZoning 
import numpy as np
import os


for filename in ["Output\\MiamiDadeForeclosure_RPMF__HOMESTEAD_07-16-2023_07-17-2023_NotMatched.csv"]:
    df = pd.read_csv(filename, converters={'Folio': str,'Middle Name': str})

    # print(df)
    for index, row in df.iterrows():
        print('*'*50)
        
        defendents = (row["tests"]) 
        
        for i in defendents.splitlines():
            if 'defendant' in i.lower() and 'defendant aka' not in i.lower() and 'america' not in i.lower() and 'unknown' not in i.lower():
                i  = i.replace("Defendant",'').strip()
                print(i)
                res = int(getFolioNumber(i))
                print(res)
                if res >1 :
                    print(i,res)