from datetime import datetime
import urllib.request
from urllib.request import urlretrieve as ret

url='https://www.openml.org/data/get_csv/61/dataset_61_iris.csv'
ret(url,'dataset_61_iris.csv')

import pandas as pd
import numpy as np

df['acq_time']=df['acq_time'].apply(lambda x : x[:2]+':'+x[2:]+":00")
df['acq_time']=df['acq_time'].apply(lambda x: datetime.strptime(x,'%H:%M:%S').time())

