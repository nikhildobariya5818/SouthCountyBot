
import math
import os
import time
import datetime
import SetDates
import numpy as np
from keywords import COMPANY_KEYWORDS
import pandas as pd
import json
import traceback
import sys
import re
from bs4 import BeautifulSoup
from clean_name import CleanName

class BrowrdSearch:

    def __init__(self, name: str) -> None:
        c = CleanName(name)
        print(json.dumps(c.get_cleaned_name()))
