# File purpose:
# Runs chess app in multiplayer mode with voice enabled inputs

from cmu_112_graphics import *
from game import *
import speech_recognition as sr

################################################################################
# Helper Functions
################################################################################

# taken from 112 website
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

class Multiplayer_ChessWV(App):
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

    def locationFromText(self, text):
        lets = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}
        nums = {'1', '2', '3', '4', '5', '6', '7', '8'}
        potentialLocations = [ ]
        
        # checks for every location
        for let in lets:
            for num in nums:
                if (let+num in text):
                    row, col = humanToPythonLocation(let+num)
                    if (self.whiteTurn) and (self.moveFrom == None) and\
                       (self.gameBoard.board[row][col].piece != None) and\
                       (self.gameBoard.board[row][col].piece.pieceColor == 'white'):
                        potentialLocations += [humanToPythonLocation(let+num)]
                    elif (self.whiteTurn) and (self.moveFrom != None) and\
                         (self.moveTo == None):
                        potentialLocations += [humanToPythonLocation(let+num)]
                    if (self.blackTurn) and (self.moveFrom == None) and\
                       (self.gameBoard.board[row][col].piece != None) and\
                       (self.gameBoard.board[row][col].piece.pieceColor == 'black'):
                        potentialLocations += [humanToPythonLocation(let+num)]
                    elif (self.blackTurn) and (self.moveFrom != None) and\
                         (self.moveTo == None):
                        potentialLocations += [humanToPythonLocation(let+num)]

        # if the speech thing couldn't find any location, then return False
        if (len(potentialLocations) == 0):
            return False, None

        # if the speech thing did find something, and there is more than one
        # location, then use the last one found
        else:
            location = potentialLocations.pop()
            if (self.moveFrom == None):
                row, col = location
                humanLocation = pythonToHumanLocation(row, col)
                nextMoves = findLegalMovesOfPiece(self.gameBoard, row, 
                                                  col)[humanLocation]
                self.highlightedLocations.append(location)
                for move in nextMoves:
                    self.highlightedLocations.append(move)
                if (len(nextMoves) != 0):
                    return True, location
                else:
                    self.highlightedLocations = [ ]
                    return False, None
            elif (self.moveTo == None):
                row, col = self.moveFrom
                humanLocation = pythonToHumanLocation(row, col)
                nextMovesOfStartPiece = findLegalMovesOfPiece(self.gameBoard, 
                                                              row, col)[humanLocation]
                if (location in nextMovesOfStartPiece):
                    return True, location
                else:
                    return False, None

    def getLocation(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio).lower()
            if ('resign' in text) or ('i give up' in text):
                if (self.blackTurn):
                    self.blackCheckmate = True
                elif (self.whiteTurn):
                    self.whiteCheckmate = True
                return None
            elif ('quit' in text):
                os.system('mpg123 exit.mp3')
                os._exit(0)
            elif (self.moveFrom != None) and ('go back' in text):
                self.moveFrom = None
                self.highlightedLocations = [ ]
                return None
            print(text)
            containsValidLocation, location = self.locationFromText(text)
            if (containsValidLocation):
                return location
            else:
                print('Please say a valid location.')
                os.system('mpg123 invalidmove.mp3')
        except Exception:
            print("Sorry, I couldn't understand that.")
            os.system('mpg123 sorry.mp3')

    ############################################################################
    # Model & Controller Functions
    ############################################################################

    def appStarted(self):
        # game setup
        self.timerDelay = 1000
        self.margin = 58
        self.gridWidth = 700 - 2*self.margin
        self.gridHeight = 700 - 2*self.margin
        self.boardOffset = 500
        self.gameBoard = Gameboard()
        self.gameBoard.setPieces()
        self.mouseLocation = None
        self.highlightedLocations = [ ]
        self.whiteCheckmate = False
        self.blackCheckmate = False
        self.takingTurn = False
        self.isListening = True

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

        # ear image taken from:
        # https://www.pinterest.com/pin/584482857867586866/
        self.listeningImage = self.loadImage('images/listening.webp')
        self.listeningImage = self.scaleImage(self.listeningImage, 0.03)

    def timerFired(self):
        if (not self.takingTurn):
            self.takeTurn()

    def keyPressed(self, event):
        if (event.key == 'q'):
            os._exit(0)

    def takeTurn(self):
        # stops timerFired from taking a turn
        self.takingTurn = True

        # checks board for a checkmate:
        checks = findChecks(self.gameBoard)
        if ('white' in checks) and (self.blackTurn):
            self.whiteCheckmate = True
        if ('black' in checks) and (self.whiteTurn):
            self.blackCheckmate = True

        if (not self.blackCheckmate) and (not self.whiteCheckmate):
            if (self.whiteTurn):
                print("White's Turn!")
                self.isListening = True
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
                    self.moveFrom = self.getLocation()
                elif (self.moveTo == None):
                    self.moveTo = self.getLocation()
                    self.isListening = False
            elif (self.blackTurn):
                self.isListening = True
                if (self.moveFrom != None) and (self.moveTo != None):
                    startRow, startCol = self.moveFrom
                    targetRow, targetCol = self.moveTo
                    pieceLocation = pythonToHumanLocation(startRow, startCol)
                    currentPieceMoves = findLegalMovesOfPiece(self.gameBoard, startRow, 
                                                            startCol)[pieceLocation]
                    if ((targetRow, targetCol) in currentPieceMoves):
                        self.gameBoard = makeMove(self.gameBoard, startRow, 
                                                  startCol, targetRow, targetCol)
                        self.whiteTurn = True
                        self.blackTurn = False
                    else:
                        print('Not a legal move. Try again.')
                    self.moveFrom = None
                    self.moveTo = None
                    self.highlightedLocations = [ ]
                elif (self.moveFrom == None):
                    self.moveFrom = self.getLocation()
                elif (self.moveTo == None):
                    self.moveTo = self.getLocation()
                    self.isListening = False
    
        # lets timerFired take another turn
        self.takingTurn = False

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

        # Move titles
        canvas.create_text(self.boardOffset/4 - 4, self.margin*13/4, anchor='n',
                        text='From:', font='Helvetica 20 bold')
        canvas.create_text(self.boardOffset/4 + 15, self.margin*17/4, anchor='n',
                        text='To:', font='Helvetica 20 bold')
        if (self.isListening) and (self.moveFrom == None):
            canvas.create_image(self.boardOffset/4 + self.margin*3, self.margin*13/4, 
                                image=ImageTk.PhotoImage(self.listeningImage), 
                                anchor='n')
        elif (self.isListening) and (self.moveTo == None):
            canvas.create_image(self.boardOffset/4 + self.margin*3, self.margin*17/4, 
                                image=ImageTk.PhotoImage(self.listeningImage), 
                                anchor='n')
        if (self.moveFrom != None):
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
            if (self.moveTo != None):
                row, col = self.moveTo
                canvas.create_rectangle(self.boardOffset/4 + self.margin, self.margin*17/4,
                                        self.boardOffset/4 + self.margin*5/2,
                                        self.margin*19/4, fill='black')
                canvas.create_text(self.boardOffset/4 + self.margin*7/4, self.margin*17/4,
                                anchor='n', text=pythonToHumanLocation(row, col), 
                                font='Helvetica 20 bold', fill='white')
            
        # Board value titles
        canvas.create_text(self.boardOffset/4 + 55, self.margin*21/4, anchor='n',
                        text='Chance to Win:', font='Helvetica 20 bold')
        checks = findChecks(self.gameBoard)
        # adjustment for aggresiveness of AI
        currentBoardValue = self.gameBoard.boardValue() + 34
        if ('white' in checks):
            chanceToWin = '1.0%'
        elif ('black' in checks):
            chanceToWin = '99.0%'
        else:
            chanceToWin = f'{currentBoardValue + 50}%'
        if (currentBoardValue > 10000000) or (currentBoardValue < -1000000):
            chanceToWin = '...'
        canvas.create_text(self.boardOffset/4 + 220, self.margin*21/4, anchor='n',
                        text=chanceToWin, font='Helvetica 20 bold')

        # displays interpretation of the percentage
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
        if (self.moveFrom != None) and (self.moveTo != None):
            canvas.create_text(self.boardOffset/4 + 11, self.margin*29/4, anchor='n',
                               text='Change:', font='Helvetica 20 bold')
            tempBoard = self.gameBoard.copy()
            startRow, startCol = self.moveFrom
            targetRow, targetCol = self.moveTo
            nextBoard = makeMove(tempBoard, startRow, startCol, targetRow, targetCol)
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
            if (nextBoardValue > 10000000):
                change = f'{99 - currentBoardValue}'
            elif (nextBoardValue < -1000000):
                change = f'{1 - currentBoardValue}'
            canvas.create_text(self.boardOffset/4 + 125, self.margin*29/4, 
                               anchor='n', text=change, font='Helvetica 20 bold')     

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
