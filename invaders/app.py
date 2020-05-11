"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There
is no need for any additional classes in this module.  If you need more classes, 99% of
the time they belong in either the wave module or the models module. If you are unsure
about where a new class should go, post a question on Piazza.

# YOUR NAME(S) AND NETID(S) HERE: ABBY PHAM (vp237)
                                  SOYEE PARK (sp798)
# DATE COMPLETED HERE: MAY 6, 2019
"""
from consts import *
from game2d import *
from wave import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application

    This class extends GameApp and implements the various methods necessary for processing
    the player inputs and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Play object

        Method draw displays the Play object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is to manage the game state: which is when the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]

    STATE SPECIFIC INVARIANTS:
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.

    For a complete description of how the states work, see the specification for the
    method update.

    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be
    documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _lastkeys: the number of keys pressed last frame
                  [int >= 0]
        _text_1: the currently active message
                 [GLabel, or None if there is no message to display]
        _text_2: the currently active message
                 [GLabel, or None if there is no message to display]
        _background: the background of the game
                     [GRectangle (it is inherited from GObject) or GImage]
        _music: the background music of the game
                [the background song is "Shark - Andrenaline", taken from NewGrounds library]
    """

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message
        (in attribute _text) saying that the user should press to play a game.
        """
        self._state = STATE_INACTIVE
        self._text_1 = GLabel(text = 'WELCOME TO SPACE INVADERS!\n' + 'Press "S" to Play\n' +
        'Press "M" to Mute Sounds\n' + 'Press "O" to Turn On Sounds', font_size = 40, font_name = 'RetroGame',
        fillcolor = None, linecolor = 'white', x = GAME_WIDTH/2.0 , y = GAME_HEIGHT/2.0)
        self._text_2 = None
        self._wave = None
        self._lastkeys = 0
        self._background = None
        self._music = Sound('bc.wav')

    def update(self,dt):
        """
        Animates a single frame in the game.

        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.

        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, and STATE_COMPLETE.  Each one of these
        does its own thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).

        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key ('s'). This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.

        STATE_COMPLETE: The wave is over, and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        #Parts of the method are based on Walker White's method _determineState
        numkeys = self.input.key_count
        change = self._lastkeys == 0 and numkeys > 0
        self._music.play()
        self._music.volume = 1
        self.state_inactive()
        self.state_newwave()
        self.state_active(dt)
        self.state_paused()
        self.state_complete()
        if (change and self.input.is_key_down('m')):
            self._music.volume = 0
            if (self._wave != None):
                self._wave.getShootingSound().volume = 0
                self._wave.getAlienSound().volume = 0
                self._wave.getAlienDieSound().volume = 0
                self._wave.getShipDieSound().volume = 0
        if (change and self.input.is_key_down('o')):
            self._music.volume = 1
            if (self._wave != None):
                self._wave.getShootingSound().volume = 1
                self._wave.getAlienSound().volume = 1
                self._wave.getAlienDieSound().volume = 1
                self._wave.getShipDieSound().volume = 1
        self._lastkeys = numkeys

    def state_inactive(self):
        """
        Update the state when it is in STATE_INACTIVE.

        This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).
        """
        if (self._state == STATE_INACTIVE):
            numkeys = self.input.key_count
            change = self._lastkeys == 0 and numkeys > 0
            self._background = GImage(x = GAME_WIDTH/2, y = GAME_HEIGHT/2,
            width = GAME_WIDTH, height = GAME_HEIGHT, source = 'Space.jpg')
            if (change and self.input.is_key_down('s')):
                self._state = STATE_NEWWAVE
                self._text_1 = None
                self._text_2 = None

    def state_newwave(self):
        """
        Update the state when it is in STATE_NEWWAVE

        This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key ('S'). This state only lasts one animation
        frame before switching to STATE_ACTIVE.
        """
        if (self._state == STATE_NEWWAVE):
            self._wave = Wave()
            self._state = STATE_ACTIVE
            self._text_1 = None
            self._text_2 = None

    def state_active(self, dt):
        """
        Update the state when it is in STATE_ACTIVE

        This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.
        """
        if (self._state == STATE_ACTIVE):
            self._background = GRectangle(x = GAME_WIDTH/2, y = GAME_HEIGHT/2,
            width = GAME_WIDTH, height = GAME_HEIGHT, fillcolor = 'black')
            self._text_1 = GLabel(text = 'Score: ' +
            str(self._wave.getTotalScore()), font_size = 20, font_name = 'RetroGame',
            linecolor = 'white', x = 100 , y = 680)
            self._text_2 = GLabel(text = 'Lives: ' + str(self._wave.getLives()),
            font_size = 20, font_name = 'RetroGame', linecolor = 'white', x = 700 , y = 680)
            self._wave.update(dt, self.input)
            if ((self._wave.check_ship()) and (self._wave.getLives() != 0)):
                self._state = STATE_PAUSED
            elif (((self._wave.check_ship()) and (self._wave.getLives() == 0)) or
            (self._wave.check_aliens()) or (self._wave.getLives() == 0)):
                self._state = STATE_COMPLETE

    def state_paused(self):
        """
        Update the state when it is in STATE_PAUSED

        Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen. This state also restores the ship after it was destroyed. The
        application switches to this state if the state was STATE_PAUSED in the
        previous frame, and the player pressed a key ('C'). This state only lasts one animation
        frame before switching to STATE_ACTIVE.
        """
        if (self._state == STATE_PAUSED):
            self._text_1 = GLabel(text = 'Press "C" to Continue', font_size = 40,
            font_name = 'RetroGame', linecolor = 'white', x = GAME_WIDTH/2.0 , y = GAME_HEIGHT/2.0)
            self._background = GImage(x = GAME_WIDTH/2, y = GAME_HEIGHT/2, width = GAME_WIDTH,
            height = GAME_HEIGHT, source = 'Space.jpg')
            numkeys = self.input.key_count
            change = self._lastkeys == 0 and numkeys > 0
            if (change and self.input.is_key_down('c')):
                self._state = STATE_ACTIVE
                self._wave.makeship()
                self._music.volume = 0

    def state_complete(self):
        """
        Update the state when it is in STATE_COMPLETE

        The wave is over, and is either won or lost.
        """
        #Images are taken from the following sources:
        #https://pngtree.com/freebackground/flame-background-cosmic-explosion_246611.html
        #https://www.shutterstock.com/es/video/clip-18681329-space-background-camera-flying-through-blue-magenta
        #https://www.tunefind.com/movie/guardians-of-the-galaxy-2014
        if (self._state == STATE_COMPLETE):
            if ((self._wave.check_ship() and (self._wave.getLives() == 0)) or
            (self._wave.getLives() == 0)):
                self._background = GImage(x = GAME_WIDTH/2, y = GAME_HEIGHT/2,
                width = GAME_WIDTH, height = GAME_HEIGHT, source = 'Doomed.jpg')
                self._text_1 = GLabel(text = 'THE EARTH IS DOOMED!\n' + 'Score: '
                + str(self._wave.getTotalScore()), font_size = 40, font_name = 'RetroGame',
                linecolor = 'white', x = GAME_WIDTH/2.0 , y = GAME_HEIGHT/2.0)
            if (self._wave.check_aliens()):
                self._background = GImage(x = GAME_WIDTH/2, y = GAME_HEIGHT/2,
                width = GAME_WIDTH, height = GAME_HEIGHT, source = 'Guardians of the Galaxy.jpeg')
                self._text_1 = GLabel(text = 'CONGRATULATIONS EARTH PROTECTORS!\n' + 'Score: ' +
                str(self._wave.getTotalScore()), font_size = 40, font_name = 'RetroGame',
                linecolor = 'white', x = GAME_WIDTH/2.0 , y = GAME_HEIGHT/2.0)

    def draw(self):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        if (self._state == STATE_INACTIVE):
            self._background.draw(self.view)
            self._text_1.draw(self.view)
        elif (self._state == STATE_PAUSED):
            self._background.draw(self.view)
            self._text_1.draw(self.view)
        elif (self._state == STATE_COMPLETE):
            self._background.draw(self.view)
            self._text_1.draw(self.view)
        elif(self._state == STATE_ACTIVE):
            self._background.draw(self.view)
            self._wave.draw(self.view)
            self._text_1.draw(self.view)
            self._text_2.draw(self.view)
        else:
            self._wave.draw(self.view)


    # HELPER METHODS FOR THE STATES GO HERE
