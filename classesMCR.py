import csv
from statistics import mean
from collections import deque

class Matrix:
    """A class for a 2D list of lists. Each sub-list is a row of Cell objects"""

    def __init__(self, filepath):
        """Reads a csv file and inserts data into a matrix"""
        self.file = filepath
        self.dataMatrix = []
        self.cellMatrix= []
        self.numRow = 0
        self.numCol = 0
        file = open(filepath)
        csvreader = csv.reader(file)
        for row in csvreader:
            self.dataMatrix.append(row)
            self.numRow+=1
            if self.numCol != len(row):
                if self.numCol == 0:
                    self.numCol = len(row)
                else:
                    print("This matrix has a non-uniform number of columns")
        file.close()
        for i in range(self.numRow):
            rowArray = []
            for j in range(self.numCol):
                self.dataMatrix[i][j] = float(self.dataMatrix[i][j])
                rowArray.append(self.Cell(i, j, self.dataMatrix[i][j]))
            self.cellMatrix.append(rowArray)

    # def reset_matrix(self):
    #     self.dataMatrix = []
    #     self.cellMatrix = []
    #     self.numRow = 0
    #     self.numCol = 0
    
    def printMatrix(self):
        """Prints a visualization of the matrix"""
        rowString = ""
        mainString = ""
        for row in self.dataMatrix:
            rowString = "\t".join(str(i) for i in row)
            mainString = rowString + "\n"
        print(mainString)
        self.printMatrixDimensions()

    def printMatrixDimensions(self):
        """Prints the dimensions of the matrix"""   
        print("Number of rows:", self.numRow)
        print("Number of columns:", self.numCol)

    def minValue(self):
        """Returns the minimum value in the matrix."""
        min = 1000
        for row in self.dataMatrix:
            for value in row:
                if value < min:
                    min = value
        return min
    
    def maxValue(self):
        """Returns the maximum value in the matrix."""
        max = -1000
        for row in self.dataMatrix:
            for value in row:
                if value > max:
                    max = value
        return max
    
    def getFile(self):
        """Returns the filepath of the CSV file used to generate this matrix"""
        return self.file
    
    ### CELL TRAVERSAL    
    def getCell(self, row, col):
        return self.cellMatrix[row][col]

    def belowCell(self, cell):
        """Returns the Cell object, if there is one, below a given cell"""
        if cell.getRow() >= self.numRow - 1:
            return None
        else:
            return self.cellMatrix[cell.getRow() + 1][cell.getCol()]

    def aboveCell(self, cell):
        """Returns the Cell object, if there is one, above a given cell"""
        if cell.getRow() <= 0:
            return None
        else:
            return self.cellMatrix[cell.getRow() - 1][cell.getCol()]

    def leftCell(self, cell):
        """Returns the Cell object, if there is one, to the left of a given cell"""
        if cell.getCol() <= 0:
            return None
        else:
            return self.cellMatrix[cell.getRow()][cell.getCol() - 1]
    
    def rightCell(self, cell):
        """Returns the Cell object, if there is one, to the right of a given cell"""
        if cell.getCol() >= self.numCol - 1:
            return None
        else:
            return self.cellMatrix[cell.getRow()][cell.getCol() + 1]

    def recursiveCheck(self, cell, differentiatingValue):
        """Recursively check which cells next to the given cell are similar in value and returns an array of Cell objects"""
        ### Do NOT use this version on high-resolution images since the call stack created will be too large.
        if cell.isSeen():
            return []
        cell.seenCell()
        prizeArray = []
        prizeArray.append(cell)
        if cell.withinRange(self.belowCell(cell), differentiatingValue):
            prizeArray.extend(self.recursiveCheck(self.belowCell(cell)))
        if cell.withinRange(self.aboveCell(cell), differentiatingValue):
            prizeArray.extend(self.recursiveCheck(self.aboveCell(cell)))
        if cell.withinRange(self.rightCell(cell), differentiatingValue):
            prizeArray.extend(self.recursiveCheck(self.rightCell(cell)))
        if cell.withinRange(self.leftCell(cell), differentiatingValue):
            prizeArray.extend(self.recursiveCheck(self.leftCell(cell)))
        return prizeArray

    def iterativeCheck(self, cell, differentiatingValue):
        """Iteratively check which cells next to the given cell are similar in value and returns an array of Cell objects"""
        prizeArray = []
        dfStack = deque(maxlen=self.numRow * self.numCol)
        dfStack.append(cell)
        prizeArray.append(cell)
        while (len(dfStack)):
            u = dfStack.pop()
            u.comparedCell() 
            for neighbour in (self.belowCell(u), self.aboveCell(u), self.leftCell(u), self.rightCell(u)):
                if not (neighbour is None or neighbour.isCompared()):
                        if u.withinRange(neighbour, differentiatingValue):
                            dfStack.append(neighbour)
                            prizeArray.append(neighbour)
        return prizeArray

    def iterativeCheckGenerator(self, cell, differentatingValue):
        """Iteratively check which cells next to the given cell are similar in value and returns an array of Cell objects"""
        dfStack = deque(maxlen=self.numRow * self.numCol)
        dfStack.append(cell)
        while (len(dfStack)):
            u = dfStack.pop()
            u.comparedCell() 
            yield(u)
            for neighbour in (self.belowCell(u), self.aboveCell(u), self.leftCell(u), self.rightCell(u)):
                if not (neighbour is None or neighbour.isCompared()):
                        if u.withinRange(neighbour, differentatingValue):
                            dfStack.append(neighbour)
    
    def identifyRegions(self, differentiatingValue):
        """Identifies regions of similar temperatures using the following algorithm:
            1. Start from one cell. Look at adjacent cells and mark them as seen.
            2. For each adjacent cell, check if it is within a 0.44% range. If it is, start constructing another array.
            3. Put the coordinates of all cells that have similar values within that array.
        Returns a list of all regions identified."""
        regionsArray = []
        for i in range(self.numRow):
            for j in range(self.numCol):
                startCell = self.getCell(i,j)
                if not startCell.isCompared():
                    region = Region(self.iterativeCheck(startCell, differentiatingValue))
                    regionsArray.append(region)
        print("Number of regions identified:", len(regionsArray))
        return regionsArray


    class Cell:
        """An inner class for each cell within a matrix"""

        def __init__(self, row, col, value):
            assert isinstance(row, int) and isinstance(col, int) and isinstance(value, float)
            self.rowVal = row
            self.colVal = col
            self.tempVal = value
            self.seen = False
            self.compared = False
        
        def getVal(self):
            """Returns the temperature of the cell/pixel"""
            return self.tempVal
        
        def getRow(self):
            """Returns the row position of the cell/pixel"""
            return self.rowVal

        def getCol(self):
            """Returns the column position of the cell/pixel"""
            return self.colVal
        
        def isSeen(self):
            """Returns if the cell/pixel has been seen (by the recursive DFS check)"""
            return self.seen

        def seenCell(self):
            """A procedure to mark the cell as seen"""
            self.seen = True
        
        def isCompared(self):
            """Returns if the cell/pixel has been compared (by the iterative DFS check)"""
            return self.compared

        def comparedCell(self):
            """A procedure to mark the cell as compared"""
            self.compared = True
        
        def withinRange(self, cell2, differentiatingValue):
            """Returns if another [adjacent] cell is within the temperature range of the given cell"""
            if cell2 is None:
                return False
            assert isinstance(cell2, Matrix.Cell)
            assert isinstance(differentiatingValue, float)
            val1 = self.getVal()
            val2 = cell2.getVal()
            if val1 == 0.0 or val2 == 0.0:
                return (abs(val1 - val2)) <= 0.000061 * abs(val1 + 273)
            return abs((val1 - val2)/val1) <= differentiatingValue
            # 0.0015 is good for ICI camera at 20°C
            # 0.0044 is good for FLIR camera at 26°C


class Region:
    """A class for each Region isolated in a matrix."""

    def __init__(self, cellsInRegion):
        for cell in cellsInRegion:
            assert isinstance(cell, Matrix.Cell) 

        self.cellArray = cellsInRegion
        self.avgTemp = mean(cell.getVal() for cell in cellsInRegion)
        self.size = len(cellsInRegion)
    
    def getCells(self):
        """Returns an array of the Cell objects within this Region."""
        return self.cellArray
    
    def getAvgTemp(self):
        """Returns the average temperature of all Cell objects within this Region."""
        return self.avgTemp
    
    def getSize(self):
        """Returns the size of this Region by checking how many cells lie within it."""
        return self.size
    
    def avgRowAmt(self):
        """Returns the 'latitude' of the region by calculating the row of an average cell in this Region."""
        return mean(cell.getRow() for cell in self.cellArray)

    def containsCellCoordinates(self, cellRow, cellCol):
        """Returns True [and that cell] if a given cell exists geographically in the region, returns False otherwise."""
        # assert isinstance(cell, Matrix.Cell)
        for item in self.cellArray:
            if item.getRow() == cellRow and item.getCol() == cellCol:
                return True, item
        return False, None
    
    ###Border-Cell Finders
    def lowerBorderRow(self):
        return max(cell.getRow() for cell in self.cellArray)
    
    def upperBorderRow(self):
        return min(cell.getRow() for cell in self.cellArray)
    
    def leftBorderCol(self):
        return min(cell.getCol() for cell in self.cellArray)
    
    def rightBorderCol(self):
        return max(cell.getCol() for cell in self.cellArray)
        

class ForcedMatrix(Matrix):
    """A class for a 2D list of lists. Each sub-list is a row of Cell objects. This is a matrix that has been created from a region,
    or a collection of regions."""

    def __init__(self, region, originalMatrix):
        """Creates a matrix that only contains information about one region."""
        assert isinstance(region, Region)
        assert isinstance(originalMatrix, Matrix)
        
        numOfRowsToCreate = region.lowerBorderRow() + 1 - region.upperBorderRow()
        numOfColsToCreate = region.rightBorderCol() + 1 - region.leftBorderCol()
        self.offset_x = region.upperBorderRow()
        self.offset_y = region.leftBorderCol()

        self.dataMatrix = []
        self.cellMatrix= []
        self.numRow = numOfRowsToCreate
        self.numCol = numOfColsToCreate

        for i in range(numOfRowsToCreate):
            rowArray = []
            for j in range(numOfColsToCreate):
                rowArray.append(-100.0)
            self.dataMatrix.append(rowArray)
        
        for i in range(self.numRow):
            for j in range(self.numCol):
                self.dataMatrix[i][j] = originalMatrix.dataMatrix[i+self.offset_x][j+self.offset_y]
        
        for i in range(self.numRow):
            rowCellArray = []
            for j in range(self.numCol):
                # self.dataMatrix[i][j] = float(self.dataMatrix[i][j])
                rowCellArray.append(Matrix.Cell(i, j, self.dataMatrix[i][j]))
            self.cellMatrix.append(rowCellArray)
        
    def getXOffset(self):
        return self.offset_x

    def getYOffset(self):
        return self.offset_y