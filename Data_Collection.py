import pandas as pd
import quandl
import re
import datetime
from pandas.tseries.offsets import DateOffset
import numpy as np
import itertools

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 90)
pd.set_option('display.max_rows', None)
pd.set_option('display.min_rows', 26)
pd.set_option('display.width', 200)


api_key = 'HxxAsWWP1AJofAW8u261'
quandl.ApiConfig.api_key = api_key
# I want to find out if hurricanes
# affect the housing price index


# First let's get the housing price index for every state:
US_States = pd.read_html("https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States")
US_States = np.array([State.strip('[D]') for State in US_States[1].iloc[:, 0]])

def HPI_State_Initial():
    US_Abbv = pd.read_html("https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States")
    HPI_Data = pd.DataFrame()
    US_Abbv = US_Abbv[0].iloc[:, 0:2]
    # The [0] takes the first element of the page, which is the list

    US_Abbv.columns = ["State", "Abbv"]
    # Unconfuses the list from wikipedia
    US_Abbv['State'] = US_Abbv['State'].apply(lambda x: x.strip('[D]'))

    for index, row in US_Abbv.iterrows():
        if HPI_Data.empty:
            HPI_Data = quandl.get("FMAC/HPI_" + row.Abbv).drop(columns="SA Value")
            # The freddie mac data gives NSA Value and SA Value,
            # I'm only looking for a correlation so I'll delete one.
            HPI_Data.rename(columns={"NSA Value": "HPI " + row.State}, inplace=True)

        else:
            HPI_Data = HPI_Data.join(quandl.get("FMAC/HPI_" + row.Abbv).drop(columns="SA Value"))
            HPI_Data.rename(columns={"NSA Value": "HPI " + row.State}, inplace=True)

    HPI_Data.to_pickle("HPI_Data.pickle")


HPI_State_Initial()

HPI_Data = pd.read_pickle("HPI_Data.pickle")
HPI_Data.index = HPI_Data.index.to_period('M')


Hurricanes = pd.read_html("https://en.wikipedia.org/wiki/List_of_Category_5_Atlantic_hurricanes")
Hurricanes = Hurricanes[1].iloc[:-1,[0,1,5,6]]
# The list is on [1] and other columns are irrelevant or NaNs.
# The last row is some words
Hurricanes.columns = ["Name","Date","Area","Death"]

US_Loc = np.append(US_States, ['United', 'States', 'Gulf', 'East', 'West', 'Coast', 'Eastcoast'])


def Cleanup_Area(Area):
    Area_New = re.findall('[A-Z][^A-Z]*', Area)
    Area_New = [Word.strip("[!@#$, ]") for Word in Area_New]
    return np.array(Area_New)


Hurricanes["Area"] = Hurricanes['Area'].apply(Cleanup_Area)


def Is_In_US(npArr):
    if (np.intersect1d(npArr, US_Loc).size != 0):
        return np.intersect1d(npArr, US_Loc)
    return np.NaN


US_Hurr = Hurricanes.copy()
US_Hurr['Area'] = US_Hurr['Area'].apply(Is_In_US)
US_Hurr = US_Hurr.dropna().set_index("Name")

US_Hurr.to_pickle("US_Hurricanes.pickle")


def simplify_date(Wiki_Date):
    Wiki_Date = Wiki_Date.strip(" †")
    # Weird wikipedia thing
    Wiki_Date = Wiki_Date.split(" ")
    Mnt, Yr = Wiki_Date[0], Wiki_Date[-1]

    datetime_object = datetime.datetime.strptime(Mnt, "%B")
    # To take a month name and turn it into a month number
    Mnt_Num = datetime_object.month

    if int(Yr) < 1975:
        return np.NAN
        # Because there's no HPI date before 1975

    return pd.to_datetime(Yr + "-" + str(Mnt_Num).zfill(2))
    # to format it the same way as the HPI Index


US_Hurr.loc[:, "Date"] = US_Hurr.loc[:, "Date"].apply(simplify_date)
US_Hurr.dropna(inplace=True)


def State_Associate(Area_List, Alt=False):
    Gulf_Coast = ['Texas', 'Louisiana', 'Mississippi', 'Alabama', 'Florida']

    if not Alt:
        East_Coast = ' Maine, New Hampshire, Massachusetts,' \
                     ' Rhode Island, Connecticut, New York, ' \
                     'New Jersey, Delaware, Maryland, Virginia,' \
                     ' North Carolina, South Carolina, Georgia, Florida'.split(',')
        East_Coast = [State.strip(" ") for State in East_Coast]
    else:
        East_Coast = ' North Carolina, South Carolina, Georgia, Florida'.split(',')
        East_Coast = [State.strip(" ") for State in East_Coast]
        # although "East Coast" is written, many of the states there are likely less affected.

    if np.intersect1d(US_States, Area_List).size != 0:
        return np.intersect1d(US_States, Area_List)
        # We are trying to find a correlation, this is where we'll find it,
        # in the exact states mentioned

    if 'Gulf' in Area_List:
        return Gulf_Coast

    if ('East' or 'Eastcoast') in Area_List:
        return East_Coast
    return Gulf_Coast
    # The gulf coast appears more in the data so we'll make that our default

HPI_Data = pd.read_pickle("HPI_Data.pickle")

US_Hurr.loc[:, "Date"] = US_Hurr.loc[:, "Date"].apply(simplify_date)
US_Hurr.dropna(inplace=True)


def State_Associate(Area_List, Alt=False):
    Gulf_Coast = ['Texas', 'Louisiana', 'Mississippi', 'Alabama', 'Florida']

    if not Alt:
        East_Coast = ' Maine, New Hampshire, Massachusetts,' \
                     ' Rhode Island, Connecticut, New York, ' \
                     'New Jersey, Delaware, Maryland, Virginia,' \
                     ' North Carolina, South Carolina, Georgia, Florida'.split(',')
        East_Coast = [State.strip(" ") for State in East_Coast]
    else:
        East_Coast = ' North Carolina, South Carolina, Georgia, Florida'.split(',')
        East_Coast = [State.strip(" ") for State in East_Coast]
        # although "East Coast" is written, many of the states there are likely less affected.

    if np.intersect1d(US_States, Area_List).size != 0:
        return np.intersect1d(US_States, Area_List)
        # We are trying to find a correlation, this is where we'll find it,
        # in the exact states mentioned

    if 'Gulf' in Area_List:
        return Gulf_Coast

    if ('East' or 'Eastcoast') in Area_List:
        return East_Coast
    return Gulf_Coast
    # The gulf coast appears more in the data so we'll make that our default


US_Hurr['Area'] = US_Hurr['Area'].apply(State_Associate, Alt=True)

print(US_Hurr)