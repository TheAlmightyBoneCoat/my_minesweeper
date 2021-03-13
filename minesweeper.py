# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 14:34:25 2018

@author: Kyla Powell

A Minesweeper game that I created after boarding a six-hour flight
and discovering my computer did not have it installed.
"""

#Get our Pygame stuff initialized
import pygame
pygame.init()
import random #To randomly place mines

#Define some colors...
black = [0,0,0]
white = [255,255,255]
red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]

#Define some constants
TILE_WIDTH = 20
TILE_HEIGHT = 26
MARGIN_WIDTH = 40        #Width of the screen border
MARGIN_HEIGHT = MARGIN_WIDTH
BUTTON_BETWEEN_WIDTH = 2 #How much space in between the buttons
BUTTON_BETWEEN_HEIGHT = BUTTON_BETWEEN_WIDTH
NUM_ROWS = 16    #How many rows of tiles?
NUM_COLUMNS = 30 #How many columns of tiles?
NUM_MINES = 99   #How many mines are on the board?

#Clamp maximum number of mines to number of tiles, minus corners
if NUM_MINES > (NUM_ROWS * NUM_COLUMNS) - 16:
  NUM_MINES = NUM_ROWS * NUM_COLUMNS - 16
VAL_MINE = -1 #Special value to indicate this tile is a mine
VAL_BLANK = 9 #Shows this tile's value needs to be calculated

#Mouse button values
LEFT_CLICK = 1
RIGHT_CLICK = 3

#Option so that the first click is never on a mine
FIRST_CLICK_PROTECTED = True
FIRST_CLICK_HAPPENED = False

#Keep track of progress toward win condition
TILES_REVEALED = 0
#Keymapping
REVEAL_KEY = pygame.K_j
FLAG_KEY = pygame.K_k

#Move the tile selector around the grid
LEFT_KEY = pygame.K_a
UP_KEY = pygame.K_w
RIGHT_KEY = pygame.K_d
DOWN_KEY = pygame.K_s

#Input mode definitions
MOUSE_INPUT = 0
KEY_INPUT = 1
INPUT_MODE = MOUSE_INPUT

#Set up the window
screenSize = [1000,700]
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("Minesweeper")

#Load images
hiddenTile = pygame.image.load("minesweeper_data/hiddenTile.png").convert()
blankTile = pygame.image.load("minesweeper_data/blankTile.png").convert()
flagTile = pygame.image.load("minesweeper_data/flaggedTile.png").convert()
incorrectFlag = pygame.image.load("minesweeper_data/incorrectFlag.png").convert()
mineTile = pygame.image.load("minesweeper_data/mine.png").convert()
oneTile = pygame.image.load("minesweeper_data/oneTile.png").convert()
twoTile = pygame.image.load("minesweeper_data/twoTile.png").convert()
threeTile = pygame.image.load("minesweeper_data/threeTile.png").convert()
fourTile = pygame.image.load("minesweeper_data/fourTile.png").convert()
fiveTile = pygame.image.load("minesweeper_data/fiveTile.png").convert()
sixTile = pygame.image.load("minesweeper_data/sixTile.png").convert()
sevenTile = pygame.image.load("minesweeper_data/sevenTile.png").convert()
eightTile = pygame.image.load("minesweeper_data/eightTile.png").convert()
tileSelected = pygame.image.load("minesweeper_data/tileSelected.png").convert()
invisible = pygame.image.load("minesweeper_data/invisible.png").convert()
tileSelected.set_colorkey(white)
invisible.set_colorkey(white)

#Make a convenient array for number of mines = image index
tileImagesArray = [blankTile, oneTile, twoTile, threeTile, fourTile, fiveTile,
    sixTile, sevenTile, eightTile]

#Sets to true when we want to exit the main loop
done = False
#Game state variables
GAME_IN_PROGRESS = 0
GAME_WIN = 1
GAME_LOSE = 2
currentGameState = GAME_IN_PROGRESS

#Our array of tiles
grid = []

#Clickable tile class
class Tile(pygame.sprite.Sprite):
    x = 0 #Column in grid
    y = 0 #Row in grid
    value = VAL_BLANK #How many mines surround this one; -1 if this is a mine
    hidden = True #Is this tile revealed?
    flagged = False #Did the user place a flag here?

    #Init array and sprite data
    def __init__(self, x, y):
        super().__init__()
        self.image = hiddenTile
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        #Calculate for size of each tile, width of screen border, space between
        #tiles.....
        self.rect.x = x * (TILE_WIDTH + BUTTON_BETWEEN_WIDTH) + MARGIN_WIDTH
        self.rect.y = y * (TILE_HEIGHT + BUTTON_BETWEEN_HEIGHT) + MARGIN_HEIGHT
        
    #Sets this tile to a mine.
    #Return: true if tile was successfully set; false if it was already a mine
    def setMine(self):
      if self.value != VAL_MINE:
        self.value = VAL_MINE
        return True
      else:
        return False
        
    #Calculates the number of mines surrounding this tile.
    #If the function returns VAL_MINE, this tile is a mine.
    def getValue(self):
      #Am I a mine?
      if (self.value == VAL_MINE):
        return VAL_MINE
      
      #Has my value been calculated already?
      if (self.value != VAL_BLANK):
        return self.value
      
      #Otherwise, let's check if any of my neighbors are mines
      #It's OK to check ourselves, since we've established we're not a mine
      self.value = 0
      for i in range(self.y - 1, self.y + 2):
        for j in range(self.x - 1, self.x + 2):
          #If the value is in valid range
          if (i >= 0 and i < NUM_ROWS and j >= 0 and j < NUM_COLUMNS):
            #Check if it's a mine
            if (grid[i][j].value == VAL_MINE):
              self.value += 1
      
      #Return the sum
      return self.value


    #Undo all user modification of this tile
    def reset(self):
      self.image = hiddenTile
      self.value = VAL_BLANK
      self.hidden = True
      self.flagged = False



    #Reveals this tile.
    #If it's blank, other tiles around it are also revealed.
    #If it's a mine, the game ends.
    def reveal(self):
      #Am I already revealed
      if not self.hidden:
        return
      
      else:
        self.hidden = False
        
        #If I'm a mine
        if self.value == VAL_MINE:
          #Make sure this isn't a protected tile
          if (not FIRST_CLICK_PROTECTED) or FIRST_CLICK_HAPPENED:
            lose()
            return
          
          else:
            self.value = VAL_BLANK
            print("Mine removed from protected tile!")
            
        #If there are no surrounding mines
        if self.getValue() == 0:
          #Reveal all surrounding tiles
          #Be careful not to call reveal on yourself again
          for i in range(self.y - 1, self.y + 2):
            if i >= 0 and i < NUM_ROWS:
              for j in range(self.x - 1, self.x + 2):
                #If this is a valid value
                 if j >= 0 and j < NUM_COLUMNS:
                  #If we're not checking ourself
                  if i != self.y or j != self.x:
                    grid[i][j].reveal()
                    
        self.image = tileImagesArray[self.getValue()]
        global TILES_REVEALED
        TILES_REVEALED += 1


    #Sets flagged to true and changes image accordingly
    def flag(self):
      #Can't flag revealed tile
      if self.hidden:
        self.flagged = True
        self.image = flagTile

    #Sets flagged to false and changes image accordingly
    def unflag(self):
      self.flagged = False
      self.image = hiddenTile

    #Action to take when left-clicked
    #Reveal myself, and record that the first click happened
    def onLeftClick(self):
      global FIRST_CLICK_HAPPENED
      if currentGameState == GAME_IN_PROGRESS:
        if not self.flagged:
          self.reveal()
        FIRST_CLICK_HAPPENED = True

    #Action to take when right-clicked
    #Toggle flagged status
    def onRightClick(self):
      #Don't respond to input if game is over, and don't flag if we're revealed
      if currentGameState == GAME_IN_PROGRESS:
        #Toggle flagged status
        if self.flagged == True:
          self.unflag()
        else:
          self.flag()



#Object for the tile selector
class tileHighlighter(pygame.sprite.Sprite):
  x = 0
  y = 0
  hidden = True

  def __init__(self):
    super().__init__()
    self.image = invisible
    self.rect = self.image.get_rect()
    self.rect.x = MARGIN_WIDTH + (self.x * (TILE_WIDTH + BUTTON_BETWEEN_WIDTH))
    self.rect.y = MARGIN_HEIGHT + (self.y * (TILE_HEIGHT + BUTTON_BETWEEN_HEIGHT))

  #Adds the given x and y to this tile's coordinates.
  #Note these are grid coordinates, not screen coordinates.
  #x - How much to add to the x-position.
  #y - How much to add to the y-position.
  def addPos(self, x, y):
    #print("Highlighter went from x = " + str(self.x), end=" ")
    self.x += x
    
    #Did we go out of bounds?
    if (self.x < 0):
      self.x = NUM_COLUMNS - 1
    elif self.x >= NUM_COLUMNS:
      self.x = 0
      
    self.rect.x = MARGIN_WIDTH + self.x * (TILE_WIDTH + BUTTON_BETWEEN_WIDTH)
    #print("to x = " + str(self.x), end = ", ")

    #print("y = " + str(self.y), end=" ")
    self.y += y
    
    # Do another out-of-bounds check
    if (self.y < 0):
      self.y = NUM_ROWS - 1
    elif self.y >= NUM_ROWS:
      self.y = 0
      
    self.rect.y = MARGIN_HEIGHT + self.y * (TILE_HEIGHT + BUTTON_BETWEEN_HEIGHT)
    #print("to y = " + str(self.y))

  #Some addPos calls for readability
  def moveRight(self):
    self.addPos(1, 0)

  def moveLeft(self):
    self.addPos(-1, 0)

  def moveUp(self):
    self.addPos(0, -1)

  def moveDown(self):
    self.addPos(0, 1)

  #Process user input
  #TODO: Adapt to reset button
  def move(self, key):
    global INPUT_MODE
    global grid
    
    # Are we just getting into key mode?
    if INPUT_MODE == MOUSE_INPUT:
      INPUT_MODE = KEY_INPUT
      self.spawn()
      return
    
    # Movement
    if (key == LEFT_KEY):
      self.moveLeft()
    elif (key == RIGHT_KEY):
      self.moveRight()
    elif (key == UP_KEY):
      self.moveUp()
    elif (key == DOWN_KEY):
      self.moveDown()

    #Reveal or flag tile
    #TODO: Adapt for reset and settings buttons
    elif (key == REVEAL_KEY):
      grid[self.y][self.x].onLeftClick()
    elif (key == FLAG_KEY):
      grid[self.y][self.x].onRightClick()


  #Reveal ourselves in key mode
  def spawn(self):
    self.image = tileSelected
    self.x = 0
    self.y = 0
    self.rect = self.image.get_rect()
    self.rect.x = MARGIN_WIDTH + self.x * (TILE_WIDTH + BUTTON_BETWEEN_WIDTH)
    self.rect.y = MARGIN_HEIGHT + self.y * (TILE_HEIGHT + BUTTON_BETWEEN_HEIGHT)

  #Hide ourselves in mouse mode
  def despawn(self):
    self.image = invisible

  #Compatibility functions - essentially useless
  def onLeftClick(self):
    pass

  def onRightClick(self):
    pass


highlightTile = tileHighlighter()



#Sets tile width and height parameters to the size of a loaded image
#By default, it's set according to hiddenTile.
def setTileDims(image = hiddenTile):
  global TILE_WIDTH
  global TILE_HEIGHT
  dimsRect = image.get_rect()
  TILE_WIDTH = dimsRect.x
  print(TILE_WIDTH, end=" ")
  TILE_HEIGHT = dimsRect.y
  print(TILE_HEIGHT)



#A general button class
class Button(pygame.sprite.Sprite):
  message = ""
  color = blue
  textColor = black
  fontName = "Calibiri"
  fontSize = 30
  font = ""
  text = ""
  width = ""
  height = ""

  def __init__(self, x, y, width, height):
    super().__init__()
    self.image = pygame.Surface([width, height])
    self.image.fill(blue)
    self.width = width
    self.height = height
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    #self.message = message
    #self.regenText()

  #Regenerates text object
  def regenText(self):
    self.font = pygame.font.SysFont(self.fontName, self.fontSize, True, False)
    self.text = self.font.render(self.message, True, self.textColor)

  #Sets font and regenerates text
  def setFontName(self, fontName):
    self.font = fontName
    self.regenText()

  #Sets message and regenerates text
  def setMessage(self, newMessage):
    self.message = newMessage
    self.regenText()

  #Sets font size and regenerates text
  def setFontSize(self, fontSize):
    self.fontSize = fontSize
    self.regenText()

  #Sets text color and regenerates text
  def setFontColor(self, fontColor):
    self.fontColor = fontColor
    self.regenText()

  #Sets button color
  def setColor(self, color):
    self.color = color



#Reset button class
class ResetButton(Button):
  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)

  #Resets the game
  def onLeftClick(self):
    global currentGameState
    global FIRST_CLICK_HAPPENED
    global TILES_REVEALED
    resetBoard()
    placeMines()
    currentGameState = GAME_IN_PROGRESS
    FIRST_CLICK_HAPPENED = False
    TILES_REVEALED = 0

  #Does nothing; purely to fit in spritesGroup()
  def onRightClick(self):
    pass
    
      

#Reveals all mines and incorrect flags
def lose():
  global currentGameState
  currentGameState = GAME_LOSE
  for i in range(NUM_ROWS):
    for j in range(NUM_COLUMNS):
      #Was it flagged?
      
      if grid[i][j].flagged == True:
        #Change it if it was flagged incorrectly
        if grid[i][j].getValue() != VAL_MINE:
          grid[i][j].image = incorrectFlag
          
      #Otherwise, reveal if it's a mine
      else:
        if grid[i][j].getValue() == VAL_MINE:
          grid[i][j].image = mineTile



#Flags all remaining mines
def win():
  global currentGameState
  currentGameState = GAME_WIN
  for i in range(NUM_ROWS):
    for j in range(NUM_COLUMNS):
      #Was it flagged?
      
      if grid[i][j].flagged == True:
        #Change it if it was flagged incorrectly
        if grid[i][j].getValue() != VAL_MINE:
          grid[i][j].image = incorrectFlag
          
      #Otherwise, flag if it's a mine
      else:
        if grid[i][j].getValue() == VAL_MINE:
          grid[i][j].image = flagTile

          

#Centers the grid in the middle of the screen
def calcMargins():
  global MARGIN_WIDTH
  global MARGIN_HEIGHT
  #First, the horizontal margin
  MARGIN_WIDTH = (screenSize[0] - ((TILE_WIDTH + BUTTON_BETWEEN_WIDTH) * NUM_COLUMNS)) / 2
  MARGIN_HEIGHT = (screenSize[1] - ((TILE_HEIGHT + BUTTON_BETWEEN_HEIGHT) * NUM_ROWS)) / 2


#Set our tile dimensions
#setTileDims()
#Center our grid
calcMargins()

#ALL sprites in this group MUST have both onLeftClick and onRightClick defined
spritesGroup = pygame.sprite.Group()
#Populate the grid
for i in range(NUM_ROWS):
  grid.append([])
  for j in range(NUM_COLUMNS):
    newTile = Tile(j, i)
    grid[i].append(newTile)
    spritesGroup.add(newTile)

#Add UI buttons
resetButton = ResetButton(screenSize[0] * 2/5, MARGIN_HEIGHT / 4, screenSize[0] / 5,
                          MARGIN_HEIGHT / 2)
spritesGroup.add(resetButton)
#spritesGroup.add(highlightTile)
texts = [] #Array of text objects
textCoords = [] #Coordinates of the text - texts[0] gets drawn at textCoords[0], etc.

#Creates a text display connected to a certain button and adds it to the text list.
#Inputs:
#button: A Button object we'll center ourselves on.
#message: What the text will say.
#color: The text color.
def addButtonText(button, message, color=black):
  #Make sure to truncate font size to int
  fontSize = int(button.height * 0.8 // 1)
  newFont = pygame.font.SysFont("Calibiri", fontSize, True, False)
  newText = newFont.render(message, True, color)
  texts.append(newText)
  textCoords.append([button.rect.x + (button.width / 2) - (len(message) * fontSize / 5),
      button.rect.y + (button.height / 10)])

#Add UI text
addButtonText(resetButton, "Reset", white)

#Give the highlight tile its own group
highlightGroup = pygame.sprite.Group()
highlightGroup.add(highlightTile)

#Process input
#def processInput():
  #Get all our events
  # for event in pygame.event.get():
   # if event.type == pygame.KEYDOWN:
    

#Wipe the board clean
def resetBoard():
  for i in range(NUM_ROWS):
    for j in range(NUM_COLUMNS):
      grid[i][j].reset()

#Place the mines
def placeMines():
  minesPlaced = 0 #How many mines we've placed so far
  while minesPlaced < NUM_MINES:
    #Generate a random location for the mine
    randRow = random.randrange(0, NUM_ROWS)
    randCol = random.randrange(0, NUM_COLUMNS)
    #Leave some space in the corners
    if randRow < 2 or randRow > NUM_ROWS - 2:
      if randCol < 2 or randCol > NUM_COLUMNS - 2:
        continue
    #Make that tile a mine, if it isn't already
    if grid[randRow][randCol].value != VAL_MINE:
      grid[randRow][randCol].value = VAL_MINE
      minesPlaced += 1

placeMines()
      
#Main loop
while not done:
  #Process mouse input
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          done = True
      elif event.type == pygame.MOUSEBUTTONDOWN:
          INPUT_MODE = MOUSE_INPUT
          highlightTile.despawn()
          [mouseX, mouseY] = pygame.mouse.get_pos()
          #Test collision
          for sprite in spritesGroup:
            if sprite.rect.collidepoint(mouseX, mouseY):
              #What type of click was it?
              if event.button == LEFT_CLICK:
                sprite.onLeftClick()
              elif event.button == RIGHT_CLICK:
                sprite.onRightClick()
      #Switch to keyboard mode
      elif event.type == pygame.KEYDOWN:
        highlightTile.move(event.key)

  #Have we won yet?
  if TILES_REVEALED == (NUM_ROWS * NUM_COLUMNS) - NUM_MINES:
    win()

  #Draw the grid
  screen.fill(white)
  spritesGroup.draw(screen)
  #Ensure highlighter is drawn on top of everything
  highlightGroup.draw(screen)
  #Draw all text
  for i in range(len(texts)):
    screen.blit(texts[i], textCoords[i])
  pygame.display.flip()
pygame.quit()
