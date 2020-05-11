"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

# YOUR NAME(S) AND NETID(S) HERE: ABBY PHAM (vp237)
                                  SOYEE PARK (sp798)
# DATE COMPLETED HERE: MAY 6, 2019
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    INSTANCE ATTRIBUTES:
        _changemove: the direction the aliens are moving [0 if moving right, 1 if moving left]
        _steps: the number of steps the aliens move until they fire [int >= 0]
        _aliensdie: the number of aliens shot by the bolts [int >= 0]
        _speed: the alien's speed [float > 0]
        _scoreaccumulator: the score accummulator [number >= 0]
        _shootingsound: the shooting sound from the ship [Sound Class]
        _aliensound: the shooting sound from the aliens [Sound Class]
        _ship_die_sound: the blast sound when the ship is destroyed [Sound Class]
        _alien_die_sound: the blast sound when the aliens are destroyed [Sound Class]
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLives(self):
        """
        Returns: The number of lives left of the player
        """
        return self._lives

    def getTotalScore(self):
        """
        Returns: The total score of the player
        """
        return self._scoreaccumulator

    def getShootingSound(self):
        """
        Returns: The shooting sound from the ship
        """
        return self._shootingsound

    def getAlienSound(self):
        """
        Returns: The shooting sound from the aliens
        """
        return self._aliensound

    def getShipDieSound(self):
        """
        Returns: The blast sound when the ship is destroyed
        """
        return self._ship_die_sound

    def getAlienDieSound(self):
        """
        Returns: The blast sound when the aliens are destroyed
        """
        return self._alien_die_sound


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializes the Wave object with default values from const.py and Sounds folder for its attributes.

        This function calls makeAliens to populate _aliens.
        """
        self._ship = Ship()
        self._aliens = self.makeAliens()
        self._bolts = []
        self._dline = GPath(points = [0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
        linewidth = 2, linecolor = 'white')
        self._lives = SHIP_LIVES
        self._time = 0
        self._changemove = 0
        self._steps = 0
        self._aliensdie = 0
        self._speed = ALIEN_SPEED
        self._scoreaccumulator = 0
        self._shootingsound = Sound('pew1.wav')
        self._aliensound = Sound('pew2.wav')
        self._ship_die_sound = Sound('blast1.wav')
        self._alien_die_sound = Sound('blast2.wav')

    #HELPER METHOD TO MAKE ALIENS
    def makeAliens(self):
        """
        Creates a 2D list of aliens with ALIEN_ROWS rows and ALIENS_IN_ROW columns.
        The space between each alien and the screen horizontally is ALIEN_H_SEP,
        and the space between each alien vertically is ALIEN_V_SEP
        """
        lst = []
        for i in range(ALIEN_ROWS):
            newlist = []
            if ((i % 6 == 0) or (i % 6 == 1)):
                source = ALIEN_IMAGES[0]
            elif ((i % 6 == 2) or (i % 6 == 3)):
                source = ALIEN_IMAGES[1]
            elif ((i % 6 == 4) or (i % 6 ==5)):
                source = ALIEN_IMAGES[2]
            for j in range(ALIENS_IN_ROW):
                newlist.append(Alien(ALIEN_H_SEP*(1+j)+ALIEN_WIDTH*(0.5+j),
                GAME_HEIGHT-ALIEN_CEILING-ALIEN_HEIGHT/2.0-(ALIEN_HEIGHT+ALIEN_V_SEP)*(ALIEN_ROWS-i-1), source))
            lst.append(newlist)
        return lst

    def makeship(self):
        """
        Creates a Ship object with the appropriate position
        """
        position = GAME_HEIGHT - SHIP_BOTTOM
        ship_position = GAME_HEIGHT - position
        self._ship = Ship()

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    #Parts of this method are based on Walker White's method update
    def update(self, dt, input):
        """
        Animates the ship, aliens, and laser bolts

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        Parameter input: The input from player to control movements of the ship and shoot laser bolts
                         [GInput; it is inherited from GameApp]
        Precondition: must be an instance of GInput
        """
        self.aliens_update(dt)
        self.bolts_update(input)
        self.check_cross_dline()
        self.aliens_die()
        self.ship_update(input)
        self.bolts_aliens()

    def ship_update(self,input):
        """
        Updates the position based on player's input and the state of the ship

        Parameter input: The input from player to control movements of the ship and shoot laser bolts
                         [GInput; it is inherited from GameApp]
        Precondition: must be an instance of GInput
        """
        da = self._ship.getX()
        if (input.is_key_down('left')):
            da = max(da-SHIP_MOVEMENT, SHIP_WIDTH/2.0)
        if (input.is_key_down('right')):
            da = min(da+SHIP_MOVEMENT, GAME_WIDTH-SHIP_WIDTH/2.0)
        self._ship.setX(da)
        self.ship_die()

    def aliens_update(self, dt):
        """
        Updates the movements of the aliens

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._time += dt
        if (self._time > ALIEN_SPEED):
            self._time = 0
            if (self._changemove == 0):
                self.aliens_move_right()
            elif (self._changemove == 1):
                self.aliens_move_left()
            self._steps += 1
        self.aliens_die()

    def aliens_move_right(self):
        """
        Move the aliens to the right. When the rightermost aliens hit the right
        edge of the screen, move the aliens down and change direction
        """
        rightermost = GAME_WIDTH-ALIEN_H_SEP-ALIEN_WIDTH/2.0
        for i in range(ALIEN_ROWS):
            for j in range(ALIENS_IN_ROW):
                alien = self._aliens[i][j]
                if not (alien is None):
                    alien.setX(alien.getX()+ALIEN_H_SEP)
                    if (alien.getX() > rightermost):
                        self._changemove = 1
        for i in range(ALIEN_ROWS):
            for j in range(ALIENS_IN_ROW):
                alien = self._aliens[i][j]
                if not (alien is None):
                    if (self._changemove == 1):
                        alien.setY(alien.getY()-ALIEN_V_SEP)
                        alien.setX(alien.getX()-ALIEN_H_SEP)

    def aliens_move_left(self):
        """
        Move the aliens to the left. When the leftermost aliens hit the left
        edge of the screen, move the aliens down and change direction
        """
        leftermost = ALIEN_H_SEP+ALIEN_WIDTH/2.0
        for i in range(ALIEN_ROWS):
            for j in range(ALIENS_IN_ROW):
                alien = self._aliens[i][j]
                if not (alien is None):
                    alien.setX(alien.getX()-ALIEN_H_SEP)
                    if (alien.getX() < leftermost):
                        self._changemove = 0
        for i in range(ALIEN_ROWS):
            for j in range(ALIENS_IN_ROW):
                alien = self._aliens[i][j]
                if not (alien is None):
                    if (self._changemove == 0):
                        alien.setY(alien.getY()-ALIEN_V_SEP)
                        alien.setX(alien.getX()+ALIEN_H_SEP)

    def bolts_update(self, input):
        """
        Updates the bolts fired by the ship and the aliens

        Parameter input: The input from player to control movements of the ship and shoot laser bolts
                         [GInput; it is inherited from GameApp]
        Precondition: must be an instance of GInput
        """
        self.bolts_ship(input)
        self.bolts_aliens()

    #Parts of this method are based on Walker White's method _moveRockets
    def bolts_ship(self, input):
        """
        Creates a laser bolt when the player presses a fire key('up' key) and removes
        the laser bolt when it goes off screen

        Parameter input: The input from player to control movements of the ship and shoot laser bolts
                         [GInput; it is inherited from GameApp]
        Precondition: must be an instance of GInput
        """
        lst = []
        for i in self._bolts:
            if i.isPlayerBolt():
                lst.append(1)
        if (len(lst) == 0):
            if (input.is_key_down('up')):
                self._bolts.append(Bolt(self._ship.getX(), SHIP_BOTTOM+SHIP_HEIGHT/2.0, 'yellow', 1))
                self._shootingsound.play()
        for i in self._bolts:
            da = i.getY()
            if i.isPlayerBolt():
                da += i.getVelocity()
                i.setY(da)
        i = 0
        while i < len(self._bolts):
            if (self._bolts[i].getY()>GAME_HEIGHT+BOLT_HEIGHT/2.0 and self._bolts[i].isPlayerBolt()):
                del self._bolts[i]
            else:
                i += 1

    def bolts_aliens(self):
        """
        Creates a laser bolt and assigns it to a bottomost alien in a random column
        and removes the laser bolt when it goes off screen
        """
        if (self._steps == 0):
            self._random = random.randrange(1, BOLT_RATE+1)
        if (self._steps == self._random):
            lst = []
            for i in range(ALIENS_IN_ROW):
                for j in range(ALIEN_ROWS):
                    if (self._aliens[j][i] != None):
                        lst.append(self._aliens[j][i])
                        self._aliensound.play()
                        break
            rnd = random.randrange(0, len(lst))
            alien = lst[rnd]
            if (len(lst) != 0):
                self._bolts.append(Bolt(alien.getX(), alien.getY(), 'purple', -1))
            self._steps = 0
        for i in self._bolts:
            da = i.getY()
            if not(i.isPlayerBolt()):
                da += i.getVelocity()
                i.setY(da)
        i = 0
        while i < len(self._bolts):
            if (self._bolts[i].getY()+BOLT_HEIGHT/2.0 < 0 and not(self._bolts[i].isPlayerBolt())):
                del self._bolts[i]
            else:
                i += 1

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the ship, aliens, defensive line and bolts

        Parameter view: the game view
        Precondition: must be an instance of GView
        """
        for row in self._aliens:
            for alien in row:
                if not (alien is None):
                    alien.draw(view)
        if not (self._ship is None):
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            if not (bolt is None):
                bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
    def aliens_die(self):
        """
        Removes the aliens if they are hit by the bolts
        """
        for bolt in self._bolts:
            if (bolt.isPlayerBolt()):
                for i in range(ALIEN_ROWS):
                    for j in range(ALIENS_IN_ROW):
                        if (self._aliens[i][j] != None):
                            if (self._aliens[i][j].collides(bolt)):
                                self._alien_die_sound.play()
                                self._scoreaccumulator += self._aliens[i][j].getScore()*(i+1)
                                print(self._speed)
                                ALIEN_SPEED = self._speed * 0.9
                                self._speed = ALIEN_SPEED
                                self._aliens[i][j] = None
                                self._bolts.remove(bolt)
                                self._aliensdie += 1

    def ship_die(self):
        """
        Removes the ship if it is hit by a bolt
        """
        for bolt in self._bolts:
            if ((not(bolt.isPlayerBolt())) and (self._ship != None)):
                if (self._ship.collides(bolt)):
                    self._ship_die_sound.play()
                    self._ship = None
                    self._bolts.remove(bolt)
                    self._lives -= 1

    def check_ship(self):
        """
        Returns: True if the ship is destroyed, False otherwise
        """
        if (self._ship is None):
            return True
        return False

    def check_aliens(self):
        """
        Returns: True if all the aliens are destroyed, False otherwise
        """
        if (self._aliensdie == ALIENS_IN_ROW*ALIEN_ROWS):
            return True
        return False

    def check_cross_dline(self):
        """
        Returns: True if the bottommost aliens cross the defense line, False otherwise
        """
        for i in range(ALIEN_ROWS):
            for j in range(ALIENS_IN_ROW):
                if ((self._aliens[i][j] != None) and (self._aliens[i][j].getY()-ALIEN_HEIGHT/2.0 <= DEFENSE_LINE)):
                    self._lives = 0
