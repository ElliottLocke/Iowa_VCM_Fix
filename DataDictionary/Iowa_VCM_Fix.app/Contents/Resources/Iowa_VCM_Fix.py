'''
Created on Oct 16, 2013
Iowa VCM Fix
This script fixes the deliverables for Iowa to match the Data Dictionary.    
It creates the Measurement Table
@author: Elliott Locke
'''

import easygui as eg
import os, sys
from Tkinter import Tk
from tkFileDialog import askopenfilename
import MySQLdb
import csv

def main():
    #____________________ Username and password ________________________
    Username, Password = eg.multpasswordbox(msg = "Enter your username and password", title = "2013iowavcm Database log in", fields = ["Username: ", "Password: "])

    #__________________ Connect to the Database __________________
    db = dbConnect("isis.roadview.com", Username, Password, "2013iowavcm")
    
    #___________Get the file path for the CSV file from the workstation __________________
    Tk().withdraw() #Not a full GUI so we take this part out.  A random box pops up without this line.  Maybe easygui next time for the input.
    titlePrep = "Choose your Measurement Table CSV File"
    messagePrep = "This script will fix the Measurement Table's CSV file from Workstation for the delivery to Iowa."
    filePath = askopenfilename(title = titlePrep, message = messagePrep) #This will open a folder for the user to open a file.  
    
    #__________________ Create the new text csv file name __________________
    csv_text_file_name = os.path.basename(filePath)
    basename = os.path.basename(csv_text_file_name).rsplit('.', 1)
    newtextcsv = os.path.join(os.path.dirname(filePath), ".".join([basename[0]+ "_new", basename[1]]))
    
    #__________________ Open the original Measurement table file __________________
    textCSV = readCSV(filePath)
    textCSV.pop(0) # take out that first line.  
    
    newtextcsvfile = open(newtextcsv, "w")
    
    #first row in the CSV file:
    newtextcsvfile.write("VC_ID, Structure_Number, Struccode, Latitude, Longitude, Direction, LEP_Vertical_Clearance_FT, LEP_Vertical_Clearance_IN, Lane_1_Vertical_Clearance_FT, Lane_1_Vertical_Clearance_IN, Lane_2_Vertical_Clearance_FT, Lane_2_Vertical_Clearance_IN, Lane_3_Vertical_Clearance_FT, Lane_3_Vertical_Clearance_IN, Lane_4_Vertical_Clearance_FT, Lane_4_Vertical_Clearance_IN, Lane_5_Vertical_Clearance_FT, Lane_5_Vertical_Clearance_IN, Lane_6_Vertical_Clearance_FT, Lane_6_Vertical_Clearance_IN, Lane_7_Vertical_Clearance_FT, Lane_7_Vertical_Clearance_IN, Lane_8_Vertical_Clearance_FT, Lane_8_Vertical_Clearance_IN, REP_Vertical_Clearance_FT, REP_Vertical_Clearance_IN, Oversize_Horizontal_Clearance_FT, Oversize_Horizontal_Clearance_IN, Posted_Height_FT, Posted_Height_IN, Date_Processed, Date_Collected, Invalid_Struccode")
    newtextcsvfile.write('\n') # new line after the header
    
    #______________________Write the rest of the lines based off of the rows in the textCSV file (Measurement Table)__________________________
    for row in textCSV:
        Structure_Number = (row[0])
        Struccode = (row[1])
        statement = "SELECT VC_ID FROM iowa_structures WHERE FHWANUM = '" + Structure_Number + "' AND STRUCCODE = '" + Struccode + "'"
        queryreturn = sqlToList(statement, db)[0] #get the only item in the list.
        newtextcsvfile.write(str(queryreturn)) # write in the VC_ID number
        
        newtextcsvfile.write(" , " + Structure_Number) # write it to the file
        newtextcsvfile.write(" , " + Struccode)
        newtextcsvfile.write(" , " + row[6])  # Latitude
        newtextcsvfile.write(" , " + row[7])  # Longitude
        newtextcsvfile.write(" , " + row[8])  # Direction
        
        # Lane heights in FT and IN
        for colnum in range(15, 25):  # range stops before the last number.  (the colnums only go up to 24.)  
            if row[colnum] == "":
                newtextcsvfile.write(" , " + " ")
                newtextcsvfile.write(" , " + " ")
            else:
                feet = row[colnum].split('.', 1)[0]
                inches = float("0." + row[colnum].split('.', 1)[1])*12
                newtextcsvfile.write(" , " + str(feet))
                newtextcsvfile.write(" , " + str(inches))
        
        # Oversize_Horizontal_Clearance_FT and IN
        if row[13] == "":                       
            newtextcsvfile.write(" , " + "")
            newtextcsvfile.write(" , " + "")
        else:
            feet = row[13].split('.', 1)[0]
            inches = float("0." + row[13].split('.', 1)[1])*12
            newtextcsvfile.write(" , " + str(feet))
            newtextcsvfile.write(" , " + str(inches))
        
        newtextcsvfile.write(" , " + row[9])  # Posted_Height_FT
        newtextcsvfile.write(" , " + row[10])  # Posted_Height_IN
        newtextcsvfile.write(" , " + row[11])  # Date Processed
        newtextcsvfile.write(" , " + row[12])  # Date Collected
        newtextcsvfile.write(" , " + row[3])  # Invalid_Struccode
        newtextcsvfile.write('\n')
            
    newtextcsvfile.close()
    
    eg.msgbox(msg = "Measurement Table Completed", title = "Measurement Table")
    
#___________________________________ Earl's readCSV file ___________________________________
def readCSV(path):
    data = list(csv.reader(open(path, 'rU')))
    return data

#____________________________________EARL's DB functions____________________________________

def dbConnect(inputHost,inputUser,inputPasswd,inputDB):

#     Create connection information for MySQLdb module.
#     
#     @type inputHost: string
#     @param inputHost: MySQL host machine or ip.
#     
#     @type inputUser: string
#     @param inputUser: MySQL username
# 
#     @type inputPasswd: string
#     @param inputPasswd: MySQL password.
# 
#     @type inputPasswd: string
#     @param inputPasswd: MySQL database.
#     
#     @rtype:  MySQLdb connect
#     @return: Return MySQLdb connection information.

    try:
        db = MySQLdb.connect(host=inputHost, user=inputUser, passwd =inputPasswd, db = inputDB)
    except:
        eg.msgbox("You entered in the incorrect username or password.")
        raise SystemExit
    return db
    
def sqlToList(statement,db):
    
#     Return a SQL select statement as a list.
#     
#     @type statement: string
#     @param statement: SQL select statement.
#     
#     @type db: MySQLdb connect
#     @param db: Need to include the database login information, the roadview package creates and runs
#     the required queries.
#     
#     @rtype:  list
#     @return: A list containing the data returned from the SELECT statement.
    
    cursor = db.cursor()
    cursor.execute(statement)
    outList = []
    if "SQLite" in db.__doc__:
        for x in cursor.fetchall():
            outList.append(x) 
    else:
        numrows = int(cursor.rowcount)
        for x in range(0,numrows):
            row = cursor.fetchone()
            if row != None:
                if len(row) == 1:
                    row = str(row[0])
                else:
                    row = list(row)
                outList.append(row)
    cursor.close()
    return outList


if __name__ == '__main__':
    main()
    sys.exit()