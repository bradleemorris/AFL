# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 13:44:24 2020

@author: bradmorris
"""

path='C:/Users/bradmorris/Documents/StubHub/Projects/AFL'
seasons=range(1980,2021)

import pandas as pd

# use scraper to pull data from afltables.com.au 
# credit: Michael Milton https://github.com/TMiguelT/AflTablesScraper
from afl_tables import MatchScraper
afl = []
for season in seasons:
    rounds = MatchScraper.scrape(season)
    for round in range(len(rounds)):
        for match in range(len(rounds[round].matches)):
            mseason=season
            mround=rounds[round].title
            mdate=rounds[round].matches[match].date
            mvenue=rounds[round].matches[match].venue
            mcrowd=rounds[round].matches[match].attendees
            mwinner=rounds[round].matches[match].winner
            mhome=rounds[round].matches[match].teams[0].name
            if len(rounds[round].matches[match].teams)==1:
                maway='Bye'
                mhomegoals=0
                mhomebehinds=0
                mhomescore=0
                mawaygoals=0
                mawaybehinds=0
                mawayscore=0
            else:
                mhomegoals=rounds[round].matches[match].teams[0].scores[3].goals
                mhomebehinds=rounds[round].matches[match].teams[0].scores[3].behinds
                mhomescore=rounds[round].matches[match].teams[0].scores[3].score
                maway=rounds[round].matches[match].teams[1].name
                mawaygoals=rounds[round].matches[match].teams[1].scores[3].goals
                mawaybehinds=rounds[round].matches[match].teams[1].scores[3].behinds
                mawayscore=rounds[round].matches[match].teams[1].scores[3].score
            afl.append([mseason,mround,mdate,mvenue,mcrowd,mwinner,mhome,mhomegoals,mhomebehinds,mhomescore,maway,mawaygoals,mawaybehinds,mawayscore])

afl = pd.DataFrame(afl,columns=['season','round','date','venue','crowd','winner','home','homegoals','homebehinds','homescore','away','awaygoals','awaybehinds','awayscore'])
afl.to_csv(path+'/match_data_'+str(seasons[0])+'_'+str(seasons[-1])+'.csv',index=False)

# output distinct venue list to add latitude/longitude for each venue (and team)
#venues=afl['venue'].drop_duplicates().sort_values()
#venues.to_csv(path+'/venues.csv')
