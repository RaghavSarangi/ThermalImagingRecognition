import os
import tkinter as tk
from PIL import Image, ImageTk
from classesMCR import *
from displayRegions import annotateImage, generateCombinedRegionImage
from tkinter import BOTTOM, LEFT, RIGHT, TOP, Toplevel, filedialog as fd
import matplotlib.pyplot as plt


### Helper Functions
def dateDifference(date1, date2):
    firstSlash1 = date1.find("/")
    secondSlash1 = date1.find("/", firstSlash1 + 1)
    substring1 = date1[firstSlash1+1 : secondSlash1]
    firstSlash2 = date2.find("/")
    secondSlash2 = date2.find("/", firstSlash2 + 1)
    substring2 = date2[firstSlash2+1 : secondSlash2]
    return int(substring1) - int(substring2)

class TimeStamp:

    def __init__(self, timeString):
        timeBits = timeString.split(":")
        self.hour = timeBits[0]
        self.minute = timeBits[1]
        self.second = timeBits[2]       
    
    def getTime(self):
        return ":".join([self.hour, self.minute, self.second])
    
    def timeDifference(self, otherTime):
        assert isinstance(otherTime, TimeStamp)
        hour_diff = int(self.hour) - int(otherTime.hour)
        minute_diff = int(self.minute) - int(otherTime.minute)
        second_diff = int(self.second) - int(otherTime.second)
        return hour_diff*3600 + minute_diff*60 + second_diff

class runStage:

    def __init__(self, folderPath):
        self.folderPath = folderPath
        # elements = folderPath.split(sep="/")
        # dateTime = elements[-1].split(sep="_")
        # self.runDate  = "/".join(dateTime[:3])
        # self.runTime = TimeStamp(":".join(dateTime[-4:-1]))

        all_files = os.listdir(folderPath)  
        csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
        csv_files.remove("dataset.csv")
        csv_files.sort()
        self.Files = csv_files

    def getLastFile(self):
        return sorted(self.Files)[-1]
    
    def getBathTemp(self):
        return self.folderPath.split(sep="/")[-1].split(sep="_")[-1]
    
    def getFileDateTimes(self):
        FileDateTimes = []
        for i in range(len(self.Files)):
            date_constructor = self.Files[i].split("_")
            date_constructor[2] = "20" + date_constructor[2]
            date = "/".join(date_constructor[:3]) 
            time = TimeStamp(":".join(self.Files[i].split("_")[3:6]))
            FileDateTimes.append((date, time))
        return FileDateTimes

    def getAbsTimeOfFilesInStage(self, genesisDate, genesisTime):
        assert isinstance(genesisTime, TimeStamp)
        self.absTimesArray=[]
        for tuple in self.getFileDateTimes():
            timeAddedDueToDaysInBetween = dateDifference(tuple[0], genesisDate) * 86400
            self.absTimesArray.append(-(genesisTime.timeDifference(tuple[1])) + timeAddedDueToDaysInBetween)
        return self.absTimesArray

def makeRegionsSeparatelyArray(regionsList, matrix, sizeLimit):
    """Produces several [relevant] images, each with an individual region highlighted along with relevant information."""
    assert isinstance(matrix, Matrix)
    for region in regionsList:
        assert isinstance(region, Region) 
    imageArray = []
    shortlistedRegions = []
    mainImage = generateCombinedRegionImage(regionsList, matrix)
    for region in regionsList:
        if region.getSize()>sizeLimit: #a minimum pixel amount has been instituted to prevent small regions from being printed
            img = mainImage.copy()
            pixels = img.load()
            for cell in region.getCells():
                pixels[cell.getCol(),cell.getRow()] = (255,255,255)
            # img.show()
            imageArray.append(img)
            shortlistedRegions.append(region)
    return shortlistedRegions, imageArray

def selectFiletoChooseRegionToFocus():
    global startDate
    global startTime
    global mainTRARunDirectoryPath

    filetypes = (('csv files', '*.csv'),)
    
    filename = fd.askopenfilename(
        title='Open a CSV file',
        initialdir='/Users/Raghav1/ConnectWiseControl/Files',
        filetypes=filetypes)

    print()
    folderName = os.path.dirname(filename)
    print("File:", os.path.basename(filename))
    print("Directory:", folderName)
    print()
    mainTRARunDirectoryPath = "/".join(folderName.split("/")[:-1])
    allFolders = os.listdir(mainTRARunDirectoryPath)
    allFolders.sort()
    allFolders.remove(".DS_Store")
    startfolderName = mainTRARunDirectoryPath + "/" + allFolders[0]
    print("Start Folder Chosen:", startfolderName)
    startDate, startTime = runStage(startfolderName).getFileDateTimes()[0]
    print("Run Start Date:", startDate, "\nRun Start Time:", startTime.getTime())

    matrix = Matrix(filename)
    output = makeRegionsSeparatelyArray(matrix.identifyRegions(0.002), matrix, 1000)
    OpenImageSelector(output[0], output[1], matrix)

def OpenImageSelector(regionsArray, imageArray, matrix):
    def next():
        global imageIndex

        img2 = compatibleImageList[imageIndex + 1]
        label.configure(image=img2)
        imageIndex +=1
        if imageIndex == len(compatibleImageList) - 1:
            button_forward["state"] = tk.DISABLED
        button_back["state"] = tk.NORMAL
    
    def previous():
        global imageIndex

        img2 = compatibleImageList[imageIndex - 1]
        label.configure(image=img2)
        imageIndex -=1
        if imageIndex == 0:
            button_back["state"] = tk.DISABLED
        button_forward["state"] = tk.NORMAL
    
    def exit():
        newWindow.withdraw()
        newWindow.quit()
    
    def choose():
        global imageIndex

        chosenRegion = regionsArray[imageIndex]
        # print("Region chosen:", chosenRegion)
        # img = showRegionsSeparatelyArray([chosenRegion], matrix)[1][0]
        # annotateImage(img, chosenRegion)
        # img.show()
        newMatrix = ForcedMatrix(chosenRegion, matrix)
        output = makeRegionsSeparatelyArray(newMatrix.identifyRegions(0.0008), newMatrix, 5)
        OpenImageSelector2(output[0], output[1], newMatrix)
        newWindow.withdraw()
        newWindow.quit()
    
    
    newWindow = Toplevel(root)
    newWindow.title("Image Selector")
    newWindow.geometry("800x600")
    compatibleImageList = [ImageTk.PhotoImage(img, master = newWindow) for img in imageArray]

    label = tk.Label(newWindow, image=compatibleImageList[imageIndex])
    label.pack(side=TOP, expand=True)

    button_forward = tk.Button(newWindow, text="Next", command= next)
    button_back = tk.Button(newWindow, text="Previous", command= previous, state= tk.DISABLED)
    button_exit = tk.Button(newWindow, text="Exit", command= exit, bg='#ffb3fe', fg = 'red')
    button_choose = tk.Button(newWindow, text="Choose", command= choose)

    button_back.pack(side= LEFT)
    button_forward.pack(side=RIGHT)
    button_exit.pack(side=BOTTOM)
    button_choose.pack(side=BOTTOM)
    
    newWindow.mainloop()

def OpenImageSelector2(regionsArray, imageArray, matrix):
    assert isinstance(matrix, ForcedMatrix)

    def next():
        global imageIndex2

        img2 = compatibleImageList[imageIndex2 + 1]
        label.configure(image=img2)
        imageIndex2 +=1
        if imageIndex2 == len(compatibleImageList) - 1:
            button_forward["state"] = tk.DISABLED
        button_back["state"] = tk.NORMAL
    
    def previous():
        global imageIndex2

        img2 = compatibleImageList[imageIndex2 - 1]
        label.configure(image=img2)
        imageIndex2 -=1
        if imageIndex2 == 0:
            button_back["state"] = tk.DISABLED
        button_forward["state"] = tk.NORMAL
    
    def exit():
        newWindow.withdraw()
        newWindow.quit()
    
    def choose():
        global imageIndex2

        chosenRegion = regionsArray[imageIndex2]
        # print("Region chosen:", chosenRegion)
        # img = makeRegionsSeparatelyArray([chosenRegion], matrix, 0)[1][0]
        # annotateImage(img, chosenRegion)
        # img.show()
        newWindow.withdraw()
        data = getAxesOfRunawayPlot(chosenRegion, matrix)
        XArray = data[0]
        YArray = data[1]
        assert len(XArray) == len(YArray)
        # print(XArray, "\n") 
        # print(YArray)
        plt.plot(XArray, YArray)
        plt.xlabel('Bath Temp. (°C)')
        # plt.xlabel('Runtime (s)')
        plt.ylabel('Region Temp. - Bath Temp. (°C)')
        plt.title('Thermal Runaway')
        plt.show()
        newWindow.quit()

    
    newWindow = Toplevel(root)
    newWindow.title("Module Region Selector")
    newWindow.geometry("500x300")
    compatibleImageList = []
    for img in imageArray:
        imageToAppend = ImageTk.PhotoImage(img, master = newWindow)
        imageToAppend = imageToAppend._PhotoImage__photo.zoom(4)
        compatibleImageList.append(imageToAppend)

    label = tk.Label(newWindow, image=compatibleImageList[imageIndex2])
    label.pack(side=TOP, expand=True)

    button_forward = tk.Button(newWindow, text="Next", command= next)
    button_back = tk.Button(newWindow, text="Previous", command= previous, state= tk.DISABLED)
    button_exit = tk.Button(newWindow, text="Exit", command= exit, bg='#ffb3fe', fg = 'red')
    button_choose = tk.Button(newWindow, text="Choose", command= choose)

    button_back.pack(side= LEFT)
    button_forward.pack(side=RIGHT)
    button_exit.pack(side=BOTTOM)
    button_choose.pack(side=BOTTOM)
    
    newWindow.mainloop()

def avgTempSnapshot(file, region, forcedMatrix):
    assert isinstance(forcedMatrix, ForcedMatrix)
    assert isinstance(region, Region)

    offset_x = forcedMatrix.getXOffset()
    offset_y = forcedMatrix.getYOffset()

    # print("CornerCoordinates: (", region.upperBorderRow() + offset_x, ",", region.leftBorderCol() + offset_y, ") , (", region.lowerBorderRow() + offset_x, ",", region.rightBorderCol() + offset_y, ")", sep="")
    
    fileMatrix = Matrix(file)
    amount = mean(fileMatrix.getCell(cell.getRow() + offset_x, cell.getCol() + offset_y).getVal() for cell in region.getCells())
    return round(amount, 3)

def getAxesOfRunawayPlot(region, newMatrix):
    assert isinstance(newMatrix, ForcedMatrix)

    x_axis_array = []
    y_axis_array = []
    allBathTemps = os.listdir(mainTRARunDirectoryPath)
    allBathTemps.sort()
    allBathTemps.remove(".DS_Store")
    for folder in allBathTemps:
        folderPath = mainTRARunDirectoryPath + "/" + folder
        stage = runStage(folderPath)
        bathTempValue = float(stage.getBathTemp()[:-1])

        x_axis_array.append(bathTempValue) #To get rid of the C
        file = stage.getLastFile()
        fileName = folderPath + "/" + file
        y_axis_array.append(avgTempSnapshot(fileName, region, newMatrix)-bathTempValue)

        ### TO PRODUCE A TEMPERATURE VS TIME GRAPH, REPLACE THE 4 LINES ABOVE WITH THESE
        # x_axis_array.extend(stage.getAbsTimeOfFilesInStage(startDate, startTime))
        # for file in stage.Files:
        #     fileName = folderPath + "/" + file
        #     y_axis_array.append(avgTempSnapshot(fileName, region, newMatrix))
    return x_axis_array, y_axis_array

imageIndex = 0 
imageIndex2 = 0
mainTRARunDirectoryPath = ""

root = tk.Tk()
root.title("Zooming Mechanism")
root.geometry("450x225")

open_button = tk.Button(root, text='Open a File', command=selectFiletoChooseRegionToFocus)
exit_button = tk.Button(root,text='Exit', command=lambda: root.quit(), bg='#ffb3fe', fg = 'red')

open_button.pack(expand=True)
exit_button.pack(expand=True)

root.mainloop()