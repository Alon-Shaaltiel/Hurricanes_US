import matplotlib.pyplot as plt
import numpy as np
import matplotlib.style as style
import pandas as pd
import itertools


style.use('ggplot')

HPI_Data = pd.read_pickle("HPI_Data.pickle")
US_Hurr = pd.read_pickle("US_Hurricanes.pickle")
US_Unaffctd = pd.Series(
    {'State': np.array(['Colorado', 'Utah', 'Nevada', 'Idaho', 'Wyoming', 'South Dakota', 'North Dakota'])})
# States that are in the middle or top middle of the US and are land-locked by others.
# they are unlikely to have many strong hurricanes there.

Columns = [['Affctd', 'Unaffctd'], ['HPI_' + Name for Name in list(US_Hurr.index.values)]]
Columns = list(itertools.product(Columns[0], Columns[1]))

HPI_Areas = pd.DataFrame(columns=Columns)
HPI_Areas.columns = pd.MultiIndex.from_tuples(HPI_Areas.columns, names=['Area', 'Hurricane'])

for Hurricane in list(US_Hurr.index.values):
    HPI_Areas[('Affctd', 'HPI_' + Hurricane)] = \
        HPI_Data.loc[:, ["HPI " + State for State in US_Hurr.loc[Hurricane, 'Area']]].mean(axis=1)

    HPI_Areas[('Unaffctd', 'HPI_' + Hurricane)] = \
        HPI_Data.loc[:, ["HPI " + State for State in US_Unaffctd.State]].mean(axis=1)

Affc_Srs = pd.Series(dtype=float)
Unaffc_Srs = pd.Series(dtype=float)
HPI_corr = pd.DataFrame(columns=list(US_Hurr.index.values), index=['Corrlt Hurr', 'Corrlt Nrml', 'Nrml STD'])
corr_info = pd.DataFrame()

for Hurr in list(US_Hurr.index.values):
    NumMnt = 8
    Date = US_Hurr.loc[Hurr, 'Date']
    Date_Before = Date - DateOffset(months=NumMnt)
    Date_After = Date + DateOffset(months=NumMnt)
    Affc_Srs = HPI_Areas['Affctd'].loc[Date_Before:Date_After, 'HPI_' + Hurr].reset_index(drop=True)
    Unaffc_Srs = HPI_Areas['Unaffctd'].loc[Date_Before:Date_After, 'HPI_' + Hurr].reset_index(drop=True)

    HPI_corr.loc['Corrlt Hurr', Hurr] = Unaffc_Srs.corr(Affc_Srs)
    corr_info = HPI_Areas[('Unaffctd', 'HPI_' + Hurr)].rolling(NumMnt * 2 + 1).corr(
        HPI_Areas[('Affctd', 'HPI_' + Hurr)]).describe()
    HPI_corr.loc['Corrlt Nrml', Hurr] = corr_info['mean']
    HPI_corr.loc['Nrml STD', Hurr] = corr_info['std']

print(HPI_corr)
print("As we can clearly see, no correlation is more than one"
      " standard deviation from the expected value.\n"
      "Most standard deviations are quite high "
      "which may point to volatility, or the house buying cycles.\n"
      "You can see these cycles in the shown figure if you zoom in a little,"
      " people buy more houses during the summer.")

fig = plt.figure()
HPI_Data['HPI Florida'].plot()
fig.legend(["Florida's HPI"])
plt.show()

# Toodles :)