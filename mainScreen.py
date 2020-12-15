# File purpose:
# Main game file. Runs main screen and all opens up the chess game
# as well as showing leaderboard.

import time, string
from cmu_112_graphics import *
from withAInoVoice import *
from withAIwithVoice import *
from noAInoVoice import *
from noAIwithVoice import *

################################################################################
# Helper Functions
################################################################################

# taken from 112 website
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

# taken from 112 website
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

################################################################################
# Controller Functions
################################################################################

class Main_Screen(App):

    def appStarted(self):
        self.startTime = int(time.time())
        self.showingMainScreen = True
        self.askingForName = False
        self.name = ''
        self.leaderboard = readFile('leaderboard.txt')
        self.names = self.leaderboard.splitlines()
        self.showingLeaderboard = False
        self.cx, self.cy = self.width//2, self.height//2
        self.scrollLevel = 0
        self.depthLevel = 1

        # for buttons:
        self.halfWidth = self.width//4
        self.halfHeight = self.height//22
        self.voiceActivated = False
        self.cursorIsBlinking = False
        self.textBoxIsSelected = False
        self.isTyping = False

    def timerFired(self):
        if ((int(time.time()) - self.startTime) % 2 == 0):
            self.cursorIsBlinking = True
        else:
            self.cursorIsBlinking = False
        if (not self.textBoxIsSelected):
            self.name = ''

    def keyPressed(self, event):
        self.isTyping = True
        if (self.textBoxIsSelected):
            if (event.key == 'Space') and (len(self.name) < 16):
                self.name += ' '
            elif (event.key == 'Backspace'):
                self.name = self.name[:-1] if (len(self.name) != 0) else ''
            elif (event.key in string.ascii_letters) and (len(self.name) < 16):
                self.name += event.key
            elif (event.key == 'Enter') and (self.askingForName) and\
                 (len(self.name) != 0):
                if (self.name not in self.leaderboard):
                    print(len(self.name))
                    if (len(self.name) < 8):
                        contents = self.leaderboard + self.name + 2*'\t' + '0' + '\n'
                    elif (len(self.name) < 16):
                        contents = self.leaderboard + self.name + '\t' + '0'+ '\n'
                    writeFile('leaderboard.txt', contents)
                self.leaderboard = readFile('leaderboard.txt')
                self.names = self.leaderboard.splitlines()
                self.askingForName = False
                contents = str(self.depthLevel) + '\n' + str(self.name)
                writeFile('settings.txt', contents)
                if (self.voiceActivated):
                    Singleplayer_ChessWV(width=1200, height=700)
                elif (not self.voiceActivated):
                    Singleplayer_ChessNV(width=1200, height=700)

        if (self.showingLeaderboard):
            if (event.key == 'Up'):
                self.scrollLevel -= 1 if (self.scrollLevel > 0) else 0
            elif (event.key == 'Down'):
                self.scrollLevel += 1 if (self.scrollLevel <= len(self.names)-14) else 0

    def keyReleased(self, event):
        self.isTyping = False

    def mousePressed(self, event):
        cx, cy = self.cx, self.cy
        halfWidth = self.halfWidth
        halfHeight = self.halfHeight

        if (not self.showingMainScreen):
            x0 = self.width*18//20
            y0 = self.height*18//20
            x1 = x0 + self.width//20
            y1 = y0 + self.height//20
            if (x0 <= event.x <= x1) and (y0 <= event.y <= y1):
                self.appStarted()
                self.voiceActivated = False

        if (self.showingMainScreen):
            # play AI chess
            cy = self.cy - halfHeight*2.5
            if (cx-halfWidth <= event.x <= cx+halfWidth) and\
               (cy-halfHeight <= event.y <= cy+halfHeight):
                self.showingMainScreen = False
                self.askingForName = True

            # play standard chess
            cy = self.cy
            if (cx-halfWidth <= event.x <= cx+halfWidth) and\
            (cy-halfHeight <= event.y <= cy+halfHeight):
                if (self.voiceActivated == True):
                    Multiplayer_ChessWV(width=1200, height=700)
                elif (self.voiceActivated == False):
                    Multiplayer_ChessNV(width=1200, height=700)
            
            # open leaderboard
            cy = self.cy + halfHeight*2.5
            if (cx-halfWidth <= event.x <= cx+halfWidth) and\
               (cy-halfHeight <= event.y <= cy+halfHeight):
                self.showingLeaderboard = True
                self.showingMainScreen = False

            # enable voice commands
            x0 = self.width//15
            y0 = self.height*4//5 + self.height//20
            x1 = x0 + self.width//20
            y1 = y0 + self.height//20
            if (x0 <= event.x <= x1) and\
               (y0 <= event.y <= y1):
                self.voiceActivated = not self.voiceActivated
        
        elif (self.askingForName):
            if (cx-halfWidth <= event.x <= cx+halfWidth) and\
               (cy-halfHeight <= event.y <= cy+halfHeight):
                self.textBoxIsSelected = not self.textBoxIsSelected

            cy = self.height//2 - 150
            third = (halfWidth*2)/3
            if (cx-halfWidth <= event.x <= cx-halfWidth+third) and\
               (cy-halfHeight <= event.y <= cy+halfHeight):
                self.depthLevel = 1
            elif (cx-halfWidth+third <= event.x <= cx-halfWidth+2*third) and\
                 (cy-halfHeight <= event.y <= cy+halfHeight):
                self.depthLevel = 2
            elif (cx-halfWidth+2*third <= event.x <= cx+halfWidth) and\
                 (cy-halfHeight <= event.y <= cy+halfHeight):
                self.depthLevel = 3

            cy = self.cy + halfHeight*2.5
            if (cx-halfWidth <= event.x <= cx+halfWidth) and\
               (cy-halfHeight <= event.y <= cy+halfHeight) and\
               (len(self.name) != 0):
                if (self.name not in self.leaderboard):
                    if (len(self.name) < 8):
                        contents = self.leaderboard + self.name + 2*'\t' + '0' + '\n'
                    elif (len(self.name) < 16):
                        contents = self.leaderboard + self.name + '\t' + '0'+ '\n'
                    writeFile('leaderboard.txt', contents)
                self.leaderboard = readFile('leaderboard.txt')
                self.names = self.leaderboard.splitlines()
                self.askingForName = False
                contents = str(self.depthLevel) + '\n' + str(self.name)
                writeFile('settings.txt', contents)
                if (self.voiceActivated):
                    Singleplayer_ChessWV(width=1200, height=700)
                elif (not self.voiceActivated):
                    Singleplayer_ChessNV(width=1200, height=700)

        elif (self.showingLeaderboard):
            x0 = self.cx - 150
            y0 = self.cy - 150
            x1 = self.cx + 150
            y1 = self.cy - 125
            if (x0 <= event.x <= x1) and (y0 <= event.y <= y1):
                self.scrollLevel -= 1 if (self.scrollLevel > 0) else 0
            y0 = self.cy + 275
            y1 = self.cy + 300
            if (x0 <= event.x <= x1) and (y0 <= event.y <= y1):
                self.scrollLevel += 1 if (self.scrollLevel <= len(self.names)-14) else 0

    ############################################################################
    # Draw Functions
    ############################################################################

    def drawNames(self, canvas):
        cx = self.cx
        cy = self.cy
        halfHeight = 200
        halfWidth = 150
        canvas.create_rectangle(cx-halfWidth, cy-halfWidth, cx+halfWidth,
                                cy+halfHeight+100)
        scalar = 0
        cy = self.cy - 100
        cx = self.cx - halfWidth

        if (len(self.names) > 14):
            names = self.names[self.scrollLevel:13+self.scrollLevel]
        else:
            names = self.names

        scalar = 0
        for name in names:
            canvas.create_text(cx+5, cy+30*scalar, text=name, font='Helvetica 20',
                                anchor='w')
            scalar += 1

    def drawInputs(self, canvas):
        cx, cy = self.cx, self.cy
        halfWidth = self.halfWidth
        halfHeight = self.halfHeight

        # draws back button to go back to main screen
        if (not self.showingMainScreen):
            x0 = self.width*18//20
            y0 = self.height*18//20
            x1 = x0 + self.width//20
            y1 = y0 + self.height//20
            halfW = (x1 - x0) // 2
            halfH = (y1 - y0) // 2
            canvas.create_rectangle(x0, y0, x1, y1)
            canvas.create_text(x0+halfW, y0+halfH, text='↻', font='Helvetica 35')

        # draws inputs for main screen
        if (self.showingMainScreen):
            # AI mode button
            cy = self.cy - halfHeight*2.5
            canvas.create_rectangle(cx-halfWidth, cy-halfHeight, 
                                    cx+halfWidth, cy+halfHeight,
                                    fill='white', outline='black')
            canvas.create_text(cx, cy, text='1-Player Game', 
                            font='Helvetica 20 bold')

            # Standard mode button
            cy = self.cy
            canvas.create_rectangle(cx-halfWidth, cy-halfHeight, 
                                    cx+halfWidth, cy+halfHeight,
                                    fill='white', outline='black')
            canvas.create_text(cx, cy, text='2-Player Game', 
                            font='Helvetica 20 bold')
            
            # Leaderboard button
            cy = self.cy + halfHeight*2.5
            canvas.create_rectangle(cx-halfWidth, cy-halfHeight, 
                                    cx+halfWidth, cy+halfHeight,
                                    fill='white', outline='black')
            canvas.create_text(cx, cy, text='AI Leaderboard', 
                            font='Helvetica 20 bold')
            
            # Voice activated checkbox
            x0 = self.width//15
            y0 = self.height*4//5 + self.height//20
            x1 = x0 + self.width//20
            y1 = y0 + self.height//20
            canvas.create_rectangle(x0, y0, x1, y1)
            if (self.voiceActivated):
                canvas.create_text(x0+x0/2, y0+self.height//40, text='✓', 
                                   font='Helvetica 29 bold', fill='red')
        
        # draws inputs for name screen before leaderboard screen
        elif (self.askingForName):
            canvas.create_rectangle(cx-halfWidth, cy-halfHeight, 
                                    cx+halfWidth, cy+halfHeight,
                                    fill='white', outline='black')
            cy = self.height//2 - 200
            canvas.create_text(cx-halfWidth, cy, text='AI Difficulty:',
                               font='Helvetica 20 bold', anchor='w')
            cy = self.height//2 - 150
            third = (halfWidth*2)/3
            if (self.depthLevel == 1):
                width1 = 5
                outline1 = 'red'
                width2 = width3 = 1
                outline2 = outline3 = 'black'
            elif (self.depthLevel == 2):
                width2 = 5
                outline2 = 'red'
                width1 = width3 = 1
                outline1 = outline3 = 'black'
            elif (self.depthLevel == 3):
                width3 = 5
                outline3 = 'red'
                width2 = width1 = 1
                outline2 = outline1 = 'black'
                canvas.create_text(cx-halfWidth+third*5//2, cy-50, 
                                   text='WARNING: Needs beefy computer',
                                   fill='red')
            canvas.create_rectangle(cx-halfWidth, cy-halfHeight,
                                    cx-halfWidth+third, cy+halfHeight, width=width1,
                                    outline=outline1)
            canvas.create_text(cx-halfWidth+third//2, cy, 
                               text='Easy', font='Helvetica 20 bold')
            canvas.create_rectangle(cx-halfWidth+third, cy-halfHeight,
                                    cx-halfWidth+2*third, cy+halfHeight, width=width2,
                                    outline=outline2)
            canvas.create_text(cx-halfWidth+third*3//2, cy,
                               text='Medium', font='Helvetica 20 bold',)
            canvas.create_rectangle(cx-halfWidth+2*third, cy-halfHeight,
                                    cx+halfWidth, cy+halfHeight, width=width3,
                                    outline=outline3)
            canvas.create_text(cx-halfWidth+third*5//2, cy,
                               text='Hard', font='Helvetica 20 bold')

            cy = self.height//2
            if (self.textBoxIsSelected):
                canvas.create_rectangle(cx-halfWidth, cy-halfHeight, 
                                            cx+halfWidth, cy+halfHeight,
                                            width=5, outline='red')
                if (self.cursorIsBlinking) or (self.isTyping):
                    text = self.name + '|'
                else:
                    text = self.name
                canvas.create_text(cx-halfWidth+5, cy, text=text,
                                   anchor='w', font='Helvetica 20 bold')

            cy = self.cy + halfHeight*2.5
            canvas.create_rectangle(cx-halfWidth/2, cy-halfHeight*2/3, 
                                    cx+halfWidth/2, cy+halfHeight*2/3,
                                    fill='white', outline='black')
            canvas.create_text(cx, cy+halfHeight*1/3, text='Enter',
                               font='Helvetica 15 bold', anchor='s')

        elif (self.showingLeaderboard):
            x0 = self.cx - 150
            y0 = self.cy - 150
            x1 = self.cx + 150
            y1 = self.cy - 125
            canvas.create_rectangle(x0, y0, x1, y1)
            y0 = self.cy + 275
            y1 = self.cy + 300
            canvas.create_rectangle(x0, y0, x1, y1)
            cx = self.cx
            cy = self.cy - 139
            canvas.create_text(cx, cy, text='▲', font='Helvetica 15 bold')
            cy = self.cy + 288
            canvas.create_text(cx, cy, text='▼', font='Helvetica 15 bold')

    def drawTitles(self, canvas):
        if (self.showingMainScreen):
            canvas.create_text(self.width//2, self.height//6, text="David's Chess!",
                            font='Helvetica 70 bold')
            canvas.create_text(self.width//7, self.height*4//5, text='Options:', 
                            font='Helvetica 20 bold')
            canvas.create_text(self.width//15+self.width*6//40, 
                            self.height*4//5+self.height*3//40,
                            text='Voice Enabled', font='Helvetica 10 bold')
        
        elif (self.askingForName):
            cx = self.cx
            cy = self.cy - self.halfHeight*2.5
            canvas.create_text(cx, cy, text='Enter Your Name:', 
                            font='Helvetica 20 bold')  
        
        elif (self.showingLeaderboard):
            cx = self.cx
            cy = self.cy
            halfHeight = 200
            halfWidth = 150
            canvas.create_text(self.width//2, self.height//6, text="AI Leaderboard",
                               font='Helvetica 70 bold')

    def redrawAll(self, canvas):
        self.drawTitles(canvas)
        self.drawInputs(canvas)
        if (self.showingLeaderboard):
            self.drawNames(canvas)

Main_Screen(width=700, height=700)
