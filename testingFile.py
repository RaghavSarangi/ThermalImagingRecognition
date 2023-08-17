### MODULE IS OUTDATED AND NO MORE IN USE

import os
from classesMCR import *
from displayRegions import *
import tkinter as tk
from tkinter import filedialog as fd

def runTest(folderPath):
    all_files = os.listdir(folderPath)    
    csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
    fileCount  = 0
    accuracyArray = []
    for filename in csv_files:
        if filename == "dataset.csv":
            continue
        filepath = os.path.join(folderPath, filename)
        print("Opened file:", filename)
        matrix = Matrix(filepath)
        result = showRegions(matrix.identifyRegions(0.0015), matrix)
        accuracyArray.append(result)
        print()
        fileCount +=1
    print("Number of files:", fileCount)
    print("Accuracy: ", accuracyArray.count(True), "/", fileCount, sep="")

# Create the root window
root = tk.Tk()
root.title('Run Test')
root.resizable(False, False)
root.geometry('450x225')

def select_folder():
    
    folderName = fd.askdirectory(
        title='Open a folder',
        initialdir='/Users/Raghav1/ConnectWiseControl/Files')

    print("Opened folder:", folderName)
    runTest(folderName)


open_button = tk.Button(
    root,
    text='Open a Folder',
    command=select_folder)

exit_button = tk.Button(
    root,
    text='Exit',
    command=lambda: root.quit(),
    bg='#ffb3fe',
    fg = 'red')

open_button.pack(expand=True)
exit_button.pack(expand=True)

# Run the application
root.mainloop()