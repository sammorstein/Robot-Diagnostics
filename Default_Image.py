# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 10:30:41 2022

@author: QTD8635
"""

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib.colors import Normalize
from tkinter import *
from tkcalendar import Calendar
from PIL import ImageTk, Image

pc_name = '10305UC02045OV1'
path = os.listdir('Z:\\INOS\\'+pc_name)

startdate = '2022-10-21'
robotnum = 1
robotname = 'R'+str(robotnum)
filetype = 'Output.Classic'
filelist = []

num_points = 3000
points = 0
fulldata = pd.DataFrame()
date = startdate
while points < num_points:
    for x in path:
        if date in x and filetype in x:
            filelist.append(x) 
    if bool(filelist):
        if robotnum % 2 == 1:
            filename = filelist[0]
        else: 
            filename = filelist[1]
        filepath = 'Z:\\INOS\\'+pc_name+'\\'+filename
        
        data = pd.read_csv(filepath,sep=',', header=0)
        data = pd.DataFrame(data,columns=['Time','Function','Model','Process','TCP X','TCP Y'])
        measdata = data[data['Function']=='Fitting']
        measdata = measdata[measdata.Model.str.contains(robotname)]
        
        fulldata = pd.concat([fulldata, measdata],axis=0)
    
    date_obj = dt.datetime.strptime(date, '%Y-%m-%d').date()
    date_obj = date_obj - dt.timedelta(days = 1)
    date = date_obj.strftime('%Y-%m-%d')
    filelist = []
    points = len(fulldata.Time)
    
fulldata = fulldata.sort_values(by=['Time'],ascending=False)
fulldata = fulldata.head(num_points)
norms = np.linspace(0,1,num_points)
norms = norms.tolist()

"""
Split between both functions
"""

tcpx = fulldata['TCP X'].tolist()
tcpx = reversed(tcpx)
tcpy = fulldata['TCP Y'].tolist()
tcpy = reversed(tcpy)
val = zip(tcpx,tcpy,norms)

cmap1 = plt.cm.plasma
fig, ax = plt.subplots()
plt.title('Stud Center Measurements')
#for x,y,norm in val:
#    ax.plot(x,y,marker=".",color=cmap1(norm))
fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=cmap1),
              ax=ax, label="Recency (1 is Most Recent)")


rad = 1
circle1 = plt.Circle((0,0),rad, color='r',fill=False)
ax.add_patch(circle1)


plt.xlim([rad*-1.2,rad*1.2])
plt.ylim([rad*-1.2,rad*1.2])

ax.set_aspect('equal')
ax.set_xlabel("TCP X position [mm]")
ax.set_ylabel("TCP Y position [mm]")
plt.savefig('default.png', dpi=300)