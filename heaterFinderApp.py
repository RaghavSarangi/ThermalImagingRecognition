from classesMCR import Matrix, ForcedMatrix
from displayRegions import showRegions, showRegionsSeparately
import tkinter as tk
from tkinter import filedialog as fd
import extraFeatures
import os

root = tk.Tk()
root.title('Thermal Imaging Recognition')
root.resizable(False, False)
root.geometry('450x225')


def select_file():
    filetypes = (('csv files', '*.csv'),)
    
    filename = fd.askopenfilename(
        title='Open a CSV file',
        initialdir='/Users/Raghav1/ConnectWiseControl/Files',
        filetypes=filetypes)

    print()
    print("File:", os.path.basename(filename))
    print("Directory:", os.path.dirname(filename))
    print()

    matrix = Matrix(filename)
    showRegions(matrix.identifyRegions(0.0044), matrix)

    # extraFeatures.convertToHeatmap(matrix)
    extraFeatures.DFSAnimator(matrix)
    # matrix.printMatrixDimensions()

open_button = tk.Button(
    root,
    text='Open a CSV File',
    command=select_file)

exit_button = tk.Button(
    root,
    text='Exit',
    command=lambda: root.quit(),
    bg='#ffb3fe',
    fg = 'red')

open_button.pack(expand=True)
exit_button.pack(expand=True)

root.mainloop()