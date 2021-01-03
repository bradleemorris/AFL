# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 10:42:08 2021

@author: bradmorris
"""

path='C:/Users/bradmorris/Documents/StubHub/Projects/AFL'

import numpy as np
import pandas as pd
import datetime as dttm

# ELO rating model from thearcfooty.com

# load match and venue data
matches=pd.read_csv(path+'/match_data_1980_2020.csv')
matches['date']=pd.to_datetime(matches['date'],utc=True)
venues=pd.read_csv(path+'/venues.csv')

# matches[matches['home']=='Collingwood'].head()


# get list of teams
teams=matches['home'].drop_duplicates().sort_values()
teams

# define t=0
dt0 = matches['date'].min() - dttm.timedelta(days=1)
dt0

# define ELO parameters
elo0 = 1500  # starting ELO
m = 400      # scale factor
p = 0.0464   # win probability to margin conversion
k = 70       # ELO damping factor (higher=more responsive)

# create ELO dataframe with default ratings
elo = []
for tm in teams:
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
def get_pred(dt,tm1,tm2):
    elo1=get_elo(dt,tm1)
    elo2=get_elo(dt,tm2)
    pred=1/(1+10**((elo2-elo1)/m))
    margin=-np.log((1-pred)/pred)/p
    return pred, margin

# function to update ELO ratings based on actual result
def calc_elos(dt,tm1,tm2,tm1score,tm2score):
    actual=1/(1+np.exp(-p*(tm1score-tm2score)))
    [pred,margin]=get_pred(dt,tm1,tm2)
    delta=k*(actual-pred)
    new_elos=[get_elo(dt,tm1)+delta,get_elo(dt,tm2)-delta]
    return pred, margin, new_elos

# Generate predicitons and update ELO ratings
predictions=[]
for index, row in matches.iterrows():
    if row['away']=='Bye':
        pred=0.5
        margin=0
    else:
        [pred, margin, new_elos]=calc_elos(row['date'],row['home'],row['away'],row['homescore'],row['awayscore'])
        elo_upd1=[row['home'],row['date'],new_elos[0]]
        elo_upd2=[row['away'],row['date'],new_elos[1]]
        elo_update=pd.DataFrame([elo_upd1,elo_upd2],columns=['team','date','ELO_rating'])
        elo=elo.append(elo_update) # ELO ratings need to be updated within loop
    predictions.append([pred,margin,new_elos[0],new_elos[1]])

# Create dataframe for predicted result and margin for each match
predictions=pd.DataFrame(predictions,columns=['pred_result','pred_margin','new_ELO_home','new_ELO_away'])

# Output predictions for inspection
matches.join(predictions).to_csv(path+'/match_data_test.csv',index=False)







