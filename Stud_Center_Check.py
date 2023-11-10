# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 08:31:25 2022

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
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from RangeSlider.RangeSlider import RangeSliderH 
import tkinter as tk
from tkinter import LEFT, BOTH, X
import sys
import math


#presetting data
glob_data = None
glob_norms = None
sc = None
cur_pc = ''
cur_robot = '99' 
cur_num = 0
cur_rad = 0 
cur_date = '2099-12-31'

#GUI window    
window = Tk()

#creates main frames and the nested frames within them
picframe = Frame()

settingsframe = Frame()

subsettingsframe = Frame(settingsframe)

pcframe = Frame(subsettingsframe)

robframe = Frame(subsettingsframe)

numframe = Frame(subsettingsframe)

radframe = Frame(subsettingsframe)

calframe = Frame(settingsframe)

sliderframe = Frame(settingsframe)

dateframe = Frame(settingsframe)

recentframe = Frame(settingsframe)

#creating the default graph for when no data selected
#creates the colormap
cmap1 = plt.cm.plasma
#creates the figure, axes and sets the figure size
fig, ax = plt.subplots()
plt.rcParams["figure.figsize"] = [15, 15]
#figure title
plt.title('Stud Center Measurements')
#creates color bar
fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=cmap1),
              ax=ax, label="Recency (1 is Most Recent)")

#creates the circle
rad = 1
circle1 = plt.Circle((0,0),rad, color='r',fill=False)
ax.add_patch(circle1)

#creates starting graph limits
plt.xlim([rad*-1.2,rad*1.2])
plt.ylim([rad*-1.2,rad*1.2])

#sets axis properties
ax.set_aspect('equal')
ax.set_xlabel("TCP X position [mm]")
ax.set_ylabel("TCP Y position [mm]")

#initializes annotations for plot
annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="-"))
annot.set_visible(False)

x0 = 0
y0 = 0
x1 = 0
y1 = 0
counter = 0

annotline = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"))
annotline.set_visible(False)

# creating the Tkinter canvas, necessary to place figures in GUIs
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,
                               master = picframe)  
#updates canvas
canvas.draw()

# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack(fill='both',expand=True)

# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas,
                                       picframe)
#updates toolbar
toolbar.update()

# placing the toolbar on the Tkinter window
canvas.get_tk_widget().pack()

#reads in pc names
pc_list = pd.read_excel(r'C:\\Users\\QTD8635.MCBMW1\\Desktop\\Stud Center Quality Check\\Folder List.xlsx')
pc = pc_list['PC Name'].tolist()
rob_list = pc_list['Robots'].tolist()

robot_list = ['Robots']
for row in rob_list:
    if type(row) == str:
        robot_list.append([int(x) for x in row.split(',')])
    else:
        robot_list.append([row])
robot_list = robot_list[1:len(robot_list)]        

#GUI title
window.title('Stud Center Check')

#function reads in data from .txts based on pc, robot, # of points, and date to start from 
def data_input(pc_name, robotnum, num_points, startdate):
    #gets .txt file path
    path = os.listdir('Z:\\INOS\\'+pc_name)
    #config for data read
    robotname = 'R'+str(robotnum)
    filetype = 'Output.Classic'
    #setup for while loop
    filelist = []
    points = 0
    fulldata = pd.DataFrame()
    date = startdate
    #loop to collect points until the limit is reached
    while points < num_points:
        #goes through folder specified by pc name
        for x in path:
            #collects the two output classic files made on the date
            if date in x and filetype in x:
                filelist.append(x) 
        #check to make sure correct files were found
        if bool(filelist):
            #checks which file the robot will be in and sets the file name of the .txt
            if pc_name == '103V5R202040OV1' or pc_name == '10305F331050OV1':
                filename = filelist[0]
            elif pc_name == '10301F331030OV1' or pc_name == '10305F331030OV1':
                filename = filelist[robotnum-1]
            elif pc_name == '10305F331040OV1':
                if robotnum == 2:
                    filename = filelist[1]
                elif robotnum == 3:
                    filename = filelist[2]
                elif robotnum % 2 == 1:
                    filename = filelist[0]
                else: 
                    filename = filelist[3]
            elif pc_name == '10305UC01030OV1' or pc_name == '10305UC01040OV1' or pc_name ==  '10305UC02035OV1' or pc_name == '10305UC02045OV1':
                if robotnum == 6:
                    filename = filelist[2]
                elif robotnum % 2 == 1:
                    filename = filelist[0]
                else:
                    filename = filelist[1]
            else:
                if robotnum % 2 == 1:
                    filename = filelist[0]
                else: 
                    filename = filelist[1]
            #sets the full filepath
            filepath = 'Z:\\INOS\\'+pc_name+'\\'+filename
            #reads in the data from the .txt that is cared about
            #only certain rows and columns are grabbed
            data = pd.read_csv(filepath,sep=',', header=0)
            data = pd.DataFrame(data,columns=['Time','EP-NR','Function','Model','Process','TCP X','TCP Y'])
            measdata = data[data['Function']=='Fitting']
            measdata = measdata[measdata.Model.str.contains(robotname)]
            #adds the data from the .txt file to a list of all points currently grabbed
            fulldata = pd.concat([fulldata, measdata],axis=0)
        
        #converts the date string to a date to go backwards 1 day
        date_obj = dt.datetime.strptime(date, '%Y-%m-%d').date()
        date_obj = date_obj - dt.timedelta(days = 1)
        #converts back to a date
        date = date_obj.strftime('%Y-%m-%d')
        #updates variables for next iteration of while loop
        filelist = []
        points = len(fulldata.Time)
    
    #sorts the data so the most recent points are on the top    
    fulldata = fulldata.sort_values(by=['Time'],ascending=False)
    #cuts off the points to the specified number ie 1020 points collected, cut down to 1000 points
    fulldata = fulldata.head(num_points)
    #sets the values for the colormap
    norms = np.linspace(0,1,num_points)
    norms = norms.tolist()
    
    #creates an index column for slider
    fulldata.index = range(len(fulldata.index))
    fulldata = fulldata.reset_index(drop=False)
    
    #returns values needed for the plots to work
    return fulldata, norms;

#function plots the points collected as well as the limit circle    
def plot_data(fulldata, rad, norms):
    #global variables to allow the function to overwrite the existing plot if it exists
    global fig
    global canvas
    global toolbar
    global ax
    global cmap1
    global sc
    global annot
    global annotline
    global norm
    global tcpx
    global tcpy
    
    #gets the TCP X data from the the input
    tcpx = fulldata['TCP X'].tolist()
    #reverses the list so that the most recent points will be plotted last, allows them to appear above old points

    tcpx.reverse()
    #same but for Y data
    tcpy = fulldata['TCP Y'].tolist()

    tcpy.reverse()
    
    flipnorms = norms
    #flipnorms.reverse()
    
    #clears any existing plot
    if sc is not None:
        sc.remove()
    ax.clear()
    
    #reapplies setup values
    cmap1 = plt.cm.plasma
    plt.rcParams["figure.figsize"] = [15, 15]
    plt.title('Stud Center Measurements')
    
    #creates colors for scatter plot
    norm = plt.Normalize(0,1)
    
    #creates scatter plot
    sc = plt.scatter(tcpx,tcpy,c=flipnorms, cmap=cmap1, norm=norm,marker=".")

    #get the max values from the points in x and y
    yabs_max = abs(max(ax.get_ylim(), key=abs))
    xabs_max = abs(max(ax.get_xlim(), key=abs))
    
    #plots circle
    circle1 = plt.Circle((0,0),rad, color='r',fill=False)
    ax.add_patch(circle1)
    
    #applies the appropriate limits
    #either uses largest of the circle radius or the x and y max points
    if rad >= yabs_max and rad>= xabs_max:
        plt.xlim([rad*-1.2,rad*1.2])
        plt.ylim([rad*-1.2,rad*1.2])
    elif yabs_max >= xabs_max and yabs_max > rad:
        plt.xlim([yabs_max*-1.2,yabs_max*1.2])
        plt.ylim([yabs_max*-1.2,yabs_max*1.2])
    elif xabs_max > yabs_max and xabs_max > rad:
        plt.xlim([xabs_max*-1.2,xabs_max*1.2])
        plt.ylim([xabs_max*-1.2,xabs_max*1.2])
    
    #reapplies the setup values
    ax.set_aspect('equal')
    ax.set_xlabel("TCP X position [mm]")
    ax.set_ylabel("TCP Y position [mm]")
    
    #recreates annotation that gets deleted by ax.clear()
    annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="-"))
    annot.set_visible(False)
    
    annotline = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"))
    annotline.set_visible(False)
    
    
    #redraws the canvas
    canvas.draw()
      
    #updates the toolbar 
    toolbar.update()
      
    #saves the figure in case    
    plt.savefig('filename.png', dpi=300)
    


#function to control the other functions on button press and to help speed up computations    
def det_action(new_pc, new_robot, new_num, new_rad, new_date):
    #confirmation that button click worked
    print('loading...')
    #global variables to allow the function to keep track of values outside of it
    global glob_data 
    global glob_norms
    global cur_pc
    global cur_robot
    global cur_num
    global cur_rad
    global cur_date
    global img
    global sliderMax
    global slider
    global hVar1
    global hVar2
    #converts the date from the calendar to the format expected
    date_obj = dt.datetime.strptime(new_date, '%m/%d/%y').date()
    new_date = date_obj.strftime('%Y-%m-%d')
    
    #if the circle radius changes, just replot with new circle
    if new_rad != cur_rad and (new_pc == cur_pc and new_robot == cur_robot and new_num == cur_num and new_date == cur_date):
        #plots with same data new radius
        plot_data(glob_data,new_rad,glob_norms)
        
        
        #confirmation the plot was successful
        print('image created')
    #if the number of points was reduced but everything else was the same, the data just gets truncated to the new number and replots
    elif new_num < cur_num and new_pc == cur_pc and new_robot == cur_robot and new_date == cur_date:
        #truncates data to new number
        glob_data = glob_data.head(new_num)
        glob_norms =  np.linspace(0,1,new_num)
        glob_norms = glob_norms.tolist()
        #replots the graph
        plot_data(glob_data,new_rad,glob_norms)
        
        
        #confirmation the plot was successful
        print('image created')
    #any other case, it gets new data and plots it
    else:
        #gets new data with new parameters
        glob_data,glob_norms = data_input(new_pc,new_robot,new_num,new_date)
        #plots the data
        plot_data(glob_data,new_rad,glob_norms)
        
        
        #confirmation the plot was successful
        print('image created')
    
    #sets the current values to the new ones for consistency
    cur_pc = new_pc
    cur_robot = new_robot
    cur_num = new_num
    cur_rad = new_rad
    cur_date = new_date   
    
    #gets rid of exisitng slider
    slider.pack_forget()
    #makes a new slider with correct endpoints
    sliderMax=cur_num-1
    hVar1 = IntVar()
    hVar2 = IntVar()
    slider = RangeSliderH( sliderframe , [hVar1, hVar2], min_val=0,max_val=sliderMax, padX=30, digit_precision='.0f' )   #horizontal
    
    #creates triggers for when the slider is changed
    hVar1.trace_add('write', update_plot)
    hVar2.trace_add('write', update_plot)
    slider.pack()
    update_plot()
    
    date = glob_data['Time'].tolist()
    date.reverse()
    epnr = glob_data['EP-NR'].tolist()
    epnr.reverse()
    
    for i in range(1,6):
        text = "({},{}), {}, {}".format(tcpx[cur_num-i],
                                      tcpy[cur_num-i],
                                      date[cur_num-i],
                                      epnr[cur_num-i])
        if i == 1:
            label_recent1.configure(text=text)
        elif i == 2:
            label_recent2.configure(text=text)
        elif i == 3:
            label_recent3.configure(text=text)
        elif i == 4:
            label_recent4.configure(text=text)
        elif i == 5:
            label_recent5.configure(text=text)
            
    

#function to get new annotation values based on the point that is hovered over
def update_annot(ind):
    #gets the left value of the slider
    [lval,rval] = slider.getValues()
    lval = round(lval)    
    #creates lists of the annotation data
    date = glob_data['Time'].tolist()
    date.reverse()
    epnr = glob_data['EP-NR'].tolist()
    epnr.reverse()
    index = glob_data['index'].astype(str)
    index = index.tolist()
    x = [str(i) for i in tcpx]
    y = [str(i) for i in tcpy]
    #gets and sets the position for the annotation
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    #the annotation message
    text = "({},{})\n{}, {}, {}".format(" ".join(x[n+lval] for n in ind["ind"]),
                                      " ".join(y[n+lval] for n in ind["ind"]),
                                      " ".join(index[n+lval] for n in ind["ind"]), 
                                      " ".join([date[n+lval] for n in ind["ind"]]),
                                      " ".join([epnr[n+lval] for n in ind["ind"]]))
    #sets the annotation message
    annot.set_text(text)
    #formatting for annotation box
    annot.get_bbox_patch().set_alpha(0.4)

#function to determine annotation behavior based on mouse position
def hover(event):
    #checks to only fire if points have been plotted
    if sc is not None:
        #makes vis equal to the visibility of the annotation
        vis = annot.get_visible()
        #checks if the mouse is moved within the plot
        if event.inaxes == ax:
            #sets values based on whether the event occured within the scatterplot
            cont, ind = sc.contains(event)
            #if the event occured within the scatterplot
            if cont:
                #updates the annotation and makes it visible
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            #if it did not
            else:
                #checks if the annotation is visible
                if vis:
                    #turns the annotation off
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

#function to change which points are shown based off the slider values
def update_plot(*args):
    #global value to allow sc to be changed
    global sc
    #gets the current values of the slider and converts them to ints
    [lval,rval] = slider.getValues()
    lval = round(lval)
    rval = round(rval)
    #gets the list of points within the values
    x = tcpx[lval:(rval+1)]
    y = tcpy[lval:(rval+1)]
    #gets rid of the old points
    sc.remove()
    #adds the points within the range back
    sc = plt.scatter(x,y,c=glob_norms[lval:(rval+1)], cmap=cmap1, norm=norm,marker=".") 
    #redraws the canvas
    canvas.draw()
      
    #updates the toolbar 
    toolbar.update()
    
    date = glob_data['Time'].tolist()
    date.reverse()
    label_sliderl.configure(text=date[lval])
    label_sliderr.configure(text=date[rval])

def pc_change(*args):
    #removes title
    drop_robot['menu'].delete(0,'end')
    #figures out what pc was clicked
    idx = pc.index(clicked_pc.get())
    
    #gets the choices for the pc selected
    new_choices = robot_list[idx]
    #sets default
    clicked_robot.set(min(new_choices))
    #adds new choices
    for choice in new_choices:
        drop_robot['menu'].add_command(label=choice, command= tk._setit(clicked_robot, choice))

def on_closing():
    #closes window and ends program
    window.destroy()
    sys.exit()

def getDistance(event):
    global counter, x0, y0, x1, y1, line
    if counter == 0:
        x0 = event.xdata
        y0 = event.ydata
        counter += 1
    elif counter == 1:
        x1 = event.xdata
        y1 = event.ydata
        distance = math.sqrt(((x0 - x1)**2)+((y0 - y1)**2))
        #print(distance)
        line = ax.plot([x0, x1], [y0, y1])
        #sets the annotation message
        annotline.set_text(round(distance,3))
        #formatting for annotation box
        annotline.get_bbox_patch().set_alpha(0.4)
        annotline.xy = [(x1+x0)/2,(y1+y0)/2]
        annotline.set_visible(True)
        canvas.draw_idle()
        counter += 1
        
    elif counter == 2:
        counter = 0
        ax.lines.remove(line[0])
        annotline.set_visible(False)
        canvas.draw_idle()
        

    

cid = fig.canvas.mpl_connect('button_press_event', getDistance)

#sets a trigger for mouse movement within the figure
fig.canvas.mpl_connect("motion_notify_event", hover)

# datatype of menu text
clicked_robot = IntVar()
  
# initial menu text
clicked_robot.set( 1 )

choices =  [1,2,3,4]

# Create Dropdown menu
drop_robot = OptionMenu( robframe , clicked_robot , *choices )
  
# datatype of menu text
clicked_pc = StringVar()

  
# initial menu text
clicked_pc.set('103V5F314150OV1')
  
clicked_pc.trace('w',pc_change)

# Create Dropdown menu
drop_pc = OptionMenu( pcframe , clicked_pc , *pc )

#datatype of entry text
num_var = IntVar()
#default value
num_var.set(1000)

#create # of points entry
num_entry = Entry( numframe , textvariable = num_var)

#datatype of entry text
rad_var = IntVar()
#default value
rad_var.set(1)

#create rad entry
rad_entry = Entry( radframe, textvariable = rad_var)

#labels for all the inputs
label_robot = Label(robframe ,
                          text = "Robot Number")
label_pc = Label(pcframe,
                          text = "PC Name")
label_num = Label(numframe,
                          text = "Number of Points")
label_rad = Label(radframe,
                          text = "Radius [mm]")

label_slider = Label(sliderframe,
                     text = "Adjust points shown (higher numbers are more recent points)")

label_sliderl = Label(dateframe,
                      text = "Earliest Date")

label_sliderr = Label(dateframe,
                      text = "Latest Date")

#labels for recents

label_recent_title = Label(recentframe,
                           text = "5 Most Recent Points:")

label_recent1 = Label(recentframe,
                      text = "Point 1")

label_recent2 = Label(recentframe,
                      text = "Point 2")

label_recent3 = Label(recentframe,
                      text = "Point 3")

label_recent4 = Label(recentframe,
                      text = "Point 4")

label_recent5 = Label(recentframe,
                      text = "Point 5")

#create calendar
cal = Calendar(calframe, selectmode = 'day')

#calendar label
label_cal = Label(calframe,
                          text = "Start Date (Calculates Backwards)")

#output button
button_pic = Button(settingsframe,
                      text = "Go!",
                      command = lambda: det_action(clicked_pc.get(),clicked_robot.get(),int(num_entry.get()),float(rad_entry.get()),cal.get_date()))

#datatype of sliders
hVar1 = IntVar()  #left handle variable
hVar2 = IntVar()  #right handle variable
#starting value which is equal to highest index point that would be associated with the default 1000 points
sliderMax=999

#creates the slider
slider = RangeSliderH( sliderframe , [hVar1, hVar2], min_val=0,max_val=sliderMax, padX=30, digit_precision='.0f' )   #horizontal

#creates triggers for when the slider is changed
hVar1.trace_add('write', update_plot)
hVar2.trace_add('write', update_plot)


label_recent_title.pack()
label_recent1.pack()
label_recent2.pack()
label_recent3.pack()
label_recent4.pack()
label_recent5.pack()

#packs the widgets into their respective frames with label on top then item
label_pc.pack()
drop_pc.pack()

label_robot.pack()
drop_robot.pack()

label_num.pack()
num_entry.pack()

label_rad.pack()
rad_entry.pack()

label_cal.pack()
cal.pack()

label_slider.pack()

slider.pack()

label_sliderl.grid(column =1, row =1, padx = 30)
label_sliderr.grid(column =2, row =1, padx = 30)

#assigns widget frames to their position in the subsetting frame
pcframe.grid(column = 1, row = 1)

robframe.grid(column = 2, row =1)

numframe.grid(column = 1, row = 2)

radframe.grid(column = 2, row = 2)

#packs subsetting frame, calendar, and button in settings frame
recentframe.pack()

subsettingsframe.pack()

calframe.pack()

button_pic.pack()

sliderframe.pack()

dateframe.pack()

#arranges picture and settings frames
picframe.pack(side=LEFT, fill=BOTH, expand=True)

settingsframe.pack(side=LEFT)

#settingsframe.pack()

window.protocol("WM_DELETE_WINDOW", on_closing)
#main loop
window.mainloop()

#sys.exit(1)
