from PIL import Image, ImageFont, ImageDraw
from colour import Color
import numpy as np
from classesMCR import Matrix, Region

### Do NOT override the system's recursion limit unless the recursiveCheck method is being used.
# import sys
# sys.setrecursionlimit(25000)

def showRegions(regionsArray, matrix):
    """Shows the regions identified. Returns True if holders were identified. Else, returns False."""
    assert isinstance(matrix, Matrix)
    for region in regionsArray:
        assert isinstance(region, Region) 

    sortRegions(regionsArray)
    image = generateCombinedRegionImage(regionsArray, matrix)
    image.show()

    # showRegionsSeparately(regionsArray, matrix)

    ### To generate an image with just the holders, change the above to: 
    # successBool, image = generateHoldersImage(regionsArray, matrix).show()
    # image.show()
    # return successBool

def generateHoldersImage(regionsArray, matrix):
    """Generates an image of the holders, if identified. If not, generates an image of all regions identified."""
    assert isinstance(matrix, Matrix)
    for region in regionsArray:
        assert isinstance(region, Region) 

    holderA, holderB = findHolders(regionsArray)  
    if holderA != 0 :
        image = generateCombinedRegionImage([holderA,holderB], matrix)
        return True, image
    else:
        image = generateCombinedRegionImage(regionsArray, matrix)
        return False, image

def generateCombinedRegionImage(regionsList, matrix):
    """Generates a combined image of all regions specified within a given matrix."""
    assert isinstance(matrix, Matrix)
    for region in regionsList:
        assert isinstance(region, Region) 

    # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
    img = Image.new( 'RGB', (matrix.numCol,matrix.numRow), "black") # create a new black image
    pixels = img.load() # create the pixel map

    # startingColour = Color("red")
    # endColour = Color("blue")
    # colors = list(startingColour.range_to(endColour,len(regionsList)))  
    for index in range(len(regionsList)):
        if regionsList[index].getSize()>5:
            # colourtoAssign = colors[index]
            colourtoAssign = list(np.random.choice(range(256), size=3))
            while colourtoAssign == [0,0,0]:
                colourtoAssign = list(np.random.choice(range(256), size=3))
            for cell in regionsList[index].getCells():
                pixels[cell.getCol(),cell.getRow()] = (colourtoAssign[0], colourtoAssign[1], colourtoAssign[2])
                # (int(colourtoAssign.rgb[0]*255), int(colourtoAssign.rgb[1]*255), int(colourtoAssign.rgb[2]*255)) 
    return img


def sortRegions(regionsList):
    """Takes in a list of regions and returns them in a sorted format"""
    for region in regionsList:
        assert isinstance(region, Region) 
    regionsList.sort(key = Region.getAvgTemp)
    return regionsList


def showRegionsSeparately(regionsList, matrix):
    """Produces several [relevant] images, each with an individual region highlighted along with relevant information."""
    assert isinstance(matrix, Matrix)
    for region in regionsList:
        assert isinstance(region, Region) 
    print()
    for region in regionsList:
        if region.getSize()>1000: #a minimum pixel amount has been instituted to prevent small regions from being printed
            img = Image.new( 'RGB', (matrix.numCol,matrix.numRow), "black")
            pixels = img.load()
            print("Region size:", region.getSize(), "\t Average Temp:", round(region.getAvgTemp(),5))
            for cell in region.getCells():
                pixels[cell.getCol(),cell.getRow()] = (255,255,255)
            annotateImage(img, region)
            img.show()
    print()

def annotateImage(image, region):
    """Annotates the images of regions produced separately to provide information about their size and average temperature."""
    assert isinstance(image, Image.Image)
    assert isinstance(region, Region) 

    fnt = ImageFont.truetype("Arial", 11) #Font
    d = ImageDraw.Draw(image) #Getting a drawing context

    d.text((5, 10), "Size: {size} px".format(size = region.getSize()), font=fnt, fill=(255, 128, 0, 255))
    d.text((5, 20), "Avg Temp.: {temp}°C".format(temp = round(region.getAvgTemp(),3)), font=fnt, fill=(255, 128, 0, 255))

###########################

def findHolders(regionsList):
    """Goes through all regions and tries to find holders by checking if there are two regions, both having sizes
    between 1000 and 3000 pixels, that have an average temperature within 3.5% of each other and a size within 28%.
    If no holders are found, returns a tuple (0,0)."""
    for region in regionsList:
        assert isinstance(region, Region) 

    length = len(regionsList)
    for a in range(length):
        # the bounds of >1000 and <3000 have been placed to preclude other similar pairs regions that are smaller or larger than the holders
        if regionsList[a].getSize() > 1000 and regionsList[a].getSize() < 3000:
            for b in range(length):
                if a != b and regionsList[b].getSize() > 1000 and regionsList[b].getSize() < 3000:
                    if checkConditions(regionsList[a], regionsList[b]):
                        printHolderDetails(regionsList[a],regionsList[b])
                        return regionsList[a],regionsList[b]
    print("Holders not found.")
    return (0,0)

def checkConditions(regionA, regionB):
    """Helper function to compare two regions and returns True if they fulfill conditions that are likely to identify them
    as holders. Returns False otherwise."""
    assert isinstance(regionA, Region) and isinstance(regionB, Region)

    boolSize = abs(regionA.getSize() - regionB.getSize())/regionA.getSize() < 0.28 
    boolTemp = abs(regionA.getAvgTemp() - regionB.getAvgTemp())/regionA.getAvgTemp() < 0.035
    return boolSize and boolTemp

def printHolderDetails(holderA, holderB):
    assert isinstance(holderA, Region) and isinstance(holderB, Region)

    if holderA.avgRowAmt() < holderB.avgRowAmt():
        print("Top Holder\n\tSize: {size} px\t Avg Temp.: {temp}°C\n".format(size = holderA.getSize(), 
            temp = round(holderA.getAvgTemp(),3)))
        print("Bottom Holder\n\tSize: {size} px\t Avg Temp.: {temp}°C".format(size = holderB.getSize(), 
            temp = round(holderB.getAvgTemp(),3)))
        print("************************************")
    else:
        print("Top Holder\n\tSize: {size} px\t Avg Temp.: {temp}°C\n".format(size = holderB.getSize(), 
            temp = round(holderB.getAvgTemp(),3)))
        print()
        print("Bottom Holder\n\tSize: {size} px\t Avg Temp.: {temp}°C".format(size = holderA.getSize(), 
            temp = round(holderA.getAvgTemp(),3)))
        print("************************************")
