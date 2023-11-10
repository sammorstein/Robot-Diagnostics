# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 07:46:57 2022

@author: QTD8635
"""

import cx_Oracle
dsnStr = cx_Oracle.makedsn("apex5usp.w10", "1526", "apex5usp")
con = cx_Oracle.connect(user="BS_PLANNING_ADMIN", password="ii7POij2##nj",dsn=dsnStr)
print( con.version)
cur = con.cursor()
for row in cur.execute("select * from STUD_COMPARISON_UC_RECORD"):
    print(row)
con.close()