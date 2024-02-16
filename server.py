from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi  # For parsing POST request data
import sys  # For accessing command line arguments
import os
import math
import Physics

# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse;

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
    def do_GET(self):
        # parse the URL to get the path and form data
        parsed  = urlparse( self.path )
         # check if the web-pages matches the list
        if parsed.path in [ '/shoot.html' ]:

            # retreive the HTML file
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

               # Check if the path matches the pattern for SVG files
        elif parsed.path.startswith("/table-") and parsed.path.endswith(".svg"):
            file_path = '.' + parsed.path
            if os.path.isfile(file_path):
                # File exists, serve the SVG file
                with open(file_path, 'rb') as fp:
                    content = fp.read()

                # Generate the headers
                self.send_response(200)
                self.send_header("Content-type", "image/svg+xml")
                self.send_header("Content-length", str(len(content)))
                self.end_headers()

                # Send the content to the browser
                self.wfile.write(content)

            else:
                # SVG file not found, send 404 response
                self.send_error(404, "File Not Found: " + self.path)

        else:
            # Path does not match any handled routes, send 404 response
            self.send_error(404, "File Not Found: " + self.path)
    
    def do_POST(self):

        parsed  = urlparse( self.path )
        
        if parsed.path in  ['/display.html']:

            # get data send as Multipart FormData (MIME format)
            form = cgi.FieldStorage( fp=self.rfile,
                                        headers=self.headers,
                                        environ = { 'REQUEST_METHOD': 'POST',
                                                    'CONTENT_TYPE': 
                                                    self.headers['Content-Type'],
                                                } 
                                    )
                        
            # Extracting form values and converting to appropriate types

            sb_number_str = form.getvalue('sb_number')
            rb_number_str = form.getvalue('rb_number')

            sb_number = max(0, min(255, int(sb_number_str)))
            rb_number = max(0, min(255, int(rb_number_str)))

            #sb_number = form.getvalue('sb_number')
            sb_x = float(form.getvalue('sb_x'))
            sb_y = float(form.getvalue('sb_y'))

            #rb_number = form.getvalue('rb_number') 
            rb_x = float(form.getvalue('rb_x'))
            rb_y = float(form.getvalue('rb_y'))
            rb_dx = float(form.getvalue('rb_dx', 0.0))
            rb_dy = float(form.getvalue('rb_dy', 0.0)) 

            # Compute acceleration based on velocity
            acc_x, acc_y = compute_acceleration(rb_dx, rb_dy)

            # Delete old SVG files
            for file in os.listdir('.'):
                if file.endswith('.svg') and file.startswith('table-'):
                    file_path = os.path.join('.', file)
                    os.remove(file_path)

            # Initialize the table
            table = Physics.Table()

            # Create and add Still Ball
            pos_sb = Physics.Coordinate(sb_x, sb_y)
            sb = Physics.StillBall(number=sb_number, pos=pos_sb)
            table.add_object(sb)

            # Create and add Rolling Ball with the computed acceleration
            pos_rb = Physics.Coordinate(rb_x, rb_y)
            vel_rb = Physics.Coordinate(rb_dx, rb_dy)
            acc_rb = Physics.Coordinate(acc_x, acc_y)
            rb = Physics.RollingBall(number=rb_number, pos=pos_rb, vel=vel_rb, acc=acc_rb)
            table.add_object(rb)

            # Write initial table state to SVG
            file_index = 0;
            write_table_to_svg(table, file_index)
            file_index += 1

            while True:
                new_table = table.segment()
                if not new_table:  # Break the loop if no new table state is generated
                    break

                table = new_table  # Update the table reference to the new state

                write_table_to_svg(table, file_index)  # Write the new table state to SVG
                file_index += 1  # Increment the file index for the next SVG file

            # Generate and send the display HTML
            self.generate_and_send_response(acc_x, acc_y, sb, rb)

    def generate_and_send_response(self, acc_x, acc_y, sb, rb):
        # Start HTML content
        html_content = """
        <!DOCTYPE html>
            <html>
                <head>
                    <title>Pool Game Segments</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        img {{ width: 100%; max-width: 600px; margin-bottom: 20px; }}
                        .back-link {{ margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <h1>Segment Results</h1>
                    <p>Acceleration computed: acc_x = {:.2f}, acc_y = {:.2f}</p>
                    <h2>Initial Conditions</h2>
                    <ul>
                        <li>Still Ball Position: (x: {:.2f}, y: {:.2f}), Number: {}</li>
                        <li>Rolling Ball Position: (x: {:.2f}, y: {:.2f}), Velocity: (dx: {:.2f}, dy: {:.2f}), Number: {}</li>
                    </ul>
                    """.format(acc_x, acc_y, sb.obj.still_ball.pos.x, sb.obj.still_ball.pos.y, sb.obj.still_ball.number, rb.obj.rolling_ball.pos.x, rb.obj.rolling_ball.pos.y, rb.obj.rolling_ball.vel.x, rb.obj.rolling_ball.vel.y, rb.obj.rolling_ball.number)

        # Embed SVG files as images
        all_files = os.listdir('.')
        svg_files = sorted([file for file in all_files if file.endswith('.svg') and file.startswith('table-')])
        for svg_file in svg_files:
            html_content += f'<img src="{svg_file}">\n'

        html_content += '<p class="back-link"><a href="/shoot.html">Back</a></p>\n'

        html_content += """
                </body>
            </html>
        """

        # Send response headers
        self.send_response(200)  # HTTP status code: OK
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(html_content)))
        self.end_headers()

        # Send the HTML content
        self.wfile.write(bytes(html_content, "utf-8"))
            
if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1])), RequestHandler )
    print( "Server listing in port:  ", int(sys.argv[1]) )
    httpd.serve_forever()

