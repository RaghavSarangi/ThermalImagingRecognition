from importlib.metadata import files
import os
import tkinter as tk
from PIL import ImageTk
from classesMCR import *
from displayRegions import generateHoldersImage, generateCombinedRegionImage
from tkinter import BOTTOM, LEFT, RIGHT, TOP, Toplevel, filedialog as fd

def produceDirectoryImages(folderPath):
    all_files = os.listdir(folderPath)    
    csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
    fileCount  = 0
    imageArray = []
    fileArray = []
    for filename in csv_files:
        if filename == "dataset.csv":
            continue
        filepath = os.path.join(folderPath, filename)
        print("Opened file:", filename)
        matrix = Matrix(filepath)
        fileArray.append(filepath)
        result = generateCombinedRegionImage(matrix.identifyRegions(0.0015), matrix) 
        imageArray.append(result)
        print()
        fileCount +=1
        ### Change the above to the following if only holder images are required:
        # successfulGeneration, result = generateHoldersImage(matrix.identifyRegions(), matrix) 
        # if successfulGeneration:
        #     fileArray.append(filepath)
        #     imageArray.append(result)
        #     print()
        #     fileCount +=1
    print("Number of files:", fileCount)
    return fileArray,imageArray


def OpenImageSelector(imageArray):
    def next():
        global imageIndex

        img2 = compatibleImageList[imageIndex + 1]
        label.configure(image=img2)
        label.image = img2
        imageIndex +=1
        if imageIndex == len(compatibleImageList) - 1:
            button_forward["state"] = tk.DISABLED
        button_back["state"] = tk.NORMAL
    
    def previous():
        global imageIndex

        img2 = compatibleImageList[imageIndex - 1]
        label.configure(image=img2)
        label.image = img2
        imageIndex -=1
        if imageIndex == 0:
            button_back["state"] = tk.DISABLED
        button_forward["state"] = tk.NORMAL
    
    def exit():
        newWindow.withdraw()
        newWindow.quit()
    
    def choose():
        global imageIndex
        global files
        print("File Used:", files[imageIndex])

    newWindow = Toplevel(root)
    newWindow.title("Image Selector")
    newWindow.geometry("800x600")
    compatibleImageList = [ImageTk.PhotoImage(img, master = newWindow) for img in imageArray]

    
    label = tk.Label(newWindow, image=compatibleImageList[imageIndex])
    label.pack(side=TOP, expand=True)

    button_forward = tk.Button(newWindow, text="Next", command= next)
    button_back = tk.Button(newWindow, text="Previous", command= previous, state= tk.DISABLED)
    button_exit = tk.Button(newWindow, text="Exit", command= exit)
    button_choose = tk.Button(newWindow, text="Choose", command= choose)
    

    button_back.pack(side= LEFT)
    button_forward.pack(side=RIGHT)
    button_exit.pack(side=BOTTOM)
    button_choose.pack(side=BOTTOM)
    
    newWindow.mainloop()

def select_folder():
    global files

    folderName = fd.askdirectory(
        title='Open a folder',
        initialdir='/Users/Raghav1/ConnectWiseControl/Files')

    print("Opened folder:", folderName)
    filesUsed,imagesProduced = produceDirectoryImages(folderName)
    files = filesUsed
    OpenImageSelector(imagesProduced)
    
imageIndex = 0 
files = []

root = tk.Tk()
root.title("Image Selector")
root.geometry("450x225")

open_button = tk.Button(root, text='Open a Folder', command=select_folder)
exit_button = tk.Button(root,text='Exit', command=lambda: root.quit(), bg='#ffb3fe', fg = 'red')

open_button.pack(expand=True)
exit_button.pack(expand=True)

root.mainloop()
