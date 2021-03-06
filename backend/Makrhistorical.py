import aiohttp
import pytz
import matplotlib.pyplot as plt
import datetime
import asyncio
import nest_asyncio
import glob
import requests
from datetime import datetime, date, time, timedelta
import datetime as dt
from flaml import AutoML
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import plot_importance, plot_tree
import xgboost as xgb
from keras import optimizers
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from keras.preprocessing.sequence import TimeseriesGenerator
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import matplotlib as plt
import swifter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import tqdm
import nltk
import re
import getpass
import os
import numpy as np
import pandas as pd
scaler = StandardScaler()

nest_asyncio.apply()


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


data_dict = {}


async def get(
    session: aiohttp.ClientSession,
    date: str,
    **kwargs
) -> dict:
    global data_dict
    api = f"https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/minute/{date}/{date}?adjusted=true&sort=asc&limit=1440&apiKey=Ot5XxPIdM4IAsPj6TdlIqHajQFK356JB"
    #print(f"Requesting {api}")
    resp = await session.request('GET', url=api, **kwargs)
    # print(resp)
    data = await resp.json()
    # print(data)
    data_dict[date] = data


async def main(dates, **kwargs):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for c in dates:
            tasks.append(get(session=session, date=c, **kwargs))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses


if __name__ == '__main__':
    start_date = '2016-01-01'
    end_date = '2022-04-02'
    dates = []
    for i in daterange(pd.to_datetime(start_date), pd.to_datetime(end_date)):
        dates.append(i.date().strftime("%Y-%m-%d"))
    # print(dates)
    asyncio.run(main(dates))


new_dict = []

for index, i in enumerate(data_dict):
    if 'results' not in list(data_dict[i].keys()):
        pass
    else:
        new_dict = new_dict + data_dict[i]['results']


df = pd.DataFrame(new_dict)
df['timestamp'] = df['t']
del df['t']
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Karachi')
df['timestamp'] = df['timestamp'].dt.tz_localize(None)
df = df[['timestamp', 'o', 'h', 'l', 'c', 'v']]
df = df.sort_values(by='timestamp')
df = df.rename({"o": "Open", "h": "High", "l": "Low",
                "c": "Close", "v": "Volume"}, axis=1)
df = df.reset_index(drop=True)


df.to_csv("Complete_Final_Historical_Minute_till_2nd_April_2022.csv", index=False)
