# File purpose:
# main game "engine", contains all game objects as well as game functions and AI

import copy

# Dictionary:
# human location - the rank and file of a chess piece on the board
# python location - the row and column of a chess piece on the board
# move - a python location that a given piece can move to
# path - a set of changes in row (dRow) and changes in column (dCol) that a 
#        piece can make 


################################################################################
# Helper Functions
################################################################################

def humanToPythonLocation(location):
    humanToPythonRows = {'8':0, '7':1, '6':2, '5':3, '4':4, '3':5, '2':6, '1':7}
    humanToPythonCols = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    row = humanToPythonRows[location[1]]
    col = humanToPythonCols[location[0]]
    return row, col

def pythonToHumanLocation(row, col):
    pythonToHumanRows = {0:'8', 1:'7', 2:'6', 3:'5', 4:'4', 5:'3', 6:'2', 7:'1'}
    pythonToHumanCols = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
    humanRow = pythonToHumanRows[row]
    humanCol = pythonToHumanCols[col]
    return humanCol + humanRow

# returns the value of the cell based on the piece that it has, it's location on
# the board, and the color of the piece
def getCellValue(location, pieceType, pieceColor):
    row, col = humanToPythonLocation(location)
    if (pieceType == 'King'):
        cellValue = Cell.kingValues[row][col]
    elif (pieceType == 'Queen'):
        cellValue = Cell.queenValues[row][col]
    elif (pieceType == 'Knight'):
        cellValue = Cell.knightValues[row][col]
    elif (pieceType == 'Bishop'):
        cellValue = Cell.bishopValues[row][col]
    elif (pieceType == 'Rook'):
        cellValue = Cell.rookValues[row][col]
    elif (pieceType == 'Pawn'):
        cellValue = Cell.pawnValues[row][col]
            
    # negates values for enemy pieces
    if (pieceColor == 'black'):
        cellValue *= -1

    return cellValue

# extracts the python locations of the nextMoves dictionary and puts them into
# a 1D list
def getLocationsOnly(nextMoves):
    locations = set()

    for piece in nextMoves:
        for move in nextMoves[piece]:
            locations.add(move)
    
    return locations

# returns a set of python locations of all the pieces of a certain color
def findPieceLocations(gameBoard, color):
    pieceLocations = set()

    for row in range(8):
        for col in range(8):
            currentPiece = gameBoard.board[row][col].piece
            if (currentPiece != None) and (currentPiece.pieceColor == color):
                pieceLocations.add((row, col))

    return pieceLocations

# returns the python location of the king of a given color, and if the king is
# not present in the board, then returns 42, 42 for checkmate 
def findKingLocation(gameBoard, color):
    for row in range(8):
        for col in range(8):
            currentPiece = gameBoard.board[row][col].piece
            if (currentPiece != None) and (currentPiece.pieceType == 'King')\
               and (currentPiece.pieceColor == color):
                return row, col
    # no king in future game state, that is bad which means checkmate has already
    # passed and this returns 42, 42 so it won't return None
    return 42, 42

def findDirection(startRow, startCol, targetRow, targetCol): 
    if (startRow - targetRow > 0) and (startCol - targetCol > 0):
        return 'NW'
    elif (startRow - targetRow > 0) and (startCol - targetCol == 0):
        return 'N'
    elif (startRow - targetRow > 0) and (startCol - targetCol < 0):
        return 'NE'
    elif (startRow - targetRow == 0) and (startCol - targetCol > 0):
        return 'W'
    elif (startRow - targetRow == 0) and (startCol - targetCol == 0):
        return None
    elif (startRow - targetRow == 0) and (startCol - targetCol < 0):
        return 'E'
    elif (startRow - targetRow < 0) and (startCol - targetCol > 0):
        return 'SW'
    elif (startRow - targetRow < 0) and (startCol - targetCol == 0):
        return 'S'
    elif (startRow - targetRow < 0) and (startCol - targetCol < 0):
        return 'SE'

# returns the path that each piece can take in a given direction
def findPath(row, pieceType, color, direction):
    # defines paths for each piece
    if (pieceType == 'Pawn'):
        if (color == 'white'):
            nPath = [(-1, 0), (-2, 0)] if (row == 6) else [(-1, 0)]
            nwPath = [(-1, -1)]
            nePath = [(-1, +1)]
        elif (color == 'black'):
            sPath = [(+1, 0), (+2, 0)] if (row == 1) else [(+1, 0)]
            swPath = [(+1, -1)]
            sePath = [(+1, +1)]

    elif (pieceType == 'Rook'):
        nPath = [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]
        sPath = [(+1, 0), (+2, 0), (+3, 0), (+4, 0), (+5, 0), (+6, 0), (+7, 0)]
        ePath = [(0, +1), (0, +2), (0, +3), (0, +4), (0, +5), (0, +6), (0, +7)]
        wPath = [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)]

    elif (pieceType == 'Knight'):
        knightPath = [(+2, +1), (+2, -1), (-2, +1), (-2, -1),
                      (+1, +2), (+1, -2), (-1, +2), (-1, -2)]
        return knightPath # since the direction doesn't really matter
    
    elif (pieceType == 'Bishop'):
        nwPath = [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]
        nePath = [(-1, +1), (-2, +2), (-3, +3), (-4, +4), (-5, +5), (-6, +6), (-7, +7)]
        swPath = [(+1, -1), (+2, -2), (+3, -3), (+4, -4), (+5, -5), (+6, -6), (+7, -7)]
        sePath = [(+1, +1), (+2, +2), (+3, +3), (+4, +4), (+5, +5), (+6, +6), (+7, +7)]
                   
    elif (pieceType == 'King'):
        nwPath = [(-1, -1)]
        nPath = [(-1, 0)]
        nePath = [(-1, +1)]
        swPath = [(+1, -1)]
        sPath = [(+1, 0)]
        sePath = [(+1, +1)]
        # castling for the king
        wPath = [(0, -1), (0, -2)] if (row == 7) or (row == 0) else [(0, -1)]
        ePath = [(0, +1), (0, +2)] if (row == 7) or (row == 0) else [(0, +1)]

    elif (pieceType == 'Queen'):
        nwPath = [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]
        nePath = [(-1, +1), (-2, +2), (-3, +3), (-4, +4), (-5, +5), (-6, +6), (-7, +7)]
        swPath = [(+1, -1), (+2, -2), (+3, -3), (+4, -4), (+5, -5), (+6, -6), (+7, -7)]
        sePath = [(+1, +1), (+2, +2), (+3, +3), (+4, +4), (+5, +5), (+6, +6), (+7, +7)]
        nPath = [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]
        sPath = [(+1, 0), (+2, 0), (+3, 0), (+4, 0), (+5, 0), (+6, 0), (+7, 0)]
        ePath = [(0, +1), (0, +2), (0, +3), (0, +4), (0, +5), (0, +6), (0, +7)]
        wPath = [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)]
    
    # dictionary that stores the pieces that can go in each direction
    availableDirections = {'NW':{'Bishop', 'King', 'Queen'}, 
                           'N':{'King', 'Queen', 'Rook'},
                           'NE':{'Bishop', 'King', 'Queen'},
                           'W':{'King', 'Queen', 'Rook'},
                           'E':{'King', 'Queen', 'Rook'},
                           'SW':{'Bishop', 'King', 'Queen'},
                           'S':{'King', 'Queen', 'Rook'},
                           'SE':{'Bishop', 'King', 'Queen'}}
    
    # adds pawn to direction dictionary based on color for capturing
    if (pieceType == 'Pawn'):
        if (color == 'black'):
            availableDirections['S'].add('Pawn')
            availableDirections['SW'].add('Pawn')
            availableDirections['SE'].add('Pawn')
        elif (color == 'white'):
            availableDirections['N'].add('Pawn')
            availableDirections['NW'].add('Pawn')
            availableDirections['NE'].add('Pawn')

    # returns the relevant path
    if (direction == 'NW') and (pieceType in availableDirections['NW']):
        return nwPath
    elif (direction == 'N') and (pieceType in availableDirections['N']):
        return nPath
    elif (direction == 'NE') and (pieceType in availableDirections['NE']):
        return nePath
    elif (direction == 'W') and (pieceType in availableDirections['W']):
        return wPath
    elif (direction == 'E') and (pieceType in availableDirections['E']):
        return ePath
    elif (direction == 'SW') and (pieceType in availableDirections['SW']):
        return swPath
    elif (direction == 'S') and (pieceType in availableDirections['S']):
        return sPath
    elif (direction == 'SE') and (pieceType in availableDirections['SE']):
        return sePath
    else:
        return None

# returns a set of legal moves that a given piece can make in a certain direction
def findLegalMovesOfPieceInDirection(gameBoard, startRow, startCol, direction):
    pieceType = gameBoard.board[startRow][startCol].piece.pieceType
    pieceColor = gameBoard.board[startRow][startCol].piece.pieceColor
    path = findPath(startRow, pieceType, pieceColor, direction)

    if (path == None):
        return None

    legalMoves = set()
    for (dRow, dCol) in path:
        newRow = startRow + dRow
        newCol = startCol + dCol
        if isLegalMove(gameBoard, startRow, startCol, newRow, newCol, 
                       path, direction):
            legalMoves.add((newRow, newCol))

    return legalMoves

# returns a dictionary that maps a piece's human location to a list of all of 
# its possible moves on the board
def findLegalMovesOfPiece(gameBoard, row, col):
    humanPieceLocation = pythonToHumanLocation(row, col)
    legalMoves = dict()
    directions = {'NW', 'N', 'NE', 'W', 'E', 'SW', 'S', 'SE'}

    for direction in directions:
        moves = findLegalMovesOfPieceInDirection(gameBoard, row, col, direction)
        if (moves != None):
            if (humanPieceLocation not in legalMoves):
                legalMoves[humanPieceLocation] = moves
            else:
                legalMoves[humanPieceLocation] = legalMoves[humanPieceLocation].union(moves)
    
    return legalMoves

# returns a dictionary of ALL pieces of a certain color's human locations mapped
# to lists of all possible moves that each piece can make
def findLegalMoves(gameBoard, color):
    pieceLocations = findPieceLocations(gameBoard, color)
    legalMoves = dict()
    
    for row, col in pieceLocations:
        movesOfPiece = findLegalMovesOfPiece(gameBoard, row, col)
        legalMoves.update(movesOfPiece)
    
    return legalMoves

################################################################################
# Game Objects
################################################################################

# physical gameboard that holds cells
class Gameboard(object):
    # size of the board is always 8x8
    def __init__(self):
        self.board = []
        for row in ['8', '7', '6', '5', '4', '3', '2', '1']:
            boardRow = []
            for col in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
                boardRow += [Cell(col+row)]
            self.board.append(boardRow)
        self.blackIsChecked = False
        self.whiteIsChecked = False

    def setPieces(self):
        self.board[0] = [Cell('a8', ChessPiece('black', 'Rook')), 
                         Cell('b8', ChessPiece('black', 'Knight')), 
                         Cell('c8', ChessPiece('black', 'Bishop')),
                         Cell('d8', ChessPiece('black', 'Queen')),
                         Cell('e8', ChessPiece('black', 'King')), 
                         Cell('f8', ChessPiece('black', 'Bishop')),
                         Cell('g8', ChessPiece('black', 'Knight')),
                         Cell('h8', ChessPiece('black', 'Rook'))]
        for col in range(8):
            self.board[1][col].addPiece(ChessPiece('black', 'Pawn'))
            self.board[6][col].addPiece(ChessPiece('white', 'Pawn'))
        self.board[7] = [Cell('a1', ChessPiece('white', 'Rook')), 
                         Cell('b1', ChessPiece('white', 'Knight')), 
                         Cell('c1', ChessPiece('white', 'Bishop')),
                         Cell('d1', ChessPiece('white', 'Queen')),
                         Cell('e1', ChessPiece('white', 'King')), 
                         Cell('f1', ChessPiece('white', 'Bishop')),
                         Cell('g1', ChessPiece('white', 'Knight')),
                         Cell('h1', ChessPiece('white', 'Rook'))]

    def getHashables(self):
        return (self.board, self.blackIsChecked, self.whiteIsChecked)

    def __hash__(self):
        return hash(self.getHashables())
    
    def __eq__(self, other):
        return isinstance(other, GameBoard) and (self.board == other.board) and\
               (self.blackIsChecked == other.blackIsChecked) and\
               (self.whiteIsChecked == other.whiteIsChecked)

    def copy(self):
        newBoard = Gameboard()
        newBoard.board = copy.deepcopy(self.board)
        newBoard.whiteIsChecked = self.whiteIsChecked
        newBoard.blackIsChecked = self.blackIsChecked
        return newBoard

    def boardValue(self):
        if (self.blackIsChecked):
            return 1000000000 # arbitrary huge value to show worst case
        elif (self.whiteIsChecked):
            return -1000000000 # arbitrary huge value to show worst case
        else:
            total = 0
            for row in range(8):
                for col in range(8):
                    total += self.board[row][col].cellValue
            return total

    def printBoard(self):
        for row in self.board:
            print(row)

# cell that holds a chess piece or nothing
class Cell(object):
    # values for every white piece relative to its position on the board
    # taken from:
    # https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977/
    # nothing else was taken from that website though, the rest of the chess 
    # game functions are indeed mine

    kingValues = [ [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                   [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                   [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                   [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                   [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
                   [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
                   [+2.0, +2.0,  0.0,  0.0,  0.0,  0.0, +2.0, +2.0],
                   [+2.0, +3.0, +1.0,  0.0,  0.0, +1.0, +3.0, +2.0]  ] 
    
    queenValues = [ [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
                    [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
                    [-1.0,  0.0, +0.5, +0.5, +0.5, +0.5,  0.0, -1.0],
                    [-0.5,  0.0, +0.5, +0.5, +0.5, +0.5,  0.0, -0.5],
                    [ 0.0,  0.0, +0.5, +0.5, +0.5, +0.5,  0.0, -0.5],
                    [-1.0, +0.5, +0.5, +0.5, +0.5, +0.5,  0.0, -1.0],
                    [-1.0,  0.0, +0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
                    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]  ]

    rookValues = [ [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [+0.5, +1.0, +1.0, +1.0, +1.0, +1.0, +1.0, +0.5],
                   [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
                   [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
                   [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
                   [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
                   [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
                   [ 0.0,  0.0,  0.0, +0.5, +0.5,  0.0,  0.0,  0.0]  ]

    bishopValues = [ [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
                     [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
                     [-1.0,  0.0, +0.5, +1.0, +1.0, +0.5,  0.0, -1.0],
                     [-1.0, +0.5, +0.5, +1.0, +1.0, +0.5, +0.5, -1.0],
                     [-1.0,  0.0, +1.0, +1.0, +1.0, +1.0,  0.0, -1.0],
                     [-1.0, +1.0, +1.0, +1.0, +1.0, +1.0, +1.0, -1.0],
                     [-1.0, +0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
                     [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]  ]
    
    knightValues = [ [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
                     [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
                     [-3.0,  0.0, +1.0, +1.5, +1.5, +1.0,  0.0, -3.0],
                     [-3.0, +0.5, +1.5, +2.0, +2.0, +1.5, +0.5, -3.0],
                     [-3.0,  0.0, +1.5, +2.0, +2.0, +1.5,  0.0, -3.0],
                     [-3.0, +0.5, +1.0, +1.5, +1.5, +1.0, +0.5, -3.0],
                     [-4.0, -2.0,  0.0, +0.5, +0.5,  0.0, -2.0, -4.0],
                     [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]  ]
    
    pawnValues = [ [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [+5.0, +5.0, +5.0, +5.0, +5.0, +5.0, +5.0, +5.0],
                   [+1.0, +1.0, +2.0, +3.0, +3.0, +2.0, +1.0, +1.0],
                   [+0.5, +0.5, +1.0, +2.5, +2.5, +1.0, +0.5, +0.5],
                   [ 0.0,  0.0,  0.0, +2.0, +2.0,  0.0,  0.0,  0.0],
                   [+0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5, +0.5],
                   [+0.5, +1.0, +1.0, -2.0, -2.0, +1.0, +1.0, +0.5],
                   [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]  ]

    # defines properties for each cell
    def __init__(self, location, piece=None):
        self.location = location
        self.piece = piece
        self.changes = 0 # number of changes that were applied to the cell
        if (piece == None):
            self.cellValue = 0
        else:
            self.cellValue = getCellValue(location, piece.pieceType,
                                          piece.pieceColor)

    def getHashables(self):
        return (self.piece, self.location, self.changes)

    def __hash__(self):
        return hash(self.getHashables())
    
    def __repr__(self):
        return f'{self.piece}, {self.location}'

    def __eq__(self, other):
        return isinstance(other, Cell) and (self.piece == other.piece) and\
               (self.location == other.location) and\
               (self.changes == other.changes)

    def addPiece(self, piece):
        self.piece = piece
        self.cellValue = getCellValue(self.location, piece.pieceType, 
                                      piece.pieceColor)

    def removePiece(self):
        self.piece = None
        self.cellValue = 0

class ChessPiece(object):
    # pieces = ['Rook', 'Bishop', 'King', 'Queen', 'Knight', 'Pawn']
    # colors = ['black', 'white']

    def __init__(self, color, pieceType):
        self.pieceType = pieceType
        self.pieceColor = color

    def getHashables(self):
        return (self.pieceType, self.pieceColor)

    def __hash__(self):
        return hash(self.getHashables())
    
    def __repr__(self):
        return f'{self.pieceColor} {self.pieceType}'
    
    def __eq__(self, other):
        return (isinstance(other, ChessPiece)) and\
               (self.pieceType == other.pieceType) and\
               (self.pieceColor == other.pieceColor)

################################################################################
# Game Functions
################################################################################

# checks if the move from the start python location to the end python location
# is legal, assuming that there is a start piece, path, and direction
def isLegalMove(gameBoard, startRow, startCol, targetRow, targetCol, path, direction):
    # first checks if this move is out of the board 
    if (targetRow < 0) or (targetRow >= 8) or\
       (targetCol < 0) or (targetCol >= 8):
        return False

    boardSize = 8
    startPieceType = gameBoard.board[startRow][startCol].piece.pieceType
    startPieceColor = gameBoard.board[startRow][startCol].piece.pieceColor

    if (gameBoard.board[targetRow][targetCol].piece != None):
        targetPieceType = gameBoard.board[targetRow][targetCol].piece.pieceType
        targetPieceColor = gameBoard.board[targetRow][targetCol].piece.pieceColor
    else:
        targetPieceType = None

    if (startPieceType == 'King') and\
       (gameBoard.board[startRow][startCol].changes == 0) and (len(path) == 2):

        if (startPieceColor == 'white') and ((startRow, startCol) == (7, 4)):
            # white king castling left
            if ((targetRow, targetCol) == (7, 2)) and\
               (gameBoard.board[7][0].piece != None) and\
               (gameBoard.board[7][0].piece.pieceType == 'Rook') and\
               (gameBoard.board[7][0].changes == 0) and\
               (gameBoard.board[7][1].piece == None) and\
               (gameBoard.board[7][2].piece == None) and\
               (gameBoard.board[7][3].piece == None):
                return True
            # white king castling right
            elif ((targetRow, targetCol) == (7, 6)) and\
                 (gameBoard.board[7][7].piece != None) and\
                 (gameBoard.board[7][7].piece.pieceType == 'Rook') and\
                 (gameBoard.board[7][7].changes == 0) and\
                 (gameBoard.board[7][5].piece == None) and\
                 (gameBoard.board[7][6].piece == None):
                return True

        elif (startPieceColor == 'black') and ((startRow, startCol) == (0, 4)):
            # black king castling left
            if ((targetRow, targetCol) == (0, 2)) and\
               (gameBoard.board[0][0].piece != None) and\
               (gameBoard.board[0][0].piece.pieceType == 'Rook') and\
               (gameBoard.board[0][0].changes == 0) and\
               (gameBoard.board[0][1].piece == None) and\
               (gameBoard.board[0][2].piece == None) and\
               (gameBoard.board[0][3].piece == None):
                return True
            # black king castling right
            elif ((targetRow, targetCol) == (0, 6)) and\
                 (gameBoard.board[0][7].piece != None) and\
                 (gameBoard.board[0][7].piece.pieceType == 'Rook') and\
                 (gameBoard.board[0][7].changes == 0) and\
                 (gameBoard.board[0][5].piece == None) and\
                 (gameBoard.board[0][6].piece == None):
                return True
        
    # denies move of king two spaces over if it doesn't meet the qualifications
    # to castle
    elif (startPieceType == 'King') and (abs(targetCol - startCol) == 2):
        return False

    # checks path leading up to piece to see if it's able to get there
    for (dRow, dCol) in path:
        newRow = startRow + dRow
        newCol = startCol + dCol
        
        # special check for pawns moving
        if (startPieceType == 'Pawn'):
            # nothing to capture
            if (len(direction) == 2) and\
               (gameBoard.board[newRow][newCol].piece == None):
                return False
            # can't move vertically in occupied spot
            elif (len(direction) == 1) and\
                 (gameBoard.board[newRow][newCol].piece != None):
                return False

        # checks if this move is out of the board and skips it
        if (newRow < 0) or (newRow >= boardSize) or\
           (newCol < 0) or (newCol >= boardSize):
            continue

        # checks if there is a piece in the way of path
        if (gameBoard.board[newRow][newCol].piece != None) and\
           ((newRow, newCol) != (targetRow, targetCol)) and\
           (startPieceType != 'Knight'): # excludes knights because of their unique path
            return False
        
        # checks if there is a piece at the target cell and if it's captureable
        elif ((newRow, newCol) == (targetRow, targetCol)) and\
             (targetPieceType != None):
            if (targetPieceColor != startPieceColor):
                return True
            else:
                return False
        
        # checks if the target cell is empty
        elif ((newRow, newCol) == (targetRow, targetCol)) and\
             (targetPieceType == None):
            return True
    
    # does not pass any check
    return False

def findChecks(gameBoard):
    checks = {'white', 'black'} # assumes both are checked first

    # finds next moves for all pieces
    nextWhiteMoves = findLegalMoves(gameBoard, 'white')
    nextWhiteMoves = getLocationsOnly(nextWhiteMoves)
    nextBlackMoves = findLegalMoves(gameBoard, 'black')
    nextBlackMoves = getLocationsOnly(nextBlackMoves)

    # finds locations for both kings
    whiteKingRow, whiteKingCol = findKingLocation(gameBoard, 'white')
    blackKingRow, blackKingCol = findKingLocation(gameBoard, 'black')

    # if the king is gone from the board, then that is bad and is past checkmate
    if ((whiteKingRow, whiteKingCol) == (42, 42)) or\
       ((blackKingRow, blackKingCol) == (42, 42)):
        return {'king is missing'}

    # must now find the attacking pieces for each side
    if ((whiteKingRow, whiteKingCol) not in nextBlackMoves):
        checks.remove('white')
    if ((blackKingRow, blackKingCol) not in nextWhiteMoves):
        checks.remove('black')

    return checks

def makeMove(gameBoard, startRow, startCol, targetRow, targetCol):
    movingPiece = gameBoard.board[startRow][startCol].piece
    oldLocation = pythonToHumanLocation(startRow, startCol)    
    newLocation = pythonToHumanLocation(targetRow, targetCol)

    # conditonals for making pawn into queen
    if (movingPiece == ChessPiece('black', 'Pawn')) and (newLocation[1] == '1'):
        gameBoard.board[targetRow][targetCol].addPiece(ChessPiece('black', 'Queen'))
    elif (movingPiece == ChessPiece('white', 'Pawn')) and (newLocation[1] == '8'):
        gameBoard.board[targetRow][targetCol].addPiece(ChessPiece('white', 'Queen'))

    # conditional for castling black king left
    elif (movingPiece == ChessPiece('black', 'King')) and (newLocation == 'c8'):
        gameBoard.board[targetRow][targetCol].addPiece(movingPiece)
        gameBoard.board[targetRow][targetCol+1].addPiece(ChessPiece('black', 'Rook'))
        gameBoard.board[targetRow][targetCol+1].changes += 1
        gameBoard.board[0][0].removePiece()
        gameBoard.board[0][0].changes += 1

    # conditional for castling black king right
    elif (movingPiece == ChessPiece('black', 'King')) and (newLocation == 'g8'):
        gameBoard.board[targetRow][targetCol].addPiece(movingPiece)
        gameBoard.board[targetRow][targetCol-1].addPiece(ChessPiece('black', 'Rook'))
        gameBoard.board[targetRow][targetCol-1].changes += 1
        gameBoard.board[0][7].removePiece()
        gameBoard.board[0][7].changes += 1

    # conditional for castling white king left
    elif (movingPiece == ChessPiece('white', 'King')) and (newLocation == 'c1'):
        gameBoard.board[targetRow][targetCol].addPiece(movingPiece)
        gameBoard.board[targetRow][targetCol+1].addPiece(ChessPiece('white', 'Rook'))
        gameBoard.board[targetRow][targetCol+1].changes += 1
        gameBoard.board[7][0].removePiece()
        gameBoard.board[7][0].changes += 1

    # conditional for castling white king right
    elif (movingPiece == ChessPiece('white', 'King')) and (newLocation == 'g1'):
        gameBoard.board[targetRow][targetCol].addPiece(movingPiece)
        gameBoard.board[targetRow][targetCol-1].addPiece(ChessPiece('white', 'Rook'))
        gameBoard.board[targetRow][targetCol-1].changes += 1
        gameBoard.board[7][7].removePiece()
        gameBoard.board[7][7].changes += 1

    # all other cases
    else:
        gameBoard.board[targetRow][targetCol].addPiece(movingPiece)

    gameBoard.board[startRow][startCol].removePiece()
    gameBoard.board[startRow][startCol].changes += 1
    gameBoard.board[targetRow][targetCol].changes += 1

    return gameBoard

################################################################################
# Minimax Functions
################################################################################

def makeBoardsForNextMoves(gameBoard, color):
    boardSize = 8

    # first finds all legal moves pieces of a certain color can make
    allLegalMoves = findLegalMoves(gameBoard, color)

    # then makes a new board for every legal move possible
    boards = []
    for pieceLocation in allLegalMoves:
        startRow, startCol = humanToPythonLocation(pieceLocation)
        for targetRow, targetCol in allLegalMoves[pieceLocation]:
            tempBoard = gameBoard.copy()
            newBoard = makeMove(tempBoard, startRow, startCol, targetRow, targetCol)
            checks = findChecks(newBoard)
            if ('white' in checks):
                newBoard.whiteIsChecked = True
            else:
                newBoard.whiteIsChecked = False
            if ('black' in checks):
                newBoard.blackIsChecked = True
            else:
                newBoard.blackIsChecked = False
            if ('king is missing' not in checks):
                boards += [newBoard]

    return boards

# psuedocode used for this taken from Youtube video:
# "Algorithms Explained – minimax and alpha-beta pruning" by Sebastian Lague
def minimax(gameBoard, depth, alpha, beta, isMaximizing):
    if (depth == 0) or (gameBoard.blackIsChecked) or (gameBoard.whiteIsChecked):
        return gameBoard.boardValue()
    
    if (isMaximizing):
        maxValue = -1000000 # arbitrarily small number for first comparison
        nextBoards = makeBoardsForNextMoves(gameBoard, 'white')
        for board in nextBoards:
            currValue = minimax(board, depth-1, alpha, beta, False)
            maxValue = max(maxValue, currValue)
            alpha = max(alpha, currValue)
            if (beta <= alpha):
                break
        return maxValue

    elif (not isMaximizing):
        minValue = 1000000 # arbitarity large number for first comparison
        nextBoards = makeBoardsForNextMoves(gameBoard, 'black')
        for board in nextBoards:
            currValue = minimax(board, depth-1, alpha, beta, True)
            minValue = min(minValue, currValue)
            beta = min(beta, currValue)
            if (beta <= alpha):
                break
        return minValue
