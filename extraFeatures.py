import cv2
import numpy as np
from classesMCR import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def convertToHeatmap(matrix):
    """Converts a given matrix to a heatmap"""
    assert isinstance(matrix, Matrix)

    df = pd.DataFrame(data = matrix.dataMatrix)
    fig, ax = plt.subplots(figsize=(11,6))
    title = "Heat Map"
    plt.title(title,fontsize=18)
    ttl = ax.title
    ttl.set_position([0.5,1.05])
    ax.axis('off')

    sns.heatmap(data = df, cmap= "RdYlGn_r", vmin=matrix.minValue(), vmax=matrix.maxValue(), ax=ax)
    plt.show()

def DFSAnimator(matrix):
    """Creates an animation of the depth-first search that is carried out by the Thermal Imaging Recognition algorithm."""
    assert isinstance(matrix, Matrix)

    img = np.zeros((matrix.numRow,matrix.numCol,3), np.uint8)
    numOfRegions = 0
    for i in range(matrix.numRow):
        for j in range(matrix.numCol):
            cell = matrix.getCell(i,j)
            if not cell.isCompared():
                numOfRegions += 1
                colourToFill = list(np.random.choice(range(256), size=3))
                regionCreator = matrix.iterativeCheckGenerator(cell, 0.0015)
                try: 
                    while True:
                        location = next(regionCreator)
                        img[location.getRow(),location.getCol()] = (255,255,0)
                        cv2.imshow('Depth-First Search',img)
                        key = cv2.waitKey(1)
                        if key == 13:
                            while True:
                                location = next(regionCreator)
                                img[location.getRow(),location.getCol()] = colourToFill
                        elif key == 27:
                            cv2.destroyAllWindows() 
                            return
                        img[location.getRow(),location.getCol()] = colourToFill
                except StopIteration:
                    continue
    cv2.waitKey(0)
    cv2.destroyAllWindows() 
    print("Total Regions Coloured:", numOfRegions)