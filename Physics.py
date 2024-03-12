import math
import phylib;
import sqlite3
import os

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS = phylib.PHYLIB_BALL_RADIUS;
FRAME_INTERVAL = 0.01;

TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;

def compute_acceleration(vel_x, vel_y):
    """Compute the acceleration of a rolling ball given its velocity."""
    speed = math.sqrt(vel_x*vel_x + vel_y*vel_y)
    if speed > phylib.PHYLIB_VEL_EPSILON:
        acc_x = -(vel_x / speed) * phylib.PHYLIB_DRAG
        acc_y = -(vel_y / speed) * phylib.PHYLIB_DRAG
    else:
        acc_x = acc_y = 0.0
    return acc_x, acc_y


HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";

FOOTER = """</svg>\n""";

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;


    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number % len(BALL_COLOURS)])

class RollingBall(phylib.phylib_object):
    """
    Python  RollingBall Class.
    """

    def __init__(self, number, pos, vel, acc):
        """
        Constructor function. Requires ball number, position, vel and acc (x,y) as
        arguments.
        """

         # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = RollingBall;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number % len(BALL_COLOURS)])

class Hole(phylib.phylib_object):
    """
    Python Hole Class.
    """

    def __init__(self, pos):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE, 
                                       pos );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = Hole;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, phylib.PHYLIB_HOLE_RADIUS)


class HCushion(phylib.phylib_object):
    """
    Python Hole Class.
    """

    def __init__(self, y):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HCUSHION, 
                                       y);
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = HCushion;

    def svg(self):
            y = -25 if self.obj.hcushion.y == 0 else 2700
            return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % y

class VCushion(phylib.phylib_object):
    """
    Python Hole Class.
    """

    def __init__(self, x):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_VCUSHION, 
                                       x);
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = VCushion;

    def svg(self):
        x = -25 if self.obj.vcushion.x == 0 else 1350
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % x

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < phylib.PHYLIB_MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    def svg(self):
        svg_str = HEADER
        for obj in self:
            if obj:  # Check if the object is not None
                svg_str += obj.svg()  # Call svg() on the object
        svg_str += FOOTER
        return svg_str
    
    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                                        Coordinate(0,0),
                                        Coordinate(0,0),
                                        Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
        
                # add ball to table
                new += new_ball;
        
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                                        Coordinate( ball.obj.still_ball.pos.x,
                                                ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
        
        # return table
        return new;

    def cueBall(self):
        for obj in self:
            if isinstance(obj, StillBall) and obj.obj.still_ball.number == 0:
                return obj
            print(obj)
        return None

class Database():

    def __init__ ( self, reset=False ):

        print("Initizlizing Database")

        if reset:
            # If reset is True, delete the existing database file if it exists
            if os.path.exists("phylib.db"):
                os.remove("phylib.db")
            
        # Establish a connection to the database
        self.conn = sqlite3.connect("phylib.db")
        self.createDB()

    def createDB( self ):
        # Creating the tables if they don't exist
        cursor = self.conn.cursor()

        # Ball Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Ball (
                            BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                            BALLNO INTEGER NOT NULL,
                            XPOS FLOAT NOT NULL,
                            YPOS FLOAT NOT NULL,
                            XVEL FLOAT,
                            YVEL FLOAT
                        )''')

        # Table Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS TTable (
                            TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                            TIME FLOAT NOT NULL
                        )''')

        # BallTable Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS BallTable (
                            BALLID INTEGER NOT NULL,
                            TABLEID INTEGER NOT NULL,
                            FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)
                        )''')

        # Shot Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Shot (
                            SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                            PLAYERID INTEGER NOT NULL,
                            GAMEID INTEGER NOT NULL,
                            FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
                        )''')

        # TableShot Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS TableShot (
                            TABLEID INTEGER NOT NULL,
                            SHOTID INTEGER NOT NULL,
                            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                            FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
                        )''')

        # Game Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Game (
                            GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                            GAMENAME VARCHAR(64) NOT NULL
                        )''')

        # Player Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Player (
                            PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                            GAMEID INTEGER NOT NULL,
                            PLAYERNAME VARCHAR(64) NOT NULL,
                            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
                        )''')

        self.conn.commit()  
        cursor.close()

    def readTable( self, tableID ):
        cursor = self.conn.cursor()

        cursor.execute('''SELECT TIME FROM TTable WHERE TABLEID = ?''', (tableID + 1,))
        time_data = cursor.fetchone()

        if not time_data:  # If no table is found, return None
            cursor.close()
            return None

        cursor.execute('''SELECT * FROM Ball
                    INNER JOIN BallTable ON Ball.BALLID = BallTable.BALLID
                    WHERE BallTable.TABLEID = ?''', (tableID + 1,))
        balls_data = cursor.fetchall()

       
        table = Table()
        table.time = time_data[0]

        for ball_data in balls_data:
            ball_number = ball_data[1]
            xpos = ball_data[2]
            ypos = ball_data[3]
            xvel = ball_data[4]
            yvel = ball_data[5]

            pos = Coordinate(xpos, ypos)
            if xvel is None or yvel is None: 
                ball = StillBall(ball_number, pos)
            else:
                vel = Coordinate(xvel, yvel)
                acc_x, acc_y = compute_acceleration(xvel, yvel)
                acc = Coordinate(acc_x, acc_y)
                ball = RollingBall(ball_number, pos, vel, acc)
            table += ball
        table.time = time_data[0]

        self.conn.commit()  
        cursor.close()

        return table

    def writeTable( self, table ):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO TTable (TIME) VALUES (?)''', (table.time,))
        table_id = cursor.lastrowid 

        for ball in table:
            if isinstance(ball, StillBall):
                cursor.execute('''INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) 
                                VALUES (?, ?, ?, ?, ?)''', (ball.obj.still_ball.number, ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y, None, None))
                ball_id = cursor.lastrowid  

                cursor.execute('''INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)''', (ball_id, table_id))
            
            elif isinstance(ball, RollingBall):
                cursor.execute('''INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) 
                                VALUES (?, ?, ?, ?, ?)''', (ball.obj.rolling_ball.number, ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y, ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y))
                ball_id = cursor.lastrowid 

                cursor.execute('''INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)''', (ball_id, table_id))
                
        self.conn.commit()  
        cursor.close()

        return table_id - 1
    
    def close( self ):
        self.conn.commit()
        self.conn.close()

    def getGame(self, gameID ):
        cursor = self.conn.cursor()  

        # Retrieve game details using a JOIN query
        cursor.execute('''SELECT G.GAMENAME, P1.PLAYERNAME, P2.PLAYERNAME
                          FROM Game G
                          JOIN Player P1 ON G.GAMEID = P1.GAMEID
                          JOIN Player P2 ON G.GAMEID = P2.GAMEID AND P1.PLAYERID < P2.PLAYERID
                          WHERE G.GAMEID = ?''', (gameID + 1,))
        game_data = cursor.fetchone()

        self.conn.commit()  
        cursor.close()

        if game_data:
            return gameID, game_data[0], game_data[1], game_data[2]
        else:
            return None
    
    def setGame(self, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()

        cursor.execute('''INSERT INTO Game (GAMENAME) VALUES (?)''', (gameName,))
        gameID = cursor.lastrowid

        # Insert players in order ensuring player1Name gets the lower PLAYERID
        cursor.execute('''INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)''', (gameID, player1Name))
        cursor.execute('''INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)''', (gameID, player2Name))

        self.conn.commit()  
        cursor.close()

        return gameID - 1  
    
    def newShot(self, gameName, playerName):
        cursor = self.conn.cursor()

        cursor.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?", (playerName,))
        player_id_result = cursor.fetchone()

        if player_id_result is None:
            raise ValueError(f"No player found with name: {playerName}")

        player_id = player_id_result[0]

        cursor.execute('''INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, 
                    (SELECT GAMEID FROM Game WHERE GAMENAME = ?))''', (player_id, gameName))
        shot_id = cursor.lastrowid
        
        self.conn.commit()  
        cursor.close()

        return shot_id - 1

    def recordTableShot(self, table_id, shot_id):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)''', (table_id + 1, shot_id + 1))
        
        self.conn.commit()  
        cursor.close()


class Game:

    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.db = Database()

        if gameID is not None and (gameName is not None or player1Name is not None or player2Name is not None):
            raise TypeError("Invalid combination of arguments provided to the constructor")

        if gameID is not None:
            gameData = self.db.getGame(gameID)

            if gameData is None:
                raise ValueError(f"No game found with gameID: {gameID}")
            
            self.gameID, self.gameName, self.player1Name, self.player2Name = gameData
        elif gameName is not None and player1Name is not None and player2Name is not None:
            self.gameID = self.db.setGame(gameName, player1Name, player2Name) # Adjust to use setGame result
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
        else:
            raise TypeError("Invalid combination of arguments provided to the constructor")


    def shoot(self, gameName, playerName, table, xvel, yvel):
        
        shot_id = self.db.newShot(gameName, playerName)
        
        cue_ball = table.cueBall()
        if cue_ball is None:
            raise ValueError("Cue ball not found on the table.")

        # Store current position of the cue ball
        xpos, ypos = cue_ball.obj.still_ball.pos.x, cue_ball.obj.still_ball.pos.y

        # Set cue ball as a rolling ball
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        cue_ball.obj.rolling_ball.number = 0
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel

        # Recalculate acceleration based on the given velocities (implement compute_acceleration accordingly)
        acc_x, acc_y = compute_acceleration(xvel, yvel)
        cue_ball.obj.rolling_ball.acc.x = acc_x
        cue_ball.obj.rolling_ball.acc.y = acc_y

        # Loop through segments until no more segments are returned
        while True:
            start_time = table.time
            segment_table = table.segment()

            if segment_table is None:
                break 

            end_time = segment_table.time
            segment_length_seconds = end_time - start_time
            steps = int(segment_length_seconds / FRAME_INTERVAL)

            frame = 0
            while frame < steps:
                elapsed_time = frame * FRAME_INTERVAL
                new_table = table.roll(elapsed_time)
                new_table.time = start_time + elapsed_time

                table_id = self.db.writeTable(new_table)
                self.db.recordTableShot(table_id, shot_id)
                frame+=1
            table = segment_table

        return shot_id

