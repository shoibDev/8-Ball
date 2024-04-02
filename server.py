from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi  # For parsing POST request data
import json
import sys  # For accessing command line arguments
import os
import math
import Physics
import random
from urllib.parse import urlparse, parse_qs

# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse;

def nudge():
    return random.uniform( -1.5, 1.5 );

def compute_acceleration(vel_x, vel_y):
    """Compute the acceleration of a rolling ball given its velocity."""
    speed = math.sqrt(vel_x*vel_x + vel_y*vel_y)
    if speed > Physics.phylib.PHYLIB_VEL_EPSILON:
        acc_x = -(vel_x / speed) * Physics.phylib.PHYLIB_DRAG
        acc_y = -(vel_y / speed) * Physics.phylib.PHYLIB_DRAG
    else:
        acc_x = acc_y = 0.0
    return acc_x, acc_y

def write_table_to_svg(table, file_index):
    svg_content = table.svg()
    file_name = f"table-{file_index}.svg"
    with open(file_name, 'w') as file:
        file.write(svg_content)

class RequestHandler(BaseHTTPRequestHandler):

    game = None;
    tableId = 0;
    initalTable = None;

    db = Physics.Database();
    cur = db.conn.cursor();

    def do_GET(self):
        parsed  = urlparse( self.path )

        if parsed.path in [ '/8-ball.html' ]:
            fp = open( '.'+self.path );
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
        
        elif parsed.path in [ '/setup.html' ]:
            fp = open( '.'+self.path );
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", str(len( content )) );
            self.end_headers();
        
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
    

        elif parsed.path == '/script.js':
            fp = open( '.'+self.path);
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "application/javascript" );
            self.send_header( "Content-length", str(len( content )) );
            self.end_headers();
        
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
        
        elif parsed.path == '/setup.js':
            fp = open( '.'+self.path);
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "application/javascript" );
            self.send_header( "Content-length", str(len( content )) );
            self.end_headers();
        
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
        elif parsed.path == '/style.css':
            fp = open( '.'+self.path);
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/css" );
            self.send_header( "Content-length", str(len( content )) );
            self.end_headers();
        
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();


        else:
            # Path does not match any handled routes, send 404 response
            self.send_error(404, "File Not Found: " + self.path)
            
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed = urlparse(self.path)
        
        if parsed.path == '/initialize':
            form_data = parse_qs(post_data.decode('utf-8'))

            player1Name = form_data.get('player1Name', [None])[0]
            player2Name = form_data.get('player2Name', [None])[0]
            gameName = form_data.get('gameName', [None])[0]

            table = Physics.Table();
        
            ball_diameter = Physics.BALL_DIAMETER + 4.0  # Including a small gap between balls
            triangle_height = math.sqrt(3) / 2 * ball_diameter

            for row in range(3, 6):
                for col in range(row):
                    # Calculate the position for each ball in this row
                    x = (Physics.TABLE_WIDTH / 2.0) - ((row - 1) * ball_diameter / 2) + (col * ball_diameter) + nudge()
                    y = (Physics.TABLE_WIDTH / 2.0) - (triangle_height * (row - 1)) + nudge()
                    # Adjust the ball number accordingly
                    ball_number = sum(range(1, row)) + col + 1
                    pos = Physics.Coordinate(x, y)
                    sb = Physics.StillBall(ball_number, pos)
                    table += sb

            
            # 1 ball
            pos = Physics.Coordinate( 
                            Physics.TABLE_WIDTH / 2.0,
                            Physics.TABLE_WIDTH / 2.0,
                            );

            sb = Physics.StillBall( 1, pos );
            table += sb;

            # 2 ball
            pos = Physics.Coordinate(
                            Physics.TABLE_WIDTH/2.0 - (Physics.BALL_DIAMETER+4.0)/2.0 +
                            nudge(),
                            Physics.TABLE_WIDTH/2.0 - 
                            math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0) +
                            nudge()
                            );
            sb = Physics.StillBall( 2, pos );
            table += sb;

            # 3 ball
            pos = Physics.Coordinate(
                            Physics.TABLE_WIDTH/2.0 + (Physics.BALL_DIAMETER+4.0)/2.0 +
                            nudge(),
                            Physics.TABLE_WIDTH/2.0 - 
                            math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0) +
                            nudge()
                            );
            sb = Physics.StillBall( 3, pos );
            table += sb;

            # cue ball also still
            pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                    Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 );
            sb  = Physics.StillBall( 0, pos );  

            table += sb;

            RequestHandler.initalTable = table;
            RequestHandler.game = Physics.Game( gameName=gameName, player1Name=player1Name, player2Name=player2Name );
            
            svg_content = table.svg()
            response_data = {
                "message": f"Game '{gameName}' initialized for players: {player1Name} and {player2Name}.",
                "svg": svg_content
            }
            # Respond to indicate success
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        elif parsed.path == '/shot':
            switchPlayer = 1  # Assume Always swithcing:
            
            form_data = parse_qs(post_data.decode('utf-8'))

            gameName = form_data.get('gameName', [None])[0]
            playerName = form_data.get('playerName', [None])[0]
            x = float(form_data.get('x', [0])[0])
            y = float(form_data.get('y', [0])[0])

            if RequestHandler.tableId == 0 and RequestHandler.db.readTable(RequestHandler.tableId) is None:
                shotId, svg_contents, balls_sunk = RequestHandler.game.shoot(gameName, playerName, RequestHandler.initalTable, x, y)
            else:
                table = RequestHandler.db.readTable(RequestHandler.tableId)
                shotId, svg_contents, balls_sunk = RequestHandler.game.shoot(gameName, playerName, table, x, y)
            
            RequestHandler.tableId = RequestHandler.db.getTableIdByShotId(shotId)
            table = RequestHandler.db.readTable(RequestHandler.tableId)

            if table.cueBall() is None: 
                pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                    Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 );
                sb  = Physics.StillBall( 0, pos );  
                table += sb;

                RequestHandler.db.writeTable(table)
                RequestHandler.db.recordTableShot(RequestHandler.tableId + 1, shotId)
                RequestHandler.tableId = RequestHandler.tableId + 1
                svg_contents.append(table.svg())

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
          
            response = json.dumps({
                'svgContents': svg_contents,
                'switchPlayer': switchPlayer,  # Add this line to include the switch information
                'balls_sunk': balls_sunk, 
            })

            self.wfile.write(response.encode('utf-8'))
            
        else:
            self.send_error(404, "File Not Found: " + self.path)
            
if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1])), RequestHandler )
    httpd.serve_forever()

