# need to open a database to start the mdserver to enable setting of 
# default file options
OpenDatabase("/home/users/hank/kitchen.vtk")

# tell VisIt the data in a PlainText file is a 2D array
# and the first row has variable names
ops=GetDefaultFileOpenOptions("PlainText")
ops["Data layout"]="2D Array"
ops["First row has variable names"]=1
SetDefaultFileOpenOptions("PlainText", ops)

OpenDatabase("/home/users/hank/plain.txt")
name=GetMetaData("/home/users/hank/plain.txt").GetScalars(0).name
if (name != "d"):
    print("The PlainText reader is incorrectly reporting the first variable name as %s" %(name))
else:
    print("Congrats -- the bug is fixed")

import sys
sys.exit()
