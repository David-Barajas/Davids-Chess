# File purpose:
# Runs chess app in singlerplayer/ai mode with mouse clicking inputs

from cmu_112_graphics import *
from game import *

################################################################################
# Helper Functions
################################################################################

# taken from 112 website
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

class Singleplayer_ChessNV(App):
    # taken from 112 website
    def getCellBounds(self, row, col):
        x0 = self.margin + self.gridWidth * col / 8 + self.boardOffset
        x1 = self.margin + self.gridWidth * (col+1) / 8 + self.boardOffset
        y0 = self.margin + self.gridHeight * row / 8
        y1 = self.margin + self.gridHeight * (row+1) / 8
        return x0, y0, x1, y1

    # taken from 112 website
    def pointInGrid(self, x, y):
        return (self.margin+self.boardOffset <= x <= self.width-self.margin)\
               and (self.margin <= y <= self.height-self.margin)

    # taken from 112 website
    def getCell(self, x, y):
        if (not self.pointInGrid(x, y)):
            return None

        cellWidth  = self.gridWidth / 8
        cellHeight = self.gridHeight / 8
        row = int((y - self.margin) / cellHeight)
        col = int((x - self.boardOffset - self.margin) / cellWidth)

        return row, col

    def getImage(self, pieceType, pieceColor):
        # gets image dirs for relative piece
        if (pieceColor == 'white'):
            if (pieceType == 'Pawn'):
                image = self.wPawnImage
            elif (pieceType == 'Rook'):
                image = self.wRookImage
            elif (pieceType == 'Knight'):
                image = self.wKnightImage
            elif (pieceType == 'Bishop'):
                image = self.wBishopImage
            elif (pieceType == 'Queen'):
                image = self.wQueenImage
            elif (pieceType == 'King'):
                image = self.wKingImage
        elif (pieceColor == 'black'):
            if (pieceType == 'Pawn'):
                image = self.bPawnImage
            elif (pieceType == 'Rook'):
                image = self.bRookImage
            elif (pieceType == 'Knight'):
                image = self.bKnightImage
            elif (pieceType == 'Bishop'):
                image = self.bBishopImage
            elif (pieceType == 'Queen'):
                image = self.bQueenImage
            elif (pieceType == 'King'):
                image = self.bKingImage
        return image

    ############################################################################
    # Model & Controller Functions
    ############################################################################

    def appStarted(self):
        # game setup
        self.timerDelay = 100
        self.margin = 58
        self.gridWidth = 700 - 2*self.margin
        self.gridHeight = 700 - 2*self.margin
        self.boardOffset = 500
        self.gameBoard = Gameboard()
        self.gameBoard.setPieces()
        self.selectedLocation = None
        self.mouseLocation = None
        self.highlightedLocations = [ ]
        self.whiteCheckmate = False
        self.blackCheckmate = False
        with open('settings.txt', "rt") as f:
            contents = f.read().splitlines()
        self.depthLevel = int(contents[0])
        self.name = contents[1]

        # player's turns and moves
        self.whiteTurn = True
        self.blackTurn = False
        self.gettingMoveFrom = True
        self.gettingMoveTo = False
        self.moveFrom = None
        self.moveTo = None

        # all piece images taken from wikipedia :)

        # black piece images
        self.bPawnImage = self.loadImage('images/bPawn.webp')
        self.bPawnImage = self.scaleImage(self.bPawnImage, 0.09)
        self.bRookImage = self.loadImage('images/bRook.webp')
        self.bRookImage = self.scaleImage(self.bRookImage, 0.09)
        self.bKnightImage = self.loadImage('images/bKnight.webp')
        self.bKnightImage = self.scaleImage(self.bKnightImage, 0.09)
        self.bBishopImage = self.loadImage('images/bBishop.webp')
        self.bBishopImage = self.scaleImage(self.bBishopImage, 0.09)
        self.bQueenImage = self.loadImage('images/bQueen.webp')
        self.bQueenImage = self.scaleImage(self.bQueenImage, 0.09)
        self.bKingImage = self.loadImage('images/bKing.webp')
        self.bKingImage = self.scaleImage(self.bKingImage, 0.09)
        # white piece images
        self.wPawnImage = self.loadImage('images/wPawn.webp')
        self.wPawnImage = self.scaleImage(self.wPawnImage, 0.09)
        self.wRookImage = self.loadImage('images/wRook.webp')
        self.wRookImage = self.scaleImage(self.wRookImage, 0.09)
        self.wKnightImage = self.loadImage('images/wKnight.webp')
        self.wKnightImage = self.scaleImage(self.wKnightImage, 0.09)
        self.wBishopImage = self.loadImage('images/wBishop.webp')
        self.wBishopImage = self.scaleImage(self.wBishopImage, 0.09)
        self.wQueenImage = self.loadImage('images/wQueen.webp')
        self.wQueenImage = self.scaleImage(self.wQueenImage, 0.09)
        self.wKingImage = self.loadImage('images/wKing.webp')
        self.wKingImage = self.scaleImage(self.wKingImage, 0.09)

        # miscellaneous

        # hour glass image taken from: 
        # https://webstockreview.net/explore/hourglass-clipart-vintage/
        self.hourGlassImage = self.loadImage('images/hourGlass.webp')
        self.hourGlassImage = self.scaleImage(self.hourGlassImage, 0.03)

    def timerFired(self):
        # checks board for a checkmate:
        checks = findChecks(self.gameBoard)
        if ('white' in checks) and (self.blackTurn):
            self.whiteCheckmate = True
        if ('black' in checks) and (self.whiteTurn):
            self.blackCheckmate = True
            with open('leaderboard.txt', 'rt') as f:
                leaderboard = f.read().splitlines()
            contents = ''
            for i in range(len(leaderboard)):
                if (leaderboard[i].startswith(self.name)):
                    leaderboard[i] = leaderboard[i][:-1] + str(int(leaderboard[i][-1]) + 1)
                contents += leaderboard[i] + '\n'
            contents = contents.strip()
            with open('leaderboard.txt', "wt") as f:
                f.write(contents)

        if (not self.blackCheckmate) and (not self.whiteCheckmate):
            if (self.whiteTurn):
                print("White's Turn!")
                if (self.moveFrom != None) and (self.moveTo != None):
                    startRow, startCol = self.moveFrom
                    targetRow, targetCol = self.moveTo
                    pieceLocation = pythonToHumanLocation(startRow, startCol)
                    currentPieceMoves = findLegalMovesOfPiece(self.gameBoard, startRow, 
                                                            startCol)[pieceLocation]
                    if ((targetRow, targetCol) in currentPieceMoves):
                        self.gameBoard = makeMove(self.gameBoard, startRow, 
                                                  startCol, targetRow, targetCol)
                        self.whiteTurn = False
                        self.blackTurn = True
                    else:
                        print('Not a legal move. Try again.')
                    self.moveFrom = None
                    self.moveTo = None
                    self.highlightedLocations = [ ]
                elif (self.moveFrom == None):
                    self.gettingMoveFrom = True
                    self.gettingMoveTo = False
                elif (self.moveTo == None):
                    self.gettingMoveFrom = False
                    self.gettingMoveTo = True
            elif (self.blackTurn):
                print("Black's Turn!")
                nextBoards = makeBoardsForNextMoves(self.gameBoard, 'black')
                minValue = 1000000000000 # high value for first comparision 
                bestBoard = None
                for board in nextBoards:
                    currValue = minimax(board, self.depthLevel, -1000000000000, 
                                        1000000000000, False)
                    if (currValue <= minValue):
                        minValue = currValue
                        bestBoard = board
                self.gameBoard = bestBoard
                self.whiteTurn = True
                self.blackTurn = False

    def keyPressed(self, event):
        if (event.key == 'q'):
            os._exit(0)

    def mousePressed(self, event):
        if (self.whiteTurn):
            if (self.gettingMoveFrom):
                self.selectedLocation = self.getCell(event.x, event.y)
                if (self.selectedLocation != None):
                    row, col = self.selectedLocation
                    if (self.gameBoard.board[row][col].piece == None):
                        print('No piece there. Try again.')
                    elif (self.gameBoard.board[row][col].piece.pieceColor != 'white'):
                        print('Invalid piece.')
                    else:
                        self.highlightedLocations.append(self.selectedLocation)
                        pieceLocation = pythonToHumanLocation(row, col)
                        legalPieceMoves = findLegalMovesOfPiece(self.gameBoard, row, 
                                                                col)[pieceLocation]
                        for move in legalPieceMoves:
                            self.highlightedLocations.append(move)
                        self.moveFrom = self.selectedLocation
                        print(self.moveFrom)
            elif (self.gettingMoveTo):
                self.selectedLocation = self.getCell(event.x, event.y)
                if (self.selectedLocation != None):
                    self.moveTo = self.selectedLocation
                    print(self.moveTo)
        x0 = self.boardOffset/4 - self.margin/3
        y0 = self.margin*38/4
        x1 = self.boardOffset/4 + self.margin*9/2
        y1 = self.margin*42/4
        if (x0 <= event.x <= x1) and (y0 <= event.y <= y1):
            self.whiteCheckmate = True

    def mouseMoved(self, event):
        self.mouseLocation = self.getCell(event.x, event.y)
    
    ############################################################################
    # View/Draw Functions
    ############################################################################

    def drawBoard(self, canvas):
        for row in range(8):
            for col in range(8):
                if ((row % 2 == 0) and (col % 2 == 0)) or\
                   ((row % 2 == 1) and (col % 2 == 1)):
                    color = rgbString(255, 206, 158)
                else:
                    color = rgbString(209, 139, 71)
                x0, y0, x1, y1 = self.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
        
        for row, col in self.highlightedLocations:
            x0, y0, x1, y1 = self.getCellBounds(row, col)
            if ((row % 2 == 0) and (col % 2 == 0)) or\
               ((row % 2 == 1) and (col % 2 == 1)):
                color = rgbString(206, 206, 206)
            else:
                color = rgbString(140, 140, 140)
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

    def drawPieces(self, canvas):
        for row in range(8):
            for col in range(8):
                piece = self.gameBoard.board[row][col].piece
                if (piece != None):
                    pieceType = piece.pieceType
                    pieceColor = piece.pieceColor
                    image = self.getImage(pieceType, pieceColor)

                    # draws image
                    x, y, _, _ = self.getCellBounds(row, col)
                    canvas.create_image(x, y, image=ImageTk.PhotoImage(image),
                                        anchor='nw')

    def drawAlgebraicNotation(self, canvas):
        scaler = self.gridWidth / 8
        nums = ['8', '7', '6', '5', '4', '3', '2', '1']
        lets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i in range(1, 9):
            canvas.create_text(self.width-self.margin//2, self.margin//2 + scaler*i,
                               text=f'{nums[i-1]}', font='Arial 25 bold')
            canvas.create_text(self.boardOffset+self.margin//2, 
                               self.margin//2 + scaler*i, text=f'{nums[i-1]}', 
                               font='Arial 25 bold')
            canvas.create_text(self.boardOffset+self.margin//2 + scaler*i, 
                               self.margin//2, text=f'{lets[i-1]}', 
                               font='Arial 25 bold')
            canvas.create_text(self.boardOffset+self.margin//2 + scaler*i, 
                               self.height-self.margin//2, text=f'{lets[i-1]}', 
                               font='Arial 25 bold')

    def drawSideWidget(self, canvas):
        # Basic titles
        canvas.create_rectangle(self.margin, self.margin, 
                                self.boardOffset-self.margin,
                                self.height-self.margin, width=6)
        canvas.create_text(self.boardOffset/2, 2*self.margin, anchor='s', 
                           text='1-Player Game', font='Helvetica 30 bold')
        canvas.create_text(self.boardOffset/4, self.margin*9/4, anchor='n',
                           text='Turn:', font='Helvetica 20 bold')
        
        # Turn titles
        if (self.whiteTurn):
            canvas.create_rectangle(self.boardOffset/4 + self.margin, self.margin*9/4,
                                    self.boardOffset/4 + self.margin*5/2,
                                    self.margin*11/4, fill='black')
            canvas.create_text(self.boardOffset/4 + self.margin*7/4, self.margin*9/4,
                               anchor='n', text='White', font='Helvetica 20 bold',
                               fill='white')
        elif (self.blackTurn):
            canvas.create_rectangle(self.boardOffset/4 + self.margin, self.margin*9/4,
                                    self.boardOffset/4 + self.margin*5/2,
                                    self.margin*11/4)
            canvas.create_text(self.boardOffset/4 + self.margin*7/4, self.margin*9/4,
                            anchor='n', text='Black', font='Helvetica 20 bold')
            if (not self.blackCheckmate) and (not self.whiteCheckmate):
                canvas.create_image(self.boardOffset/4 + self.margin*3, self.margin*9/4, 
                                    image=ImageTk.PhotoImage(self.hourGlassImage), 
                                    anchor='n')
        
        # Move titles
        canvas.create_text(self.boardOffset/4 - 4, self.margin*13/4, anchor='n',
                        text='From:', font='Helvetica 20 bold')
        canvas.create_text(self.boardOffset/4 + 15, self.margin*17/4, anchor='n',
                        text='To:', font='Helvetica 20 bold')
        if (self.whiteTurn) and (self.moveFrom != None):
            row, col = self.moveFrom
            canvas.create_rectangle(self.boardOffset/4 + self.margin, self.margin*13/4,
                                    self.boardOffset/4 + self.margin*5/2,
                                    self.margin*15/4, fill='black')
            canvas.create_text(self.boardOffset/4 + self.margin*7/4, self.margin*13/4,
                            anchor='n', text=pythonToHumanLocation(row, col), 
                            font='Helvetica 20 bold', fill='white')
            pieceLocation = pythonToHumanLocation(row, col)
            currentPieceMoves = findLegalMovesOfPiece(self.gameBoard, row, 
                                                    col)[pieceLocation]
            if (self.mouseLocation != None) and\
               (self.mouseLocation in currentPieceMoves):
                row, col = self.mouseLocation
                canvas.create_rectangle(self.boardOffset/4 + self.margin, self.margin*17/4,
                                        self.boardOffset/4 + self.margin*5/2,
                                        self.margin*19/4, fill='black')
                canvas.create_text(self.boardOffset/4 + self.margin*7/4, self.margin*17/4,
                                anchor='n', text=pythonToHumanLocation(row, col), 
                                font='Helvetica 20 bold', fill='white')
            
        # Board value titles
        canvas.create_text(self.boardOffset/4 + 55, self.margin*21/4, anchor='n',
                        text='Chance To Win:', font='Helvetica 20 bold')
        checks = findChecks(self.gameBoard)
        # adjustment for aggresiveness of AI
        currentBoardValue = self.gameBoard.boardValue() + 34
        if ('white' in checks):
            chanceToWin = '1.0%'
        elif ('black' in checks):
            chanceToWin = '99.0%'
        else:
            chanceToWin = f'{currentBoardValue + 50}%'
        if (currentBoardValue > 10000000):
            currentBoardValue = 49
            chanceToWin = '99.0%'
        elif (currentBoardValue < -1000000):
            currentBoardValue = -49
            chanceToWin = '1.0%'
        elif (self.blackTurn):
            chanceToWin = '...'
        canvas.create_text(self.boardOffset/4 + 220, self.margin*21/4, anchor='n',
                        text=chanceToWin, font='Helvetica 20 bold')
            
        # displays interpretation of percentage
        if ('white' in checks):
            canvas.create_rectangle(self.boardOffset/4 - self.margin/3, self.margin*24/4,
                                    self.boardOffset/4 + self.margin*9/2,
                                    self.margin*28/4, fill='white')
            canvas.create_text(self.boardOffset/4 + 125, self.margin*25/4, anchor='n',
                            text="White Is Checked!", font='Helvetica 20 bold',
                            fill='black')
        elif ('black' in checks):
            canvas.create_rectangle(self.boardOffset/4 - self.margin/3, self.margin*24/4,
                                    self.boardOffset/4 + self.margin*9/2,
                                    self.margin*28/4, fill='black')
            canvas.create_text(self.boardOffset/4 + 125, self.margin*25/4, anchor='n',
                            text="Black Is Checked!", font='Helvetica 20 bold',
                            fill='white')
        elif (currentBoardValue > 0):
            canvas.create_rectangle(self.boardOffset/4 - self.margin/3, self.margin*24/4,
                                    self.boardOffset/4 + self.margin*9/2,
                                    self.margin*28/4, fill='black')
            canvas.create_text(self.boardOffset/4 + 125, self.margin*25/4, anchor='n',
                            text="In White's Favor", font='Helvetica 20 bold',
                            fill='white')
        elif (currentBoardValue < 0):
            canvas.create_rectangle(self.boardOffset/4 - self.margin/3, self.margin*24/4,
                                    self.boardOffset/4 + self.margin*9/2,
                                    self.margin*28/4, fill='white')
            canvas.create_text(self.boardOffset/4 + 125, self.margin*25/4, anchor='n',
                            text="In Black's Favor", font='Helvetica 20 bold',
                            fill='black')
        
        # Next board value titles
        if (self.whiteTurn) and (self.moveFrom != None) and\
           (self.mouseLocation != None) and\
           (self.mouseLocation in currentPieceMoves):
            canvas.create_text(self.boardOffset/4 + 11, self.margin*29/4, anchor='n',
                               text='Change:', font='Helvetica 20 bold')
            tempBoard = self.gameBoard.copy()
            startRow, startCol = self.moveFrom
            targetRow, targetCol = self.mouseLocation
            nextBoard = makeMove(tempBoard, startRow, startCol, targetRow, targetCol)
            nextChecks = findChecks(nextBoard)
            nextChecks = findChecks(nextBoard)
            nextBoardValue = nextBoard.boardValue() + 34
            if ('white' in nextChecks):
                change = f'{1-currentBoardValue-50}%'
            elif ('black' in nextChecks):
                change = f'{99-currentBoardValue-50}%'
            else:
                currentChecks = findChecks(self.gameBoard)
                if ('white' in currentChecks) and ('white' not in nextChecks):
                    change = f'{abs(nextBoardValue-50 - 1)}%'
                elif ('black' in currentChecks) and ('black' not in nextChecks):
                    change = f'-{99 - nextBoardValue-50}%'
                else:
                    change = f'{nextBoardValue - currentBoardValue}%'
    
            if (self.gameBoard.blackIsChecked) and (not nextBoard.blackIsChecked):
                change = f'{99 - currentBoardValue}%'
            elif (self.gameBoard.whiteIsChecked) and (not nextBoard.whiteIsChecked):
                change = f'{1 - currentBoardValue}%'
            canvas.create_text(self.boardOffset/4 + 125, self.margin*29/4, 
                               anchor='n', text=change, font='Helvetica 20 bold')
        
        # resign button
        canvas.create_rectangle(self.boardOffset/4 - self.margin/3, self.margin*38/4,
                                self.boardOffset/4 + self.margin*9/2,
                                self.margin*42/4, fill='white')
        canvas.create_text(self.boardOffset/4 + 125, self.margin*39/4, anchor='n',
                        text="Resign", font='Helvetica 20 bold',
                        fill='black')

    def drawGameOverScreen(self, canvas, loser):
        canvas.create_rectangle(0, (self.height*2/5)-5, self.width, (self.height*3/5)+5,
                            fill='white')
        canvas.create_text(self.width/2, self.height/2, text=f'{loser} loses!',
                        font='Arial 50 bold')

    def redrawAll(self, canvas):
        self.drawBoard(canvas)
        self.drawPieces(canvas)
        self.drawAlgebraicNotation(canvas)
        self.drawSideWidget(canvas)
        if (self.blackCheckmate):
            self.drawGameOverScreen(canvas, 'Black')
        elif (self.whiteCheckmate):
            self.drawGameOverScreen(canvas, 'White')
