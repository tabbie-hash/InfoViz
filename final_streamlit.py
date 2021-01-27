#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# coding: utf-8

# In[ ]:
#Documents\MSI\Fall_2020\SI649_InfoVis\Final

import pandas as pd
import altair as alt
import numpy as np
import pprint
import streamlit as st
import networkx as nx
import nx_altair as nxa
import time, json
import seaborn as sns

#data:
gamedata = {}
with open('bobvalice.json') as json_file:
    gamedata = json.load(json_file)

robotdata = pd.read_csv("examplematch1.robotdata.csv")

#filter data

# figure out the correct answers
correctAnswer = []
for row in robotdata[robotdata.id < 100].sort_values('id').iterrows():
    row = row[1]                 # the row data
    expires = int(row.expires)   # when the robot expired
    col = "t_"+str(expires)      # the column for that time
    valAtExp = row[col]          # the value at that time for that robot
    correctAnswer.append(valAtExp)

#who won and why
gamewins = pd.DataFrame(gamedata['winreasons'])
gamewins.insert(0, 'time', range(1, 1 + len(gamewins)))

hints = pd.DataFrame(gamedata['team1_hints_bots'])
game = pd.DataFrame(list(gamedata.items()),columns = ['winner','reason'])

#add additional information
dataset = pd.DataFrame({'time':np.arange(1,101),'realanswer': correctAnswer,
                        'team1_bet': gamedata['team1_bets'],'team2_bet': gamedata['team2_bets']})

dataset.insert(4, 'winner', gamewins['winner'])
dataset.insert(5, 'reason', gamewins['reason'])
dataset.insert(6, 'robot_name', robotdata['name'])
dataset.insert(7, 'astrogation_buffer_length', robotdata['Astrogation Buffer Length'])
dataset.insert(8, 'Polarity Sinks', robotdata['Polarity Sinks'])
dataset.insert(9, 'Arakyd Vocabulator Model', robotdata['Arakyd Vocabulator Model'])
dataset.insert(10, 'Axial Piston Model', robotdata['Axial Piston Model'])
dataset.insert(11, 'Nanochip Model', robotdata['Nanochip Model'])
dataset.insert(12, 'AutoTerrain Tread Count', robotdata['AutoTerrain Tread Count'])
dataset.insert(12, 'InfoCore Size', robotdata['InfoCore Size'])
dataset.insert(12, 'Sonoreceptors', robotdata['Sonoreceptors'])
dataset.insert(12, 'Cranial Uplink Bandwidth', robotdata['Cranial Uplink Bandwidth'])
dataset.insert(12, 'Productivity', robotdata['Productivity'])

#Integration of production values
team_productivity = []


team1 = 0
team2 = 0
for index, row in dataset.iterrows():
    productivity = {}
    productivity['time'] = row['time']
    if row['winner'] == 1:
        team1 += row['Productivity']
        productivity['team1'] = team1
    else:
        team1 += 0
        productivity['team1'] = team1
    if row['winner'] == 2:
        team2 += row['Productivity']
        productivity['team2'] = team2
    else:
        team2 += 0
        productivity['team2'] = team2
    team_productivity.append(productivity)
team_prod = pd.DataFrame(team_productivity)
longform_prod = team_prod.melt(id_vars='time',value_vars=['team1','team2'])

#get margin of error percentage
dataset['team1'] = abs(dataset['realanswer'] - dataset['team1_bet'])
dataset['team2'] = abs(dataset['realanswer'] - dataset['team2_bet'])
dataset['team1percent'] = (dataset['team1'] / (dataset['team1'] + dataset['team2'])) * 100
dataset['team2percent'] = (dataset['team2'] / (dataset['team1'] + dataset['team2'])) * 100

longform = dataset.melt(id_vars='time',value_vars=['team1','team2'])
margin_longform = dataset.melt(id_vars='time',value_vars=['team1percent','team2percent'])

margin_longform = margin_longform.replace(to_replace=r'team1percent', value='team1', regex=True)
margin_longform = margin_longform.replace(to_replace=r'team2percent', value='team2', regex=True)

#merge dataframes
robo_merged = pd.merge(longform_prod, dataset, left_on='time', right_on='time')

#get new_parts df
robotdata.drop(robotdata.tail(48).index, inplace = True)


#Vis1
m2_over = alt.selection_single(on = 'mouseover', nearest = True, empty = 'none')
opacity2 = alt.condition(m2_over, alt.value(1), alt.value(0.0))

#vertical line
rule1 = alt.Chart(robo_merged).mark_rule(color='lightgray').encode(
    x='time:O',
    size=alt.value(4),
    opacity = opacity2
)

#make circles
circle1 = alt.Chart(robo_merged).mark_circle(color = 'black').encode(
    x='time:O',
    y='value:Q',
    opacity = opacity2,
    tooltip = ('time:O', 'value:Q', 'variable:N', 'winner:N')

).add_selection(m2_over)


#Vis2
line1 = alt.Chart(robo_merged, title='Productivity Over Time').mark_line().encode(
    x='time:O',
    y='value:Q',
    color='variable:N'
).properties(width = 500)

chart1 = line1 + rule1 + circle1

#Vis3
margin1 = alt.Chart(margin_longform, title='Relative Bet Error').mark_bar().encode(
    x= alt.X('time:O',axis=None),
    y= alt.Y('sum(value):Q',axis=None),
    color='variable:N'
).properties(width = 500, height = 100
).add_selection(m2_over)

margin1 = margin1 + rule1

#Vis4
ranked_text = alt.Chart(robo_merged).mark_text().encode(
    y=alt.Y('time:O',axis=None)
).transform_window(
    row_number='row_number()'
).transform_filter(m2_over)
name = ranked_text.encode(text='robot_name:N').properties(title='Name', width=10)
prod = ranked_text.encode(text='Productivity:Q').properties(title='Productivity', width=100,)
astro = ranked_text.encode(text='Astrogation Buffer Length:Q').properties(title='Astrogation Buffer Length', width=100,)
polar = ranked_text.encode(text='Polarity Sinks:Q').properties(title='Polarity Sinks', width=100,)
band = ranked_text.encode(text='Arakyd Vocabulator Model:Q').properties(title='Arakyd Vocabulator Model', width=100,)
axial = ranked_text.encode(text='Axial Piston Model:Q').properties(title='Axial Piston Model', width=100,)
nano = ranked_text.encode(text='Nanochip Model:Q').properties(title='Nanochip Model', width=100,)
auto = ranked_text.encode(text='AutoTerrain Tread Count:Q').properties(title='AutoTerrain Tread Count', width=100,)
info = ranked_text.encode(text='InfoCore Size:Q').properties(title='InfoCore Size', width=100,)
sono = ranked_text.encode(text='Sonoreceptors:Q').properties(title='Sonoreceptors', width=100,)
band = ranked_text.encode(text='Cranial Uplink Bandwidth:Q').properties(title='Cranial Uplink Bandwidth', width=100,)





text1 = name & prod & astro & polar & band | axial & nano & auto & info & sono & band

first_fig = chart1 & margin1 | text1

first_fig = first_fig.configure_view(
    strokeWidth=0
)


#Robot specific stats
list = ['Repulsorlift Motor HP', 'Astrogation Buffer Length', 'Polarity Sinks', 'AutoTerrain Tread Count', 'InfoCore Size', 'Sonoreceptors', 'Cranial Uplink Bandwidth']
selection = alt.selection_single(empty = 'none', on = 'mouseover')
opacity = alt.condition(selection, alt.value(1.0), alt.value(0.4))
area_selection = alt.selection_interval(empty = 'none')
colorCondition=alt.condition(selection|area_selection, alt.value('green'), alt.value('purple'))
sizeCondition=alt.condition(selection|area_selection,alt.value(80),alt.value(20))

scatter = alt.Chart(robotdata).mark_point().encode(
    alt.X('Productivity:Q'),
    alt.Y(alt.repeat("column"), type ='quantitative'),
    opacity = opacity,
    tooltip = ['name:N', 'id:N']
).add_selection(
    selection
).add_selection(
    area_selection
).encode(
    color = colorCondition,
    size = sizeCondition
).properties(
    width = 150,
    height = 150
).repeat(
    column = list[0:3]
)

scatter2 = alt.Chart(robotdata).mark_point().encode(
    alt.X('Productivity:Q'),
    alt.Y(alt.repeat("column"), type ='quantitative'),
    opacity = opacity,
    tooltip = ['name:N', 'id:N']
).add_selection(
    selection
).add_selection(
    area_selection
).encode(
    color = colorCondition,
    size = sizeCondition
).properties(
    width = 150,
    height = 150
).repeat(
    column = list[3:7]
)

box1 = alt.Chart(robotdata).mark_boxplot(size = 60).encode(
    alt.Y('Productivity:Q'),
    alt.X ('Arakyd Vocabulator Model:N'),
    alt.Color('mean(Productivity):Q')
).properties(
    width = 150,
    height = 300
)

box2 = alt.Chart(robotdata).mark_boxplot(size = 30).encode(
    alt.Y('Productivity:Q'),
    alt.X('Axial Piston Model:N'),
    alt.Color('mean(Productivity):Q')
).properties(
    width = 150,
    height = 300
)

box3 = alt.Chart(robotdata).mark_boxplot(size = 60).encode(
    alt.Y('Productivity:Q'),
    alt.X('Nanochip Model:N'),
    alt.Color('mean(Productivity):Q')
).properties(
    width = 150,
    height = 300
)
boxplt = box1 | box2 | box3


#Here is where the charts and text gets displayed

st.title('ROBOGAMES INSIGHTS\nby - Erin Murray, Inigo Peng, Shanti, Vineeth Jason Putti, Tabassum Nisha ')

st.header('PRODUCTIVITY METER:')
first_fig
st.text('The time series line chart has an interactive slider which shows\nthe match statistics for both the players. It displays the relationship\nbetween the time and productivity with the players represented by\ndifferent colors. The slider moves along with the mouse on the x-axis and\ndisplays intersection dots with the lines.')
st.text('The tooltip on hover shows details about the current data point that included\nthe current team, winning team, value of productivity and time instance.\nThe sidebar panels displaying fixed stats on the right dynamically provide additional\ndetails of the current robot, its parts and its productivity.')

st.header('PRODUCTIVITY CORRELATIONS:')
scatter
scatter2
st.text('These scatter plots illustrate the correlation between the attributes clearly.\nFor example - we can see that both sonoreceptors and cranial uplink bandwidth\nhave a significant correlation with productivity.')
st.text('The robots are displayed on the horizontal axis and their productivity\nid on the vertical axis. Each sub plot represents a\ndifferent part. Hovering over the scatter plot simultaneously\ncorresponds the mark to all the scatter plots and it displays the Robot name\nand its id. The user can also select by dragging over the area to compare\nmultiple points. The marks also enlarge when selected for more comfortable viewing.')

st.header('PRODUCTIVITY OF DIFFERENT ROBOT PARTS:')
boxplt
st.text('This is a detailed view of the relationship between a part\nand productivity. The type part is represented on the horizontal\naxis and the productivity on the vertical axis. Each sub plot represents\na different part. For example : We could see that for some robot parts like\nKappa Axial Piston Model, most of the productivity value is spread out\nbetween -10 and 100. Simultaneously, the alpha Axial Piston model\nhas the majority of its productivity between 30 and 75.')

#st.subheader('\nIn conclusion, these communicative visualizations sufficiently cater to our domain task objectives and provide viewers a much valuable insight and analysis on the game.\nThank you.')

st.set_option('deprecation.showPyplotGlobalUse', False)
st.pyplot()
