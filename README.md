# David's Chess
My 15-112 Term Project!

This is a small chess game app that you can play singleplayer with against an AI, multiplayer on the same computer, and can be voice enabled to take move commands and can dictate back to you the move that it made, for your amusement. To run, all you need to do is open the mainScreen.py file.

Dependencies:
- pyaudio
- speech_recognition
- gTTS
- cmu_112_graphics
- mpg123
- Windows (have not tried on other operating systems)

Speech commands:
- To make a move, say the square you're moving from/to when prompted by the ear icon as a location the board     (i.e. 'a6')
- If you stated a square from which you don't want to move from anymore, just say 'go back'
- To quit the game, say 'quit' at any time
- To resign, say 'resign' or 'i give up'
