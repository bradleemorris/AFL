# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 10:42:08 2021

@author: bradmorris
"""

path='C:/Users/bradmorris/Documents/StubHub/Projects/AFL'
from math import cos, asin, sqrt, pi
import numpy as np
import pandas as pd
import datetime as dttm
import pytz
from dateutil.relativedelta import relativedelta as reldt

# Recreate ELO rating model from thearcfooty.com

# load match and venue data
matches=pd.read_csv(path+'/match_data_1980_2020.csv')
matches['date']=pd.to_datetime(matches['date'],utc=True)
venues=pd.read_csv(path+'/venues.csv')

# matches[matches['home']=='Collingwood'].head()


# get list of teams
teams=matches['home'].drop_duplicates().sort_values()
teams

# define t=0
dt0 = matches['date'].min() - reldt(weeks=18)
dt0

# define ELO parameters
elo0 = 1500  # starting ELO
m = 400      # scale factor
p = 0.0464   # win probability to margin conversion
k = 70       # ELO damping factor (higher=more responsive)
gamma = 0.33 # Distance travelled scale parameter
alpha = 6    # Distance travelled advantage parameter
beta  = 15   # Games played at venue advantage parameter

# create ELO dataframe with default ratings
elo = []
for tm in teams:
    if tm in ['Gold Coast', 'Greater Western Sydney']:
        elo.append([tm,dt0,1090])
    else:
        elo.append([tm,dt0,elo0])
elo=pd.DataFrame(elo,columns=['team','date','ELO_rating'])

# function to pop latest ELO for given team, date
def get_elo(dt,tm):
    if dt < elo['date'].min():
        print("\nget_elo() failed: invalid date")
        return 1500
    else:
        return elo['ELO_rating'][(elo['team']==tm) & (elo['date']<dt)].iloc[-1]

# function to predict result and margin for given teams and date
def get_pred(dt,tm1,tm2,venue):
    elo1=get_elo(dt,tm1)
    elo2=get_elo(dt,tm2)
    hga=alpha*get_trv(tm1,tm2,venue)+beta*get_exp(dt,tm1,tm2,venue)
    pred=1/(1+10**(-(elo1-elo2+hga)/m))
    margin=-np.log((1-pred)/pred)/p
    return pred, margin

# function to update ELO ratings based on actual result
def calc_elos(dt,tm1,tm2,venue,tm1score,tm2score):
    actual=1/(1+np.exp(-p*(tm1score-tm2score)))
    [pred,margin]=get_pred(dt,tm1,tm2,venue)
    delta=k*(actual-pred)
    new_elos=[get_elo(dt,tm1)+delta,get_elo(dt,tm2)-delta]
    return pred, margin, new_elos

def get_exp(dt,tm1,tm2,venue):
    exp_tm1=len(matches[(matches['venue']==venue)&(matches['date']>dt+reldt(years=-3))&(matches['date']<dt)&((matches['home']==tm1)|(matches['away']==tm1))])
    exp_tm2=len(matches[(matches['venue']==venue)&(matches['date']>dt+reldt(years=-3))&(matches['date']<dt)&((matches['home']==tm2)|(matches['away']==tm2))])
    exp=np.log(exp_tm1+1)-np.log(exp_tm2+1)
    return exp

def get_dist(lat1,lon1,lat2,lon2): # Haversine distance formula
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 12742 * asin(sqrt(a))

def get_trv(tm1,tm2,venue):
    latlon_tm1=venues[['latitude','longitude']][venues['venue']==tm1].values[0]
    latlon_tm2=venues[['latitude','longitude']][venues['venue']==tm2].values[0]
    latlon_ven=venues[['latitude','longitude']][venues['venue']==venue].values[0]
    trv_tm1=get_dist(latlon_tm1[0],latlon_tm1[1],latlon_ven[0],latlon_ven[1])
    trv_tm2=get_dist(latlon_tm2[0],latlon_tm2[1],latlon_ven[0],latlon_ven[1])
    if trv_tm1>=trv_tm2: # if Home team travel > Away team travel then ignore travel advantage
        trv=0
    else:
        trv=(trv_tm2-trv_tm1)**gamma
    return trv


# Generate predictions and update ELO ratings
predictions=[]
for index, row in matches.iterrows():
    if row['round']=='Round 1': # ELO ratings regress 10% towards mean at start of season
        dt=pd.to_datetime(str(row['season'])+'0101',format='%Y%m%d',utc=True)
        elo_upd1=[row['home'],dt,0.9*get_elo(dt,row['home'])+0.1*elo0]
        if row['away']!='Bye':
            elo_upd2=[row['away'],dt,0.9*get_elo(dt,row['away'])+0.1*elo0]
        else:
            elo_upd2=[]
        elo_update=pd.DataFrame([elo_upd1,elo_upd2],columns=['team','date','ELO_rating'])
        elo=elo.append(elo_update) # ELO ratings need to be updated within loop
    if row['away']=='Bye':
        pred=0.5
        margin=0
    else:
        [pred, margin, new_elos]=calc_elos(row['date'],row['home'],row['away'],row['venue'],row['homescore'],row['awayscore'])
        elo_upd1=[row['home'],row['date'],new_elos[0]]
        elo_upd2=[row['away'],row['date'],new_elos[1]]
        elo_update=pd.DataFrame([elo_upd1,elo_upd2],columns=['team','date','ELO_rating'])
        elo=elo.append(elo_update) # ELO ratings need to be updated within loop
    predictions.append([pred,margin])

# Create dataframe for predicted result and margin for each match
predictions=pd.DataFrame(predictions,columns=['pred_result','pred_margin'])

# Output predictions for inspection
matches.join(predictions).to_csv(path+'/match_data_test.csv',index=False)


# Plot ELO scores for 2016 season
import matplotlib.pyplot as plt

x=[dttm.datetime(2016,1,1,tzinfo=pytz.UTC)+dttm.timedelta(days=i) for i in range(365)]
y1=[get_elo(i,'Sydney') for i in x]
y2=[get_elo(i,'Geelong') for i in x]
y3=[get_elo(i,'Hawthorn') for i in x]

plt.plot(x,y1,'r',x,y2,'b',x,y3,'y')
plt.show()

