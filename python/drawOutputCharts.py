import matplotlib.pyplot as plt
# tkinter module for importing a file via a dialog box (should be crossplatform)
from tkinter import Tk 
from tkinter.filedialog import askopenfilename
 
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing 
filePath1 = askopenfilename() # show an "Open" dialog box and return the path to the selected file 
filePath2 = askopenfilename()
filePath3 = askopenfilename()

xValues1 = []
yValues1 = []
nLine = 0

# Open the chosen file
with open(filePath1, "r") as plottedValues:
    # We remove the first two lines
    for line in plottedValues:
        if nLine < 2:
            nLine += 1
        else:
            # Remove the \n
            line = line.rstrip()
            # Split the line : current year to the left, canopy rate to the right.
            coordinates = line.split(",")
            # We record the values only if they aren't missing, and if current year is 2021 or later.
            if coordinates[0] != "" and int(coordinates[0]) >= 2021 and coordinates[1] != "":
                xValues1.append(int(coordinates[0]))
                yValues1.append(float(coordinates[1]))

xValues2 = []
yValues2 = []
nLine = 0

# Open the chosen file
with open(filePath2, "r") as plottedValues:
    # We remove the first two lines
    for line in plottedValues:
        if nLine < 2:
            nLine += 1
        else:
            # Remove the \n
            line = line.rstrip()
            # Split the line : current year to the left, canopy rate to the right.
            coordinates = line.split(",")
            # We record the values only if they aren't missing, and if current year is 2021 or later.
            if coordinates[0] != "" and int(coordinates[0]) >= 2021 and coordinates[1] != "":
                xValues2.append(int(coordinates[0]))
                yValues2.append(float(coordinates[1]))

xValues3 = []
yValues3 = []
nLine = 0

# Open the chosen file
with open(filePath3, "r") as plottedValues:
    # We remove the first two lines
    for line in plottedValues:
        if nLine < 2:
            nLine += 1
        else:
            # Remove the \n
            line = line.rstrip()
            # Split the line : current year to the left, canopy rate to the right.
            coordinates = line.split(",")
            # We record the values only if they aren't missing, and if current year is 2021 or later.
            if coordinates[0] != "" and int(coordinates[0]) >= 2021 and coordinates[1] != "":
                xValues3.append(int(coordinates[0]))
                yValues3.append(float(coordinates[1]))

#plt.plot(xValues1, yValues1, "green", xValues2, yValues2, "red", xValues3, yValues3, "blue")
plt.plot(xValues1, yValues1, "green", xValues2, yValues2, "red")
#plt.plot(xValues1, yValues1, "green")
plt.yticks(range(6,34,2))
plt.xlabel('Year')
plt.ylabel('Overall canopy rate')
plt.title('Simulated evolution of the overall canopy rate through time.')
plt.legend(["Without new trees", "With new trees"])
plt.grid(True)
plt.show()