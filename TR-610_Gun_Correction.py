# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 13:54:09 2022

@author: QTD8635
"""

import pandas as pd
import zipfile as zp
import cx_Oracle
import os, shutil


#Oracle Database information- first line is database info, second line is makes the connection with the BS_PLANNING_ADMIN user
dsnStr = cx_Oracle.makedsn("apex5usp.w10", "1526", "apex5usp")
con = cx_Oracle.connect(user="BS_PLANNING_ADMIN", password="ii7POij2##nj",dsn=dsnStr)
cur = con.cursor()

#master robot

#unzips folder where file is contained
with zp.ZipFile(r'Y:\G01_G02\_Test_Cell\00tc01_st004_ir001.zip' , 'r') as zip_ref:
    zip_ref.extractall(r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups Test')

#reads in data    
csv_data = pd.read_csv(r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups Test\C\KRC\Roboter\UserFiles\tr610_cor.csv')

#keeps only the most recent correction of each gun
data = csv_data.drop_duplicates(subset=['EquipNum'], keep='last')

#gets rid of empty column causing problems
data = data.drop(data.columns[25], axis=1)
data = data[data.EquipNum != '          ']

#Applies scaling factor to convert data to mm
data['C1Dev_X'] = data['C1Dev_X'].apply(lambda x: x/10.628)
data['C1AftCorX'] = data['C1AftCorX'].apply(lambda x: x/10.628)
data['C1Dev_Y'] = data['C1Dev_Y'].apply(lambda x: x/10.563)
data['C1AftCorY'] = data['C1AftCorY'].apply(lambda x: x/10.563)

data['C2Dev_X'] = data['C2Dev_X'].apply(lambda x: x/1.969)
data['C2AftCorX'] = data['C2AftCorX'].apply(lambda x: x/1.969)
data['C2Dev_Y'] = data['C2Dev_Y'].apply(lambda x: x/1.919)
data['C2AftCorY'] = data['C2AftCorY'].apply(lambda x: x/1.919)

data['C3Dev_X'] = data['C3Dev_X'].apply(lambda x: x/11.114)
data['C3AftCorX'] = data['C3AftCorX'].apply(lambda x: x/11.114)
data['C3Dev_Y'] = data['C3Dev_Y'].apply(lambda x: x/11.297)
data['C3AftCorY'] = data['C3AftCorY'].apply(lambda x: x/11.297)

data['C4Dev_X'] = data['C4Dev_X'].apply(lambda x: x/9.734)
data['C4AftCorX'] = data['C4AftCorX'].apply(lambda x: x/9.734)
data['C4Dev_Y'] = data['C4Dev_Y'].apply(lambda x: x/9.566)
data['C4AftCorY'] = data['C4AftCorY'].apply(lambda x: x/9.566)

#deletes current data in table, commit forces the changes to be applied
cur.execute('DELETE FROM TR_610_MASTER')
con.commit()

#inserts the new data into table row by row
for i,row in data.iterrows():
    sql = 'INSERT INTO TR_610_MASTER VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21,:22,:23,:24,:25)'
    cur.execute(sql,tuple(row))
con.commit()


#reads in file locations
data = pd.read_excel(r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups\TR_610_File_Locations.xlsx')

#for loop empties the folder of the master files
#code copied from stack exchange
folder = r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups Test'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

#creates the empty output dataframe
out = pd.DataFrame({0:['date'],1:['Time'],2:['Gun Number'],3:['X'],4:['Y'],5:['Z'],6:['A'],7:['B'],8:['C'],'Robot':['Robot']})

#goes through every file location and reads in the tr610 csv for every robot
for i,string in data.iterrows():
    #prints the current file location for monitoring purposes
    print(string[0])
    #converts the value in the row to a string
    path = string[0]#.to_string()
    #the conversion process is a bit funky so this keeps the bit we want
    path = path.split('  ',1)
    path = path[0]
    #gets the robot name from the file path using the same method as above
    robotname = path.split('Auto_Backups' ,1)
    robotname = robotname[1]
    robotname = robotname.split('.',1)
    robotname = robotname[0]
    robotname = robotname[1:]
    #extracts all files from the folder located at the file path
    with zp.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups Test')
    #if a tr610 exists it reads in the file or lets you know otherwise
    try:    
        csv_data = pd.read_csv(r'C:\Users\QTD8635.MCBMW1\Desktop\Robot Backups Test\C\KRC\Roboter\UserFiles\tr610_cor.csv',header = None)
    except Exception as e:
            print('Failed to read %s. Reason: %s' % (file_path, e))
    #creates a column the length of the data read in of the robot name
    col = [robotname] * len(csv_data)
    #sets the robot column of the data that was read in with the robot name
    csv_data['Robot'] = col    
    #adds the data from the current tr610 to the output
    out =  pd.concat([out, csv_data], ignore_index=True)  
    #deletes all unzipped files from the folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))    
#renames the columns to match the sql table's column names            
out.rename(columns ={ 0 : 'Date', 1 : 'Time', 2 : 'EquipNum', 3 : 'Corr_X', 4 : 'Corr_Y', 5 : 'Corr_Z', 6 : 'Corr_A', 7 : 'Corr_B', 8 : 'Corr_C'}, inplace=True)
#the header columns from the tr610's get read into the the dataframe so this removes them
out = out[out.Date != 'date']
#converts empty values to something that can be exported to the database
out = out[out.EquipNum != '          ']
out.replace('',)

#clears the table in the database
cur.execute('DELETE FROM TR_610_ROBOTS')
con.commit()

#inserts the new data in table
for i,row in out.iterrows():
    print(row)
    sql = 'INSERT INTO TR_610_ROBOTS VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)'
    cur.execute(sql,tuple(row))
con.commit()


"""
This code was to try and get the charts to display in python rather than on the apex site.
I determined that it would be way easier to do it in APEX as there are 90 guns this could be done for.

"""
# def makePlot(gun):
#     num = 0
#     for i, x in enumerate(arr[:,2]):
#         if x.strip()==gun.strip():
#             num = i
#             break
            
    
#     offsetLabels = ['C1_X','C1_Y','C2_X','C2_Y','C3_X','C3_Y','C4_X','C4_Y']
#     beforeCorr = arr[num,3:11]
#     afterCorr = arr[num,17:25]
    
#     x = np.arange(len(offsetLabels))
#     width = .35
    
#     fig, axs = plt.subplots()
    
#     rects1 = axs.bar(x - width/2, beforeCorr, width, label='Before')
#     rects2 = axs.bar(x + width/2, afterCorr, width, label='After')
    
#     axs.set_ylabel('Offset')
#     axs.set_title('Gun correction Before vs After')
#     axs.set_xticks(x)
#     axs.set_xticklabels(offsetLabels)
#     axs.legend()
    
#     def autolabel(rects):
#         """Attach a text label above each bar in *rects*, displaying its height."""
#         for rect in rects:
#             height = rect.get_height()
#             height = round(height,3)
#             if height > 0: 
#                 axs.annotate('{}'.format(height),
#                         xy=(rect.get_x() + rect.get_width() / 2, height),
#                         xytext=(0, 3),  # 3 points vertical offset
#                         textcoords="offset points",
#                         ha='center', va='bottom')
#             else: 
#                 axs.annotate('{}'.format(height),
#                         xy=(rect.get_x() + rect.get_width() / 2, height),
#                         xytext=(0, -12),  # 3 points vertical offset
#                         textcoords="offset points",
#                         ha='center', va='bottom')
    
    
#     autolabel(rects1)
#     autolabel(rects2)
    
#     fig.tight_layout()
    
# makePlot('BS0180097')


#closes the connection
con.close()